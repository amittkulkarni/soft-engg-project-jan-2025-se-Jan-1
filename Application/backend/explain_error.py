from langchain_core.prompts import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from typing import Optional
from pydantic import SecretStr

def categorize_error(error_message: str):
    """Categorize the error to provide more specific explanations"""

    error_categories = {
        "SyntaxError": "syntax",
        "IndentationError": "syntax",
        "NameError": "variable",
        "TypeError": "type",
        "ValueError": "value",
        "IndexError": "index",
        "KeyError": "key",
        "AttributeError": "attribute",
        "ImportError": "import",
        "ModuleNotFoundError": "import",
        "ZeroDivisionError": "logic",
        "FileNotFoundError": "file",
        "PermissionError": "permission",
        "RuntimeError": "runtime",
        "RecursionError": "recursion"
    }

    for error_type, category in error_categories.items():
        if error_type in error_message:
            return category

    return "general"

def initialize_error_explainer(google_api_key: Optional[SecretStr] = None):
    """Initialize error explainer with examples for common error categories"""

    llm = ChatGoogleGenerativeAI(
        model="gemini-1.5-flash",
        google_api_key=google_api_key,
        temperature=0.2
    )

    # Create a more detailed prompt with examples
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

    # Create the chain
    error_explanation_chain = error_prompt | llm

    return error_explanation_chain

def explain_error(error_message: str, google_api_key: Optional[SecretStr] = None):
    """Enhanced error explanation with categorization"""

    # Categorize the error
    error_category = categorize_error(error_message)

    # Initialize the chain
    error_explanation_chain = initialize_error_explainer(google_api_key)

    # Process the error message with category
    try:
        explanation = error_explanation_chain.invoke({
            "error_message": error_message,
            "error_category": error_category
        })

        # Extract content based on response format
        if hasattr(explanation, 'content'):
            return explanation.content
        elif isinstance(explanation, str):
            return explanation
        else:
            return str(explanation)

    except Exception as e:
        return f"I couldn't analyze this error properly. Basic details: {error_message.split('Traceback')[0]}"


type_error = """
Traceback (most recent call last):
File "<stdin>", line 1, in <module>
File "<__array_function__ internals>", line 180, in mean
File "/usr/local/lib/python3.8/dist-packages/numpy/core/fromnumeric.py", line 3432, in mean
return _methods._mean(a, axis=axis, dtype=dtype, out=out, keepdims=keepdims)
File "/usr/local/lib/python3.8/dist-packages/numpy/core/_methods.py", line 153, in _mean
arr = asanyarray(a)
File "/usr/local/lib/python3.8/dist-packages/numpy/core/_asarray.py", line 83, in asanyarray
return array(a, dtype, copy=False, order=order, subok=True)
TypeError: int() argument must be a string, a bytes-like object or a number, not 'list'
            """

value_error = """
Traceback (most recent call last):
File "<stdin>", line 5, in <module>
File "/usr/local/lib/python3.8/dist-packages/sklearn/linear_model/_base.py", line 647, in fit
X, y = self._validate_data(X, y, accept_sparse=accept_sparse,
File "/usr/local/lib/python3.8/dist-packages/sklearn/base.py", line 581, in _validate_data
X, y = check_X_y(X, y, accept_sparse=accept_sparse,
File "/usr/local/lib/python3.8/dist-packages/sklearn/utils/validation.py", line 964, in check_X_y
X = check_array(X, accept_sparse=accept_sparse,
File "/usr/local/lib/python3.8/dist-packages/sklearn/utils/validation.py", line 746, in check_array
array = np.asarray(array, order=order, dtype=dtype)
ValueError: Found input variables with inconsistent numbers of samples: [5, 6]
            """

inf_error = """Traceback (most recent call last):
File "<stdin>", line 6, in <module>
File "/usr/local/lib/python3.8/dist-packages/sklearn/linear_model/_base.py", line 647, in fit
X, y = self._validate_data(X, y, accept_sparse=accept_sparse,
File "/usr/local/lib/python3.8/dist-packages/sklearn/base.py", line 581, in _validate_data
X, y = check_X_y(X, y, accept_sparse=accept_sparse,
File "/usr/local/lib/python3.8/dist-packages/sklearn/utils/validation.py", line 964, in check_X_y
X = check_array(X, accept_sparse=accept_sparse,
File "/usr/local/lib/python3.8/dist-packages/sklearn/utils/validation.py", line 746, in check_array
array = np.asarray(array, order=order, dtype=dtype)
File "/usr/local/lib/python3.8/dist-packages/numpy/core/_asarray.py", line 83, in asarray
return array(a, dtype, copy=False, order=order)
ValueError: Input contains NaN, infinity or a value too large for dtype('float64').
"""

from rich.console import Console
from rich.markdown import Markdown

def print_error_explanation(error_message, explanation):
    """Display error explanation with markdown formatting"""
    console = Console()

    # Print a divider and the original error summary
    console.print("\n[bold red]Error Message:[/bold red]", style="bold red")
    console.print(error_message.split("\n")[-1], style="red")

    # Print the explanation with markdown formatting
    console.print("\n[bold green]Explanation:[/bold green]", style="bold green")
    md = Markdown(explanation)
    console.print(md)

    # Print a divider for better readability
    console.print("\n" + "-" * 80 + "\n")

# Usage with your existing code
type_error_output = explain_error(type_error)
print_error_explanation(type_error, type_error_output)

value_error_output = explain_error(value_error)
print_error_explanation(value_error, value_error_output)

inf_error_output = explain_error(inf_error)
print_error_explanation(inf_error, inf_error_output)
