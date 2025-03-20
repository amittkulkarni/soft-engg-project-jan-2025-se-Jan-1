import os
from typing import Dict
from functools import lru_cache

from langchain_core.prompts import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI

# Global singleton for LLM
_llm = None

def get_api_key() -> str:
    """Get API key from environment variable"""
<<<<<<< HEAD
    api_key = "AIzaSyAmZBJC_WzWLlaUdfiM3GMu9UkCjAWOJ0o"
=======
    #api_key = os.environ.get("GOOGLE_API_KEY")
    api_key = "AIzaSyCV5i-u0oROux-Wt0TMqiRivVD6H0rGbjc"
>>>>>>> b8736b5e13c4bc0d1ebe08f35c530d382a48fb64
    if not api_key:
        raise ValueError("GOOGLE_API_KEY environment variable not set")
    return api_key

def get_llm():
    """Singleton pattern for LLM to avoid multiple initializations"""
    global _llm
    if _llm is None:
        _llm = ChatGoogleGenerativeAI(
            model="gemini-1.5-flash",
            google_api_key=get_api_key(),
            temperature=0.2
        )
    return _llm

# Error categorization with expanded categories
ERROR_CATEGORIES: Dict[str, str] = {
    # Syntax errors
    "SyntaxError": "syntax",
    "IndentationError": "syntax",
    "TabError": "syntax",

    # Variable errors
    "NameError": "variable",
    "UnboundLocalError": "variable",

    # Type errors
    "TypeError": "type",
    "ValueError": "value",

    # Collection errors
    "IndexError": "index",
    "KeyError": "key",
    "AttributeError": "attribute",

    # Module errors
    "ImportError": "import",
    "ModuleNotFoundError": "import",

    # Logic errors
    "ZeroDivisionError": "logic",
    "OverflowError": "logic",
    "ArithmeticError": "logic",

    # File errors
    "FileNotFoundError": "file",
    "PermissionError": "permission",
    "IOError": "file",

    # Other errors
    "RuntimeError": "runtime",
    "RecursionError": "recursion",
    "MemoryError": "memory",
    "TimeoutError": "timeout",

    # ML-specific errors
    "ValueError: Input contains NaN": "data_quality",
    "ValueError: Found input variables with inconsistent": "data_shape",
    "could not convert string to float": "data_type",
    "not fitted yet": "model_state",
    "not callable": "function_call"
}

def categorize_error(error_message: str) -> str:
    """
    Categorize the error based on its type to provide more specific explanations.

    Args:
        error_message: The complete error message to analyze

    Returns:
        A category string representing the type of error
    """
    # First check for specific ML errors that might be substrings
    for error_pattern, category in ERROR_CATEGORIES.items():
        if ":" not in error_pattern and error_pattern in error_message:
            return category

    # Then check for standard Python error types
    for error_type, category in ERROR_CATEGORIES.items():
        if ":" in error_type and error_type.split(":")[0] in error_message:
            return category

    # Default category
    return "general"

def get_error_explanation_chain():
    """Create and return the error explanation chain"""
    llm = get_llm()

    error_prompt = ChatPromptTemplate.from_messages([
        ("system", """You are an expert programming instructor specializing in explaining Python errors to beginners.
Your task is to explain the following error message in simple, human-readable terms.

The error category is: {error_category}

For your explanation:
1. Start with a one-sentence summary of what went wrong
2. Explain why this error occurs in simple language
3. Suggest 1-2 specific ways to fix the issue
4. Include a brief example if helpful

         Keep your explanation under 150 words, friendly, and educational."""),
        ("human", "Error message: {error_message}")
    ])

    return error_prompt | llm

@lru_cache(maxsize=50)
def cached_explain_error(error_message: str, error_category: str):
    """
Cached version of error explanation for common errors.

Args:
error_message: The error message to explain
error_category: The category of the error

Returns:
A human-readable explanation of the error
    """
    # Create the chain
    error_explanation_chain = get_error_explanation_chain()

    # Process the error with the chain
    response = error_explanation_chain.invoke({
        "error_message": error_message,
        "error_category": error_category
    })

    # Extract content based on response format
    if hasattr(response, 'content'):
        return response.content
    elif isinstance(response, str):
        return response
    else:
        return str(response)

def explain_error(error_message: str) -> str:
    """
Explains a Python error message in human-readable terms.

Args:
error_message: The error message to explain

Returns:
A human-readable explanation of the error
    """
    try:
        # Extract just the actual error line if it's a full traceback
        if "Traceback" in error_message:
            error_lines = error_message.strip().split('\n')
            actual_error = error_lines[-1] if error_lines else error_message
        else:
            actual_error = error_message

        # Categorize the error
        error_category = categorize_error(error_message)

        # Use the cached version for efficiency
        return cached_explain_error(actual_error, error_category)

    except Exception as e:
        # Graceful fallback if something goes wrong
        return f"I couldn't analyze this error properly. Basic details: {error_message.split('Traceback')[0]}"