import warnings
from functools import lru_cache
from typing import Dict, List, Any
import os

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from pydantic import BaseModel, Field
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from langchain_google_genai import ChatGoogleGenerativeAI

# Suppress deprecation warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)

# Global singletons for components
_embeddings = None
_vector_store = None
_llm = None
_mcq_cache = {}

# Define the schema for MCQ output
class MCQQuestion(BaseModel):
    question: str = Field(description="The question text")
    options: List[str] = Field(description="List of 4 options")
    correct_answer: str = Field(description="The correct answer")
    explanation: str = Field(description="Explanation of why the answer is correct")

class MCQSet(BaseModel):
    questions: List[MCQQuestion] = Field(description="List of MCQ questions")

def get_api_key() -> str:
    """Get API key for Google Generative AI"""
    #api_key =  os.environ.get("GOOGLE_API_KEY")
    api_key = "AIzaSyCV5i-u0oROux-Wt0TMqiRivVD6H0rGbjc"
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
            temperature=0.7
        )
    return _llm

def get_weeks_range(quiz_type: str) -> str:
    """Determine weeks range based on quiz type"""
    if quiz_type.lower() == "quiz1":
        return "Weeks 1-4"
    elif quiz_type.lower() == "quiz2":
        return "Weeks 1-8"
    elif quiz_type.lower() == "endterm":
        return "Weeks 1-10"
    else:
        raise ValueError(f"Invalid quiz type: {quiz_type}. Must be one of: quiz1, quiz2, endterm")

@lru_cache(maxsize=20)
def get_mcq_prompt(weeks_range: str) -> ChatPromptTemplate:
    """Get the MCQ generation prompt"""
    return ChatPromptTemplate.from_messages([
        (
            "system",
            f"""You are an expert Machine Learning Practice instructor. Generate multiple choice questions that reference code snippets
or coding concepts to test a student's understanding of machine learning implementation.

Guidelines:
- Create questions about how code snippets work, what specific functions do, or how libraries are used in machine learning contexts
- Each question must have 4 distinct options (A, B, C, D) with only one correct answer
            - Focus on practical ML knowledge for the {weeks_range} range of the course
- Include code snippets from scikit-learn, NumPy, pandas, TensorFlow, or PyTorch when relevant
- Make the questions challenging but fair, testing conceptual understanding rather than memorization
- Ensure options are not too similar to each other to avoid ambiguity
- Provide a clear, educational explanation for why the correct answer is right

Context: {{context}}
            Number of questions: {{num_questions}}"""
        ),
        (
            "human",
            "Generate MCQ questions in JSON format with question text, options, correct answer, and explanation."
        )
    ])

def generate_mcqs(
        quiz_type: str,
        num_questions: int = 20,
        persist_directory: str = "vector_store"
) -> Dict[str, Any]:
    """
Generate multiple-choice questions for a specific quiz type.

Args:
quiz_type: Type of quiz (quiz1, quiz2, or endterm)
num_questions: Number of questions to generate
persist_directory: Directory for the vector store

Returns:
Dictionary containing generated MCQs and metadata
    """
    # Check cache first
    cache_key = f"{quiz_type}_{num_questions}"
    if cache_key in _mcq_cache:
        return _mcq_cache[cache_key]

    try:
        # Determine weeks range based on quiz type
        weeks_range = get_weeks_range(quiz_type)

        # Get components
        llm = get_llm()
        vectorstore = get_vector_store(persist_directory)

        # Retrieve context from the vector store
        search_results = vectorstore.similarity_search(
            weeks_range,
            k=min(num_questions * 2, 50)  # Get more context than needed for better coverage
        )

        # Combine context from the search results
        context = "\n".join([doc.page_content for doc in search_results])

        # Create the chain for MCQ generation
        mcq_prompt = get_mcq_prompt(weeks_range)
        output_parser = JsonOutputParser(pydantic_object=MCQSet)
        chain = mcq_prompt | llm | output_parser

        # Generate the MCQs
        response = chain.invoke({
            "context": context,
            "num_questions": num_questions
        })
        # Safer parsing of the response
        if hasattr(response, "questions"):
            # If response is a Pydantic object
            questions = response.questions
        elif hasattr(response, "dict"):
            # If response has dict method but questions isn't directly accessible
            questions = response.dict().get("questions", [])
        elif isinstance(response, dict):
            # If response is already a dictionary
            questions = response.get("questions", [])
        elif isinstance(response, list):
            # If response is directly a list of questions
            questions = response
        else:
            # Fall back to empty list if we can't determine the format
            questions = []
        # Format the result
        result = {
            "success": True,
            "message": f"Successfully generated {len(response.questions) if hasattr(response, 'questions') else num_questions} MCQs",
            "quiz_type": quiz_type,
            "weeks_range": weeks_range,
            "questions": questions
        }

        # Cache the result
        _mcq_cache[cache_key] = result
        return result

    except Exception as e:
        return {
            "success": False,
            "message": f"Failed to generate MCQs: {str(e)}",
            "quiz_type": quiz_type,
            "questions": []
        }

def clear_cache():
    """Clear all MCQ caches"""
    global _mcq_cache
    _mcq_cache = {}
    get_mcq_prompt.cache_clear()

