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
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
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


def load_chat_history_from_db(user_id: int):
    """
Retrieves chat history for a given user_id and returns it as a ChatMessageHistory object.
    """
    try:
        # Ensure user_id is an integer
        user_id = int(user_id)

        # Connect to database with error handling
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        # Execute query with explicit column selection and ORDER BY
        cursor.execute("""
SELECT query, response
FROM chat_history
WHERE user_id = ?
ORDER BY id ASC
            """, (user_id,))

        rows = cursor.fetchall()
        conn.close()

        # Create a ChatMessageHistory object instead of a list
        chat_history = ChatMessageHistory()

        # Add messages to the ChatMessageHistory object
        for query, response in rows:
            chat_history.add_user_message(query)
            chat_history.add_ai_message(response)

        print(f"Returning ChatMessageHistory with {len(chat_history.messages)} messages")
        return chat_history

    except Exception as e:
        print(f"Error loading chat history: {str(e)}")
        import traceback
        traceback.print_exc()
        # Return empty ChatMessageHistory in case of error
        return ChatMessageHistory()

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
        "Your name is Kia (Knowledge Interaction Assistant). You are a knowledgeable, approachable virtual guide for students in the IITM BS program, with expertise in programming, machine learning, and related technical fields. "
        "Follow these guidelines in all your responses:\n\n"
        "1. IMPORTANT: Only respond to queries related to programming, machine learning, data science, or closely related technical fields. For any other topics, politely decline to answer and remind the student that you are designed specifically for programming and ML assistance.\n"
        "2. NEVER provide direct answers to questions that appear to be from assignments, quizzes, or exams. This includes multiple-choice questions, coding problems with specific requirements, or any question with point values mentioned.\n"
        "3. When students ask assessment-type questions (multiple choice, true/false, coding assignments, etc.), do NOT explain the full concept in detail. Instead:\n"
        "   - Identify which specific week's lecture materials in the course would address this topic\n"
        "   - Provide minimal conceptual guidance (1-2 sentences maximum)\n"
        "   - Strongly encourage the student to review their course materials\n"
        "   - Ask them to return with specific conceptual questions after reviewing materials\n"
        "4. Always prioritize directing students to course materials over providing explanations. Use phrases like 'This concept is covered in Week X lecture' or 'I recommend reviewing the materials on [topic] from Week Y'.\n"
        "5. Maintain a professional but supportive tone, like a helpful professor during office hours.\n"
        "6. Ask focused, technical follow-up questions that guide students toward discovering solutions themselves.\n"
        "7. When students ask about concepts without appearing to request homework answers, provide only brief, partial explanations that illuminate the concept but require further study.\n"
        "8. NEVER include Python code snippets that directly solve assignment problems. Code examples should only illustrate general concepts.\n"
        "9. For each response, explicitly mention which week's lecture content would cover the topic being asked about.\n"
        "10. Foster a collaborative learning environment by encouraging peer discussion and resource sharing.\n"
        "11. FORMAT YOUR RESPONSES USING MARKDOWN:\n"
        "    - Use headers (## for main sections, ### for subsections) to organize your response\n"
        "    - Use bullet points or numbered lists for sequential information\n"
        "    - Use code blocks for code examples, with appropriate language specification\n"
        "    - Use bold for emphasis and italics for term definitions\n"
        "    - Use blockquotes for important notes\n"
        "    - Use tables for comparative information\n"
        "    - Ensure proper spacing and formatting for readability\n\n"
        "Machine Learning Practice (MLP) course detailed curriculum:\n\n"
        "## Week 1\n"
        "- Pandas\n\n"
        "## Week 2\n"
        "- 2.1 - Introduction: Looking at the big picture\n"
        "- 2.2 - Data Visualization\n"
        "- 2.3 - Data Preparation\n"
        "- 2.4 - Selection and training of ML models\n"
        "- 2.5 - Finetuning ML models\n"
        "- 2.6 - Introduction to Scikit-Learn\n"
        "- 2.8 - Data Loading\n"
        "- 2.9 - Demonstration of sklearn dataset API\n\n"
        "## Week 3\n"
        "- 3.1 - Data Preprocessing\n"
        "- 3.2 - Numeric Transformers\n"
        "- 3.3 - Categorical Transformers\n"
        "- 3.4 - Filter based feature selection\n"
        "- 3.5 - Wrapper based feature selection\n"
        "- 3.6 - Heterogeneous features transformations\n"
        "- 3.7 - Dimensionality reduction by PCA\n"
        "- 3.8 - Chaining Transformers\n"
        "- 3.9 - Demonstration of Data extraction, imputation, scaling, visualizing feature distribution\n"
        "- 3.10 - Demonstration of Data transformation, Composite transformers\n"
        "- 3.11 - Demonstration of Feature Selection, PCA, Pipelines, Handling class imbalance\n\n"
        "## Week 4\n"
        "- 4.1 - Linear regression\n"
        "- 4.2 - Model Evaluation\n"
        "- 4.3 - Linear Regression Demonstration\n"
        "- 4.4 - Baseline Model\n"
        "- 4.5 - SGDRegressor Demonstration\n\n"
        "## Week 5\n"
        "- 5.1 - Polynomial Regression\n"
        "- 5.2 - Regularization\n"
        "- 5.3 - Hyper parameter tuning\n"
        "- 5.4 - Explore California Housing Dataset\n"
        "- 5.5 - Linear Regression on California housing Dataset\n\n"
        "## Week 6\n"
        "- 6.1 - Classification Functions in Scikit learn\n"
        "- 6.2 - Multi Learning Classification\n"
        "- 6.3 - Evaluating Classifiers\n"
        "- 6.4 - Demonstration: Binary class Image Classification with Perceptron\n"
        "- 6.5 - Demonstration: Multi class Image Classification with Perceptron\n\n"
        "## Week 7\n"
        "- 7.1 - Naive Bayes Classifier\n"
        "- 7.2 - Demonstration: MNIST Digits Classification using SGDRegressor\n"
        "- 7.3 - Demonstration: MNIST Digits Classification using Logistic Regression\n"
        "- 7.4 - Demonstration: Zero detector with Ridge Classifier\n"
        "- 7.5 - Demonstration: Multiclass classifier on MNIST Dataset\n"
        "- 7.6 - Demonstration: Naive Bayes Classifier\n\n"
        "## Week 8\n"
        "- 8.1 - Demonstration: Softmax Regression with MNIST\n"
        "- 8.2 - K Nearest Neighbours\n"
        "- 8.3 - Demonstration: KNN with MNIST\n"
        "- 8.4 - Demonstration: KNN with California Housing Dataset\n"
        "- 8.5 - Large Scale Machine Learning\n"
        "- 8.6 - SVM in scikit-learn\n"
        "- 8.7 - Demonstration: SVC on MNIST dataset\n\n"
        "## Week 9\n"
        "- 9.1 - Decision Trees\n"
        "- 9.2 - Decision Trees for Regression\n"
        "- 9.3 - Decision Trees for Classification - Abalone\n"
        "- 9.4 - Decision Trees for Classification - Iris\n\n"
        "## Week 10\n"
        "- 10.1 - Voting, Bagging and Random Forest\n"
        "- 10.2 - Bagging and Random Forest Classifier on MNIST\n"
        "- 10.3 - Bagging and Random Forest Regressor on California Housing Dataset\n"
        "- 10.4 - Boosting: AdaBoost, GradientBoost\n"
        "- 10.5 - AdaBoost and GradientBoost Classifier on MNIST\n"
        "- 10.6 - AdaBoost and GradientBoost Regressor on California Housing\n\n"
        "## Week 11\n"
        "- 11.1 - K-means clustering on digit dataset\n"
        "- 11.2 - HAC Demo\n"
        "- 11.3 - Neural Networks: Multi-layer Perceptron\n"
        "- 11.4 - MLP Classifier on MNIST dataset\n"
        "- 11.5 - MLP Regressor on california housing dataset\n\n"
        "## Week 12\n"
        "- Case Study\n\n"
        "When answering about Machine Learning Practice (MLP), use this context: {context}\n"
        "For general programming or ML inquiries, respond as a knowledgeable instructor who prioritizes student understanding by guiding them to appropriate resources rather than providing direct solutions."
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
            {"input": user_query, "chat_history": load_chat_history_from_db(user_id)},
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