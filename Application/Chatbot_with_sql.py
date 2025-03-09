import os
import re
import textwrap
import logging
import sqlite3
from datetime import datetime

# Rich for console Markdown formatting
from rich.console import Console
from rich.markdown import Markdown

import warnings
warnings.filterwarnings("ignore")
# --------------------------------------------------------------------------
# 1. LangChain & Related Imports
# --------------------------------------------------------------------------
from langchain_huggingface import HuggingFaceEmbeddings  # Updated for huggingface
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.chains import create_retrieval_chain, create_history_aware_retriever
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_chroma import Chroma
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory


# --------------------------------------------------------------------------
# 2. Database Setup (user_id as INTEGER)
# --------------------------------------------------------------------------
if not os.path.exists("instance"):
    os.makedirs("instance")

DB_PATH = os.path.join("instance", "app.db")

def initialize_database():
    """
    Creates a table with user_id as INTEGER, 
    plus query, response, and created_at for timestamps.
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS chat_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            query TEXT,
            response TEXT,
            created_at TEXT
        )
    ''')
    conn.commit()
    conn.close()

initialize_database()

def save_chat_turn_to_db(user_id: int, query: str, response: str):
    """
    Saves a single turn (user query + AI response) in the database.
    user_id is stored as an integer now.
    """
    created_at = datetime.now().strftime("%I:%M %p")  # e.g., "10:30 PM"
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO chat_history (user_id, query, response, created_at) VALUES (?, ?, ?, ?)",
        (user_id, query, response, created_at)
    )
    conn.commit()
    conn.close()

def load_chat_history_from_db(user_id: int) -> ChatMessageHistory:
    """
    Retrieves chat history for a given integer user_id and constructs
    a ChatMessageHistory object from it.
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT query, response FROM chat_history WHERE user_id = ? ORDER BY id", (user_id,))
    rows = cursor.fetchall()
    conn.close()

    history = ChatMessageHistory()
    for (query, response) in rows:
        history.add_user_message(query)
        history.add_ai_message(response)

    return history

def delete_user_history(user_id: int):
    """
    Completely removes all chat history for a specific integer user_id.
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM chat_history WHERE user_id = ?", (user_id,))
    conn.commit()
    conn.close()

# --------------------------------------------------------------------------
# 3. Embeddings & Model Configuration
# --------------------------------------------------------------------------
# HuggingFace embeddings to avoid deprecation
huggingface_embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)

# If you're still using Google Generative AI for the chat model:
os.environ["GOOGLE_API_KEY"] = "YOUR_GOOGLE_API_KEY"
chat_model = ChatGoogleGenerativeAI(
    model="gemini-1.5-flash",
    convert_system_message_to_human=False
)

# --------------------------------------------------------------------------
# 4. Load & Process Documents
# --------------------------------------------------------------------------
pdf_files = [
    r"C:\Users\HP\OneDrive\Desktop\python files\slides\MLP Week 4 Slides.pdf",
    r"C:\Users\HP\OneDrive\Desktop\python files\slides\MLP Week 6 Slides.pdf"
]
all_docs = []
for pdf_path in pdf_files:
    loader = PyPDFLoader(pdf_path)
    pdf_pages = loader.load()
    all_docs.extend(pdf_pages)

text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
splits = text_splitter.split_documents(all_docs)

vector_store = Chroma.from_documents(splits, embedding=huggingface_embeddings)
retriever = vector_store.as_retriever(search_type="similarity", search_kwargs={"k": 3})

# --------------------------------------------------------------------------
# 5. Define Prompts
# --------------------------------------------------------------------------
system_prompt = (
    "Your name is Kia meaning (Knowledge Interaction Assistanat), you are a soft spoken lady tutor specialized in Machine Learning Practice (MLP). "
    "You should provide detailed, structured answers with bullet points and examples. "
    "If the question is about general conversation, respond accordingly as a chatbot. "
    "Otherwise, use retrieved MLP-related documents to answer.\n\n"
    "{context}"
)

retriever_prompt = (
    "You have to remember the chat history of users. "
    "You should remember the user prompts and the answers you give. "
    "Make sense of this chat history and answer accordingly when user references context in the chat history."
)

chat_prompt = ChatPromptTemplate.from_messages([
    ("system", system_prompt),
    ("human", "{input}")
])

contextualize_prompt = ChatPromptTemplate.from_messages([
    ("system", retriever_prompt),
    MessagesPlaceholder(variable_name="chat_history"),
    ("human", "{input}")
])

qa_prompt = ChatPromptTemplate.from_messages([
    ("system", system_prompt),
    MessagesPlaceholder("chat_history"),
    ("human", "{input}")
])

# --------------------------------------------------------------------------
# 6. Create Retrieval & QA Chains
# --------------------------------------------------------------------------
qachain = create_stuff_documents_chain(chat_model, chat_prompt)
chat_history_retriever = create_history_aware_retriever(chat_model, retriever, contextualize_prompt)
answer_chain = create_stuff_documents_chain(chat_model, qa_prompt)
RAG_chain = create_retrieval_chain(chat_history_retriever, answer_chain)

# --------------------------------------------------------------------------
# 7. RunnableWithMessageHistory
# --------------------------------------------------------------------------
def _load_history_for_chain(session_id: str) -> BaseChatMessageHistory:
    """
    RunnableWithMessageHistory strictly wants 'session_id'.
    We cast session_id to int, then load from DB using user_id (int).
    """
    return load_chat_history_from_db(int(session_id))

conversation_RAG_Chain = RunnableWithMessageHistory(
    RAG_chain,
    _load_history_for_chain,
    input_messages_keys="input",
    history_messages_key="chat_history",
    output_message_keys="answer",
)

# --------------------------------------------------------------------------
# 8. The get_answer(user_id, user_query) Function
# --------------------------------------------------------------------------
def get_answer(user_id: int, user_query: str) -> str:
    """
    - user_id is an integer in our DB.
    - For the chain, pass session_id=str(user_id) to avoid 'Missing keys' error.
    """
    # Load existing history from DB
    chat_history = load_chat_history_from_db(user_id)

    response_data = conversation_RAG_Chain.invoke(
        {"input": user_query, "chat_history": chat_history.messages},
        config={"configurable": {"session_id": str(user_id)}}  # Must be string
    )
    ai_response = response_data.get("answer", "Sorry, I could not retrieve an answer.")
    save_chat_turn_to_db(user_id, user_query, ai_response)

    return ai_response

# --------------------------------------------------------------------------
# 9. Logging (Optional)
# --------------------------------------------------------------------------
logging.getLogger("langchain_core.callbacks.manager").setLevel(logging.ERROR)

# --------------------------------------------------------------------------
# 10. Example Usage with Rich Markdown
# --------------------------------------------------------------------------
if __name__ == "__main__":
    console = Console()

    # user_id is an integer now
    resp1 = get_answer(123, "Hi, my name is Siddharth, I am an AI Engineer and Data Scientist, studying at IITM. What is your name?")
    console.print(Markdown(resp1))

    resp2 = get_answer(123, "What did I say my name was, what do i do and where do I study?")
    console.print(Markdown(resp2))

    resp3 = get_answer(123, "What is SGDRegressor, and how do I use it?")
    console.print(Markdown(resp3))

    # If you want to delete all history for user_id=123:
    # delete_user_history(123)
    # resp3 = get_answer(123, "What is my name, where do i study and What do i do?")
    # console.print(Markdown(resp3))
