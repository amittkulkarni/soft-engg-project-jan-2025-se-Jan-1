import re
import os
import textwrap
import logging
import sqlite3
import warnings
warnings.filterwarnings('ignore')
from datetime import datetime
from langchain.schema import Document
from IPython.display import display
from IPython.display import Markdown
from rich.console import Console
from rich.markdown import Markdown
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain import hub
from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_chroma import Chroma
from langchain_community.document_loaders import PyPDFLoader
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.prompts import MessagesPlaceholder
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain.chains import create_history_aware_retriever
from langchain_core.messages import HumanMessage, AIMessage
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_community.embeddings import HuggingFaceEmbeddings    


# -----------------------------------------------------------------------------
# 1. Set up Google API Key environment variable
# -----------------------------------------------------------------------------
os.environ["GOOGLE_API_KEY"] = "YOUR_GOOGLE_API_KEY"

# Instantiate the embeddings model
gemini_embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")

# Instantiate the chat model
model = ChatGoogleGenerativeAI(model="gemini-1.5-flash", convert_system_message_to_human=True)

# -----------------------------------------------------------------------------
# 2. Load and Process Documents
# -----------------------------------------------------------------------------

# Loading Multiple Documents

pdf_files = [r"COMPLETE PATH TO THE DOCUMENT1", r"COMPLETE PATH TO DOCUMENT2"]
docs = [PyPDFLoader(pdf).load() for pdf in pdf_files]

all_docs = [page for doc in docs for page in doc]
# print(f"Loaded {len(all_docs)} pages from {len(pdf_files)} PDFs")


# Split the document into chunks
text_splitter = RecursiveCharacterTextSplitter(chunk_size=2000, chunk_overlap=200)
splits = text_splitter.split_documents(all_docs)

# Create vector store
vector_store = Chroma.from_documents(documents=splits, embedding=gemini_embeddings)
retriever = vector_store.as_retriever(search_type="similarity", search_kwargs={"k": 5})

# -----------------------------------------------------------------------------
# 3. Define System and Chat Prompts
# -----------------------------------------------------------------------------
system_prompt = (
    "You are an AI assistant specialized in Machine Learning Practice (MLP). "
    "You should provide detailed, structured answers with bullet points and examples. "
    "If the question is about general conversation, respond accordingly as a chatbot. "
    "Otherwise, use retrieved MLP-related documents to answer.\n\n"
    "{context}"
)

retriever_prompt = (
    "You have to remember the chat history of users."
    "You should remember the user prompts and the answers you give."
    "Make sense of this chat history and answer accordingly when user references context in the chat history."
)

chat_prompt = ChatPromptTemplate.from_messages([("system", system_prompt), ("human", "{input}")])

contextualize_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", retriever_prompt),
        MessagesPlaceholder(variable_name="chat_history"),
        ("human", "{input}"),
    ]
)

qa_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", system_prompt),
        MessagesPlaceholder("chat_history"),
        ("human", "{input}")
    ]
)

# -----------------------------------------------------------------------------
# 4. Create Chains
# -----------------------------------------------------------------------------
qachain = create_stuff_documents_chain(model, chat_prompt)
chat_history_retriever = create_history_aware_retriever(model, retriever, contextualize_prompt)
answer_chain = create_stuff_documents_chain(model, qa_prompt)

RAG_chain = create_retrieval_chain(chat_history_retriever, answer_chain)

# -----------------------------------------------------------------------------
# 5. Database Setup
# -----------------------------------------------------------------------------
DB_PATH = "chat_history.db"

def initialize_database():
    """
    Creates necessary tables for storing chat history if they don't exist.
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS chat_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT,
            role TEXT,  -- 'user' or 'ai'
            message TEXT,
            timestamp TEXT
        )
    ''')
    conn.commit()
    conn.close()

initialize_database()

def save_message_to_db(session_id, role, message):
    """
    Stores a chat message in the database with a timestamp (WhatsApp-like format: '10:30 PM').
    """
    timestamp = datetime.now().strftime("%I:%M %p")
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO chat_history (session_id, role, message, timestamp) VALUES (?, ?, ?, ?)",
        (session_id, role, message, timestamp)
    )
    conn.commit()
    conn.close()

def load_chat_history_from_db(session_id):
    """
    Retrieves chat history for a given session from the database 
    and returns a ChatMessageHistory object.
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT role, message, timestamp FROM chat_history WHERE session_id = ?", (session_id,))
    chat_history = cursor.fetchall()
    conn.close()

    history = ChatMessageHistory()
    for role, message, _ in chat_history:
        if role == "user":
            history.add_user_message(message)
        else:
            history.add_ai_message(message)
    return history

def get_session_history(session_id):
    """
    Retrieve or create chat history for a given session from the database.
    """
    history = load_chat_history_from_db(session_id)
    return history

# -----------------------------------------------------------------------------
# 6. Combine Chain with Message History
# -----------------------------------------------------------------------------
conversation_RAG_Chain = RunnableWithMessageHistory(
    RAG_chain,
    get_session_history,
    input_messages_keys="input",
    history_messages_key="chat_history",
    output_message_keys="answer",
)

# -----------------------------------------------------------------------------
# 7. Main Chat Function
# -----------------------------------------------------------------------------
def chat(input_text, session_id="chat1"):
    """
    Handles the chat flow and returns only the AI's response.
    """
    # Retrieve chat history from the database
    chat_history = load_chat_history_from_db(session_id)

    # Invoke the RAG chain
    response_data = conversation_RAG_Chain.invoke(
        {"input": input_text, "chat_history": chat_history.messages},
        config={"configurable": {"session_id": session_id}}
    )

    # Extract AI's response
    response = response_data.get("answer", "Sorry, I could not retrieve an answer. Please try again.")

    # Store messages in the database
    save_message_to_db(session_id, "user", input_text)
    save_message_to_db(session_id, "ai", response)

    # Return the response
    return response

# -----------------------------------------------------------------------------
# 8. Configure Logging
# -----------------------------------------------------------------------------
logging.getLogger('langchain_core.callbacks.manager').setLevel(logging.ERROR)

# -----------------------------------------------------------------------------
# 
console = Console()

answer = chat("Hi, my name is Siddharth and I study at IITM, I am an AI Engineer and Data Scientist?", session_id="chat1")
console.print(Markdown(answer))
answer = chat("What is my name and where do I study and Wwhat do I do?", session_id="chat1")
console.print(Markdown(answer))
answer = chat("What is SGDRegressor? How to use it?", session_id="chat1")
console.print(Markdown(answer))
