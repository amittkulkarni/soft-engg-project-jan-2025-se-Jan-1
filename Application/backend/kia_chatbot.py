import os
import sqlite3
import warnings
from functools import lru_cache
from datetime import datetime
from typing import Dict, Any

warnings.filterwarnings("ignore")

# LangChain imports
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.chains import create_retrieval_chain, create_history_aware_retriever
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_chroma import Chroma
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory

# Global singletons
_embeddings = None
_vector_store = None
_llm = None
_rag_chain = None
_conversation_chain = None

# Database configuration
if not os.path.exists("instance"):
    os.makedirs("instance")

DB_PATH = os.path.join("instance", "app.db")

def get_api_key() -> str:
    """Get API key for Google Generative AI"""
    api_key = "AIzaSyAmZBJC_WzWLlaUdfiM3GMu9UkCjAWOJ0o"
    if not api_key:
        raise ValueError("Google API key is not set")
    return api_key

def get_embeddings():
    """Singleton for embeddings"""
    global _embeddings
    if _embeddings is None:
        _embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2"
        )
    return _embeddings

def get_vector_store(persist_directory: str = "vector_store"):
    """Singleton for vector store"""
    global _vector_store
    if _vector_store is None:
        _vector_store = Chroma(
            collection_name="pdf_embeddings",
            embedding_function=get_embeddings(),
            persist_directory=persist_directory
        )
    return _vector_store

def get_llm():
    """Singleton for language model"""
    global _llm
    if _llm is None:
        _llm = ChatGoogleGenerativeAI(
            model="gemini-1.5-flash",
            google_api_key=get_api_key(),
            convert_system_message_to_human=False
        )
    return _llm

def initialize_database():
    """Initialize the chat history database"""
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

def save_chat_turn_to_db(user_id: int, query: str, response: str):
    """Save a chat turn to the database"""
    created_at = datetime.now().strftime("%I:%M %p")
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO chat_history (user_id, query, response, created_at) VALUES (?, ?, ?, ?)",
        (user_id, query, response, created_at)
    )
    conn.commit()
    conn.close()

def load_chat_history_from_db(user_id: int) -> ChatMessageHistory:
    """Load chat history from the database"""
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
    """Delete a user's chat history"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM chat_history WHERE user_id = ?", (user_id,))
    conn.commit()
    conn.close()

@lru_cache(maxsize=1)
def get_system_prompt() -> str:
    """Get the main system prompt for Kia"""
    return (
        "Your name is Kia (Knowledge Interaction Assistant). You are a friendly, approachable machine learning tutor with a casual personality. "
        "Follow these guidelines in all your responses:\n"
        "1. Keep responses brief and conversational - like you're chatting with a friend (2-3 sentences unless detailed explanation is requested)\n"
        "2. Give hints instead of complete answers to encourage learning - 'Have you considered...?' or 'Try thinking about...'\n"
        "3. Use occasional emojis and casual language to maintain a warm, friendly tone\n"
        "4. Ask follow-up questions that guide students toward discovering answers themselves\n"
        "5. Connect ML concepts to real-world applications with simple examples\n"
        "6. If a student seems stuck, provide just enough guidance to help them progress\n\n"
        "When answering about Machine Learning Practice (MLP), use this context: {context}\n"
        "For general conversation, respond naturally as a friendly tutor who wants to build rapport with students."
    )

@lru_cache(maxsize=1)
def get_retriever_prompt() -> str:
    """Get the retriever context prompt"""
    return (
        "You need to understand the conversation history with this student. "
        "When they refer to something mentioned earlier, recall that information. "
        "Pay attention to personal details they've shared, topics they're struggling with, "
        "and maintain a casual, supportive tone throughout the conversation."
    )

def get_chain():
    """Get the RAG conversation chain"""
    global _rag_chain, _conversation_chain

    if _rag_chain is None or _conversation_chain is None:
        # Initialize the vector store retriever
        vector_store = get_vector_store()
        retriever = vector_store.as_retriever(search_kwargs={"k": 3})

        # Create the prompts
        system_prompt = get_system_prompt()
        retriever_prompt = get_retriever_prompt()

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

        # Get the language model
        llm = get_llm()

        # Create the chains
        qa_chain = create_stuff_documents_chain(llm, chat_prompt)
        chat_history_retriever = create_history_aware_retriever(llm, retriever, contextualize_prompt)
        answer_chain = create_stuff_documents_chain(llm, qa_prompt)
        _rag_chain = create_retrieval_chain(chat_history_retriever, answer_chain)

        # Create the conversation chain with message history
        _conversation_chain = RunnableWithMessageHistory(
            _rag_chain,
            lambda session_id: load_chat_history_from_db(int(session_id)),
            input_messages_keys="input",
            history_messages_key="chat_history",
            output_message_keys="answer",
        )

    return _conversation_chain

def get_answer(user_id: int, user_query: str) -> Dict[str, Any]:
    """
Get an answer from Kia for a user query.

Args:
user_id: The user ID
user_query: The user's query text

Returns:
Dictionary with response data
    """
    try:
        # Initialize the database if it doesn't exist
        initialize_database()

        # Get the conversation chain
        conversation_chain = get_chain()

        # Get the response
        response_data = conversation_chain.invoke(
            {"input": user_query, "chat_history": load_chat_history_from_db(user_id).messages},
            config={"configurable": {"session_id": str(user_id)}}
        )

        ai_response = response_data.get("answer", "Hmm, I'm having a little trouble with that right now. Can we try a different question? 😊")

        # Save the chat turn
        save_chat_turn_to_db(user_id, user_query, ai_response)

        return {
            "success": True,
            "message": "Response generated successfully",
            "response": ai_response,
            "user_id": user_id
        }

    except Exception as e:
        return {
            "success": False,
            "message": f"Failed to generate response: {str(e)}",
            "response": "I seem to be having a little brain freeze! Let's chat again in a moment? 😅",
            "user_id": user_id
        }

def clear_user_history(user_id: int) -> Dict[str, Any]:
    """
Clear chat history for a user.

Args:
user_id: The user ID

Returns:
Dictionary with status information
    """
    try:
        delete_user_history(user_id)
        return {
            "success": True,
            "message": f"Chat history cleared for user {user_id}",
            "user_id": user_id
        }
    except Exception as e:
        return {
            "success": False,
            "message": f"Failed to clear chat history: {str(e)}",
            "user_id": user_id
        }