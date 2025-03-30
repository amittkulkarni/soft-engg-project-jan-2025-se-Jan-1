import os
import warnings
from typing import Dict, Any
from functools import lru_cache

from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from langchain_google_genai import ChatGoogleGenerativeAI

# Suppress deprecation warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)

# Global singletons for components
_embeddings = None
_vector_store = None
_llm = None
_summary_cache = {}

def get_api_key() -> str:
    """Get API key from environment variable"""
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise ValueError("GOOGLE_API_KEY environment variable is not set")
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

def get_slides_filename(week: int) -> str:
    """Generate the standardized filename for a week's slides"""
    return f"MLP Week {week} Slides.pdf"

@lru_cache(maxsize=20)
def generate_slides_summary(text: str, week: int) -> str:
    """Generate a summary of the slides content using Google Gemini"""
    llm = get_llm()

    prompt = (
        f"You are an expert Machine Learning educator creating comprehensive week summaries. "
        f"Create a detailed summary of Week {week} slides (700-900 words) that captures all key concepts. "
        f"Your response MUST be in Markdown format with:"
        f"\n\n## Formatting Requirements:"
        f"\n- Clear hierarchical headings (# for title, ## for main sections, ### for subsections)"
        f"\n- Add a blank line before AND after each heading"
        f"\n- Use bullet points for key concepts with a blank line between lists"
        f"\n- Format code examples in proper code blocks with Python syntax highlighting:``````"
        f"\n- Present mathematical formulas using LaTeX notation (\\( \\) for inline, \\[ \\] for display)"
        f"\n- For tables, use proper Markdown table formatting with alignment:\n"
        f"  | Column1 | Column2 | Column3 |\n"
        f"  | ------- | :-----: | ------: |\n"
        f"  | Left    | Center  | Right   |"
        f"\n- Add a blank line before and after code blocks and tables"

        f"\n\n## Content Requirements:"
        f"\n- Begin with a clear heading: '# Week {week}: [Main Topic]'"
        f"\n- Start the first paragraph with 'In Week {week},' introducing the main topics"
        f"\n- Include major concepts, algorithms, mathematical formulas, and code implementations"
        f"\n- Explain relationships between concepts and their practical applications"
        f"\n- If present, include computational complexity and performance considerations"
        f"\n- Highlight important functions, libraries, and implementation details"
        f"\n- End with a comprehensive conclusion starting with 'In conclusion, Week {week}'"
        f"\n- If Dr. Ashish Tendulkar is mentioned, refer to him as 'Prof. Ashish' in the conclusion"

        f"\n\nSlides content:\n{text}"
    )

    try:
        response = llm.invoke(prompt)
        return response.content if hasattr(response, "content") else str(response)
    except Exception as e:
        return f"Error generating summary: {str(e)}"

def retrieve_slides_content(week: int, persist_directory: str = "vector_store") -> str:
    """Retrieve the slides content for a specific week"""
    vector_store = get_vector_store(persist_directory)

    # Get the expected filename for this week
    filename = get_slides_filename(week)

    # Use retriever with exact filename match
    retriever = vector_store.as_retriever(
        search_kwargs={"filter": {"source": filename}, "k": 10}
    )

    docs = retriever.get_relevant_documents("")

    if not docs:
        # Try an alternative search by week number if filename doesn't match
        retriever = vector_store.as_retriever(
            search_kwargs={"filter": {"week": str(week)}, "k": 10}
        )
        docs = retriever.get_relevant_documents("")

    if not docs:
        return ""

    # Combine document contents
    combined_text = "\n".join([doc.page_content for doc in docs])
    return combined_text

def summarize_week_slides(week: int, persist_directory: str = "vector_store") -> Dict[str, Any]:
    """
Generate a summary for slides from a specific week.

Args:
week: Week number (integer)
persist_directory: Directory of the vector store

Returns:
Dictionary with summary and metadata
    """
    global _summary_cache

    # Check if we already have this summary cached
    cache_key = f"week_{week}"
    if cache_key in _summary_cache:
        return _summary_cache[cache_key]

    # Retrieve the slides content
    slides_content = retrieve_slides_content(week, persist_directory)

    if not slides_content.strip():
        result = {
            "success": False,
            "message": f"No slides content found for Week {week}",
            "summary": "",
            "week": week
        }
    else:
        # Generate summary from the slides content
        summary = generate_slides_summary(slides_content, week)

        result = {
            "success": True,
            "message": f"Summary generated successfully for Week {week}",
            "summary": summary,
            "week": week
        }

    # Cache the result
    _summary_cache[cache_key] = result
    return result

def clear_cache():
    """Clear all summary caches"""
    global _summary_cache
    _summary_cache = {}
    generate_slides_summary.cache_clear()
