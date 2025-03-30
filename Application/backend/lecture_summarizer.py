import os
import warnings
from typing import Dict, Any, List
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

def get_lecture_filename(week: int, lecture: int) -> str:
    """Generate the standardized filename for a lecture transcript"""
    return f"Week_{week}_Lecture_{lecture}.pdf"

def get_available_lectures(persist_directory: str = "vector_store") -> List[Dict[str, int]]:
    """Get list of all available lectures in the vector store"""
    vector_store = get_vector_store(persist_directory)

    # Get all documents to extract metadata
    results = vector_store.get()

    # Extract unique lecture names from metadata
    lectures = set()
    if results and 'metadatas' in results:
        for metadata in results['metadatas']:
            if metadata and 'source' in metadata:
                source = metadata['source']
                if source.startswith("Week_") and source.endswith(".pdf"):
                    lectures.add(source)

    # Parse week and lecture numbers
    lecture_info = []
    for lecture in sorted(lectures):
        try:
            # Extract week and lecture numbers from the filename
            parts = lecture.replace('.pdf', '').split('_')
            if len(parts) == 4 and parts[0] == 'Week' and parts[2] == 'Lecture':
                lecture_info.append({
                    'week': int(parts[1]),
                    'lecture': int(parts[3]),
                    'filename': lecture
                })
        except (ValueError, IndexError):
            continue

    return lecture_info

@lru_cache(maxsize=50)
def generate_lecture_summary(text: str) -> str:
    """Generate a summary of the lecture text using Google Gemini"""
    llm = get_llm()

    # Use regular string with f-string for the text parameter
    prompt = (
        "You are a YouTube Video Lecture Summarizer specializing in academic content. "
        "Create a concise, well-structured summary (250-300 words) of the following lecture. "

        "## Formatting Guidelines:\n"
        "- Use hierarchical headings starting with level 2 (##) for the lecture title and level 3 (###) for subsections\n"
        "- Include appropriate whitespace between sections for readability but not too many\n"
        "- Add mathematical formulas using LaTeX notation (\\( \\) for inline, \\[ \\] for display)\n"
        "- Present code examples in language-specific code blocks using proper syntax:\n"
        "```\n"
        "def example_function():\n"
        "    return \"This is sample code\"\n"
        "```\n"
        "- Use tables for comparing concepts, like this:\n"
        "| Algorithm | Time Complexity | Space Complexity |\n"
        "| --------- | --------------- | ---------------- |\n"
        "| Quicksort | O(n log n)      | O(log n)         |\n"
        "- Use bullet points for key concepts and numbered lists for sequential steps\n"
        "- Highlight important definitions or theorems in blockquotes (> theorem statement)\n"

        "## Content Structure:\n"
        "1. Begin with a level 2 heading that captures the lecture title/topic\n"
        "2. Start the first paragraph with 'In this lecture...' or 'This lecture...'\n"
        "3. Organize the main body with level 3 headings for distinct subtopics\n"
        "4. Include any important definitions, theorems, or algorithms in highlighted blocks\n"
        "5. Conclude with a paragraph starting with 'Prof. Ashish'\n"

        "## Example Format Structure:\n"
        "## [Lecture Title]: [Subtopic]\n\n"
        "In this lecture, Professor Ashish introduces the fundamental concepts of [topic]...\n\n"
        "### Key Concept 1\n"
        "The main points about this concept include...\n\n"
        "> **Definition:** A formal definition of an important term goes here.\n\n"

        "Ensure your summary is engaging and conversational while maintaining academic precision. "
        "Never mention that this content came from a PDF document. "
        "When presenting technical concepts, balance clarity with technical accuracy.\n\n"

        f"Please summarize the following lecture:\n\n{text}"
    )

    try:
        response = llm.invoke(prompt)
        return response.content if hasattr(response, "content") else str(response)
    except Exception as e:
        return f"Error generating summary: {str(e)}"

def retrieve_transcript(lecture_filename: str, persist_directory: str = "vector_store") -> str:
    """Retrieve the transcript content for a specific lecture"""
    vector_store = get_vector_store(persist_directory)

    # Since there's only one transcript per lecture, use exact matching
    retriever = vector_store.as_retriever(
        search_kwargs={"filter": {"source": lecture_filename}, "k": 10}
    )

    docs = retriever.get_relevant_documents("")

    if not docs:
        return ""

    # Combine all chunks from the transcript
    transcript_text = "\n".join([doc.page_content for doc in docs])
    return transcript_text

def summarize_lecture(week: int, lecture: int, persist_directory: str = "vector_store") -> Dict[str, Any]:
    """
Generate a summary for a specific lecture.

Args:
week: Week number (integer)
lecture: Lecture number (integer)
persist_directory: Directory of the vector store

Returns:
Dictionary with summary and metadata
    """
    global _summary_cache

    # Check if we already have this summary cached
    cache_key = f"{week}_{lecture}"
    if cache_key in _summary_cache:
        return _summary_cache[cache_key]

    # Get the lecture filename
    lecture_filename = get_lecture_filename(week, lecture)

    # Retrieve the transcript
    transcript = retrieve_transcript(lecture_filename, persist_directory)

    if not transcript:
        result = {
            "success": False,
            "message": f"No transcript found for Week {week}, Lecture {lecture}",
            "summary": "",
            "week": week,
            "lecture": lecture
        }
    else:
        # Generate summary from the transcript
        summary = generate_lecture_summary(transcript)

        result = {
            "success": True,
            "message": "Summary generated successfully",
            "summary": summary,
            "week": week,
            "lecture": lecture
        }

    # Cache the result
    _summary_cache[cache_key] = result
    return result

def clear_cache():
    """Clear all summary caches"""
    global _summary_cache
    _summary_cache = {}
    generate_lecture_summary.cache_clear()
