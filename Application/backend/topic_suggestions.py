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
_suggestions_cache = {}

# Define the schema for suggestions output
class TopicSuggestion(BaseModel):
    topic: str = Field(description="The ML topic that needs improvement")
    suggestions: List[str] = Field(description="List of learning suggestions for this topic")
    resources: List[str] = Field(description="Recommended resources to study this topic")

class SuggestionSet(BaseModel):
    overall_assessment: str = Field(description="General assessment of the student's performance")
    topic_suggestions: List[TopicSuggestion] = Field(description="List of topic-specific suggestions")
    general_tips: List[str] = Field(description="General learning tips applicable to all topics")

def get_api_key() -> str:
    """Get API key for Google Generative AI"""
    api_key = os.environ.get("GOOGLE_API_KEY")
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

@lru_cache(maxsize=20)
def get_suggestions_prompt() -> ChatPromptTemplate:
    return ChatPromptTemplate.from_messages([
        (
            "system",
            """You are an expert Machine Learning education advisor. Given a list of questions that a student
answered incorrectly, analyze them to identify the underlying topics, and provide targeted learning
suggestions to help the student improve.

Guidelines:
- Identify 2-4 key ML topics that the student needs to improve based on the wrong questions
- For each topic, provide 2-3 specific learning suggestions
- For each topic, recommend 1-2 resources (textbooks, websites, or practice exercises)
- Include general learning tips that apply across all topics
- Provide an overall assessment of the student's understanding and learning path
- Keep suggestions practical, specific, and actionable
- Focus on conceptual understanding rather than just memorization

The wrong questions are: {{wrong_questions}}

Return your response in the following JSON format:
{{
"overall_assessment": "A brief assessment of the student's performance and knowledge gaps",
"topic_suggestions": [
{{
"topic": "Topic name",
"suggestions": ["Suggestion 1", "Suggestion 2"],
"resources": ["Resource 1", "Resource 2"]
}}
],
"general_tips": ["General tip 1", "General tip 2"]
}}

            You MUST return valid JSON. Do not include any explanations outside the JSON structure."""
        ),
        (
            "human",
            "Generate personalized learning suggestions based on these wrong answers."
        )
    ])

def generate_topic_suggestions(
        wrong_questions: List[str],
        persist_directory: str = "vector_store"
) -> Dict[str, Any]:
    """
Generate personalized learning suggestions based on questions answered incorrectly.

Args:
wrong_questions: List of question texts that were answered incorrectly
persist_directory: Directory for the vector store

Returns:
Dictionary containing suggestions and metadata
    """
    # Check cache first - using joined questions as key
    cache_key = "_".join(sorted([q[:50] for q in wrong_questions]))  # Limit length for cache key
    if cache_key in _suggestions_cache:
        return _suggestions_cache[cache_key]

    try:
        # Handle empty input
        if not wrong_questions:
            return {
                "success": True,
                "message": "No wrong questions provided",
                "suggestions": {
                    "overall_assessment": "All questions were answered correctly. Great job!",
                    "topic_suggestions": [],
                    "general_tips": ["Continue practicing to maintain your knowledge."]
                }
            }

        # Get components
        llm = get_llm()
        vectorstore = get_vector_store(persist_directory)

        # Combine all wrong questions into a single search query
        search_query = " ".join(wrong_questions)

        # Retrieve context from the vector store
        search_results = vectorstore.similarity_search(
            search_query,
            k=min(len(wrong_questions) * 2, 30)  # Proportional retrieval with upper limit
        )

        # Extract context from search results
        context = "\n".join([doc.page_content for doc in search_results])

        # Create the chain for suggestions generation
        suggestions_prompt = get_suggestions_prompt()
        output_parser = JsonOutputParser(pydantic_object=SuggestionSet)
        chain = suggestions_prompt | llm | output_parser

        # Generate the suggestions
        response = chain.invoke({
            "wrong_questions": wrong_questions,
            "context": context
        })

        # Safely parse the response
        if hasattr(response, "topic_suggestions"):
            suggestions = response
        elif hasattr(response, "dict"):
            suggestions = response.dict()
        elif isinstance(response, dict):
            suggestions = response
        else:
            # Fall back to a default structure
            suggestions = {
                "overall_assessment": "Unable to generate detailed assessment.",
                "topic_suggestions": [],
                "general_tips": [
                    "Review the course materials for the topics you missed.",
                    "Practice additional exercises in those areas."
                ]
            }

        # Format the result
        result = {
            "success": True,
            "message": "Successfully generated learning suggestions",
            "suggestions": suggestions
        }

        # Cache the result
        _suggestions_cache[cache_key] = result
        return result

    except Exception as e:
        return {
            "success": False,
            "message": f"Failed to generate suggestions: {str(e)}",
            "suggestions": {
                "overall_assessment": "We encountered an issue analyzing your answers.",
                "topic_suggestions": [],
                "general_tips": [
                    "Review lecture materials for topics where you made mistakes.",
                    "Consider discussing difficult concepts with your instructor."
                ]
            }
        }

def clear_cache():
    """Clear all suggestions caches"""
    global _suggestions_cache
    _suggestions_cache = {}
    get_suggestions_prompt.cache_clear()