import warnings
from functools import lru_cache
from typing import Dict, Any
import os

from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from langchain_google_genai import ChatGoogleGenerativeAI

# Suppress deprecation warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)

# Global singletons for components
_embeddings = None
_vector_store = None
_llm = None
_notes_cache = {}

def get_api_key() -> str:
    """Get API key for Google Generative AI"""
    api_key = os.getenv("GOOGLE_API_KEY")
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
            google_api_key=get_api_key()
        )
    return _llm

@lru_cache(maxsize=50)
def generate_topic_summary(text: str, topic: str) -> str:
    """Generate a summary of topic-specific text using Google Gemini"""
    llm = get_llm()

    prompt = (
        f"You are an expert machine learning educator creating concise study notes. "
        f"Create detailed yet concise notes on '{topic}' based on the following content. "
        f"Your response MUST be in Markdown format with careful attention to spacing:"
        f"\n- Add two blank lines before each heading AND one blank line after each heading"
        f"\n- Use clear hierarchical headings (## for main sections, ### for subsections)"
        f"\n- Include a blank line after each bullet point list"
        f"\n- Ensure proper table formatting with spaces between columns and rows"
        f"\n- For tables, use this format with proper alignment and spacing:\n"
        f"  | Column1 | Column2 | Column3 |\n"
        f"  | ------- | :-----: | ------: |\n"
        f"  | Left    | Center  | Right   |\n"
        f"\n- Add a blank line before and after code blocks and tables"
        f"\n- Use bullet points for key concepts with a blank line between lists"
        f"\n- Include code examples with proper syntax highlighting when relevant"
        f"\n- Add mathematical formulas using LaTeX notation (\\( \\) for inline, \\[ \\] for display)"
        f"\n\nKeep the notes between 600-700 words. Focus on technical accuracy and clarity."
        f"\nEnd with a brief concluding paragraph summarizing the importance of {topic} in machine learning."
        f"\n\nContent to summarize:\n{text}"
    )

    try:
        response = llm.invoke(prompt)
        return response.content if hasattr(response, "content") else str(response)
    except Exception as e:
        return f"Error generating summary: {str(e)}"

def generate_topic_notes(
        topic: str,
        persist_directory: str = "vector_store"
) -> Dict[str, Any]:
    """
Generate comprehensive notes on a specific machine learning topic.

Args:
topic: The topic to generate notes for
persist_directory: Directory for the vector store

Returns:
Dictionary containing generated notes and metadata
    """
    # Check cache first
    if topic in _notes_cache:
        return _notes_cache[topic]

    try:
        # Get vector store
        vector_store = get_vector_store(persist_directory)

        # Retrieve relevant chunks, with a limit to prevent overly large prompts
        retriever = vector_store.as_retriever(search_kwargs={"k": 20})
        docs = retriever.get_relevant_documents(topic)

        if not docs:
            result = {
                "success": False,
                "message": f"No information found for topic '{topic}'",
                "notes": "",
                "topic": topic
            }
        else:
            # Combine text from documents, with a limit to prevent token overflow
            combined_text = "\n".join([doc.page_content for doc in docs[:15]])

            # Generate summary
            notes = generate_topic_summary(combined_text, topic)

            result = {
                "success": True,
                "message": f"Successfully generated notes for '{topic}'",
                "notes": notes,
                "topic": topic
            }

        # Cache the result
        _notes_cache[topic] = result
        return result

    except Exception as e:
        return {
            "success": False,
            "message": f"Failed to generate notes: {str(e)}",
            "notes": "",
            "topic": topic
        }

def clear_cache():
    """Clear all notes caches"""
    global _notes_cache
    _notes_cache = {}
    generate_topic_summary.cache_clear()
