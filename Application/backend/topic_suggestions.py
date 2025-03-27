import os
import logging
from typing import Dict, List, Any
# Import LangChain components
from langchain_core.prompts import PromptTemplate
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field

# Configure logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Model definitions
class TopicSuggestion(BaseModel):
    topic: str = Field(description="The ML topic that needs improvement")
    suggestions: List[str] = Field(description="List of learning suggestions for this topic")

class SuggestionSet(BaseModel):
    overall_assessment: str = Field(description="General assessment of the student's performance")
    topic_suggestions: List[TopicSuggestion] = Field(description="List of topic-specific suggestions")
    general_tips: List[str] = Field(description="General learning tips applicable to all topics")

# Global component initialization
_embeddings = None
_vector_store = None
_llm = None

def get_api_key() -> str:
    """Get API key for Google Generative AI"""
    api_key = os.environ.get("GOOGLE_API_KEY", "AIzaSyCV5i-u0oROux-Wt0TMqiRivVD6H0rGbjc")
    if not api_key:
        raise ValueError("Google API key is not set")
    return api_key

def get_embeddings():
    """Get embeddings singleton"""
    global _embeddings
    if _embeddings is None:
        _embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2"
        )
    return _embeddings

def get_vector_store(persist_directory: str = "vector_store"):
    """Get vector store singleton"""
    global _vector_store
    if _vector_store is None:
        _vector_store = Chroma(
            collection_name="pdf_embeddings",
            embedding_function=get_embeddings(),
            persist_directory=persist_directory
        )
    return _vector_store

def get_llm():
    """Get LLM singleton"""
    global _llm
    if _llm is None:
        _llm = ChatGoogleGenerativeAI(
            model="gemini-1.5-flash",
            google_api_key=get_api_key(),
            temperature=0.2,
            max_output_tokens=2048
        )
    return _llm

def create_prompt():
    """Create the prompt template for suggestions"""
    template = """You are an expert Machine Learning education advisor analyzing questions
a student answered incorrectly to provide personalized learning suggestions.

QUESTIONS THE STUDENT MISSED:
{formatted_questions}

REFERENCE MATERIALS:
{context}

YOUR TASK:
1. Analyze each question to identify specific ML concepts being tested
2. Determine knowledge gaps based on the question content and code samples
3. Create a personalized learning plan that addresses these specific gaps

FORMAT YOUR RESPONSE AS VALID JSON:
{format_instructions}

IMPORTANT: Focus ONLY on the concepts in these specific questions. Do not make generic recommendations."""

    parser = PydanticOutputParser(pydantic_object=SuggestionSet)
    prompt = PromptTemplate(
        template=template,
        input_variables=["formatted_questions", "context"],
        partial_variables={"format_instructions": parser.get_format_instructions()}
    )

    return prompt, parser

def generate_topic_suggestions(wrong_questions: List[str]) -> Dict[str, Any]:
    """Generate personalized topic suggestions based on incorrect answers"""
    logger.info(f"Generating suggestions for {len(wrong_questions)} questions")

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

        # Format questions with explicit numbering
        formatted_questions = ""
        for i, question in enumerate(wrong_questions):
            formatted_questions += f"QUESTION {i+1}:\n{question}\n\n"

        logger.info(f"Formatted {len(wrong_questions)} questions")

        # Get relevant context from vector store
        vector_store = get_vector_store()
        all_contexts = []

        for question in wrong_questions:
            results = vector_store.similarity_search(question, k=3)
            context = "\n".join([doc.page_content for doc in results])
            all_contexts.append(context)

        combined_context = "\n\n---\n\n".join(all_contexts)
        logger.info(f"Retrieved context ({len(combined_context)} chars)")

        # Create prompt and parser
        prompt_template, output_parser = create_prompt()

        # Get LLM
        llm = get_llm()

        # Generate suggestions
        formatted_prompt = prompt_template.format(
            formatted_questions=formatted_questions,
            context=combined_context[:5000]  # Limit context size
        )

        logger.info("Sending request to LLM")
        response = llm.invoke(formatted_prompt)
        logger.info(f"Received response from LLM: {response.content[:100]}...")

        # Parse response
        try:
            parsed_response = output_parser.parse(response.content)
            suggestions = parsed_response.dict()
            logger.info("Successfully parsed LLM response")
        except Exception as e:
            logger.error(f"Failed to parse LLM response: {e}")
            # Fallback to a simple structure
            suggestions = {
                "overall_assessment": "Analysis generated but couldn't be properly formatted.",
                "topic_suggestions": [],
                "general_tips": [
                    "Review the course materials for the topics you missed.",
                    "Practice additional exercises in those areas."
                ]
            }

        # Return successful response
        return {
            "success": True,
            "message": "Successfully generated learning suggestions",
            "suggestions": suggestions
        }

    except Exception as e:
        logger.error(f"Error generating suggestions: {str(e)}", exc_info=True)
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