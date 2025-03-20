import os
from typing import List, Dict, Optional
from functools import lru_cache

from pydantic import BaseModel, Field
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.text_splitter import RecursiveCharacterTextSplitter

# Define the schema for MCQ output
class MCQQuestion(BaseModel):
    question: str = Field(description="The question text")
    options: List[str] = Field(description="List of 4 options")
    correct_answer: str = Field(description="The correct answer")

class MCQSet(BaseModel):
    questions: List[MCQQuestion] = Field(description="List of MCQ questions")

# Global variables for singleton pattern
_llm = None
_vectorstore = None
_embeddings = None

def get_api_key() -> str:
    """Get API key from environment variable"""
    api_key = "AIzaSyAmZBJC_WzWLlaUdfiM3GMu9UkCjAWOJ0o"
    if not api_key:
        raise ValueError("GOOGLE_API_KEY environment variable not set")
    return api_key

def get_embeddings():
    """Singleton for embeddings"""
    global _embeddings
    if _embeddings is None:
        _embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2"
        )
    return _embeddings

def get_llm():
    """Singleton for LLM"""
    global _llm
    if _llm is None:
        _llm = ChatGoogleGenerativeAI(
            model="gemini-1.5-flash",
            google_api_key=get_api_key(),
            temperature=0.7
        )
    return _llm

def get_vectorstore(persist_directory: str = "vector_store"):
    """Singleton for vector store"""
    global _vectorstore
    if _vectorstore is None:
        _vectorstore = Chroma(
            persist_directory=persist_directory,
            embedding_function=get_embeddings()
        )
    return _vectorstore

def initialize_components(persist_directory: str = "vector_store"):
    """Initialize all components at once"""
    return get_llm(), get_vectorstore(persist_directory)

def get_text_splitter():
    """Get text splitter with default configuration"""
    return RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        separators=["\n\n", "\n", " ", ""]
    )

def add_documents(documents: List[str], metadata: Optional[List[Dict]] = None, batch_size: int = 10):
    """
Add documents to the vector store in batches.

Args:
documents: List of text documents
metadata: Optional metadata for each document
batch_size: Number of documents to process at once
    """
    vectorstore = get_vectorstore()
    text_splitter = get_text_splitter()

    if metadata is None:
        metadata = [{"source": f"doc_{i}"} for i in range(len(documents))]

    # Process in batches
    for i in range(0, len(documents), batch_size):
        batch_docs = documents[i:i+batch_size]
        batch_meta = metadata[i:i+batch_size] if metadata else None

        # Split documents
        split_docs = []
        for doc in batch_docs:
            split_docs.extend(text_splitter.split_text(doc))

        # Adjust metadata to match split chunks
        batch_meta_adjusted = batch_meta[:len(split_docs)] if batch_meta else None

        # Add to vector store
        vectorstore.add_texts(
            texts=split_docs,
            metadatas=batch_meta_adjusted
        )

    return {"added": len(documents), "chunks": len(split_docs)}

@lru_cache(maxsize=50)
def cached_generate_mcqs(topic: str, num_questions: int):
    """Cached version of generate_mcqs for frequently requested topics"""
    llm = get_llm()
    vectorstore = get_vectorstore()
    return _generate_mcqs_impl(llm, vectorstore, topic, num_questions)


def generate_topic_mcqs(topic: str, num_questions: int = 5) -> MCQSet:

    """
Public interface to generate MCQs.
Delegates to cached version if appropriate.

Args:
topic: The ML topic to generate questions about
num_questions: Number of questions to generate

Returns:
MCQSet object containing the generated questions
    """
    # For very specific topics or many questions, bypass cache
    if num_questions > 10 or len(topic.split()) > 5:
        llm = get_llm()
        vectorstore = get_vectorstore()
        return _generate_mcqs_impl(llm, vectorstore, topic, num_questions)

    # Use cached version for common requests
    return cached_generate_mcqs(topic, num_questions)

def _generate_mcqs_impl(llm, vectorstore, topic: str, num_questions: int) -> MCQSet:
    """
Implementation of MCQ generation.

Args:
llm: LLM instance
vectorstore: Vector store with context documents
topic: Topic to generate questions about
num_questions: Number of questions to generate

Returns:
MCQSet containing the generated questions
    """
    # Search for relevant documents
    search_results = vectorstore.similarity_search(
        topic,
        k=min(num_questions * 2, 20)  # Get more context for better questions
    )

    mcq_prompt = ChatPromptTemplate.from_messages([
        (
            "system",
            """You are an expert Machine Learning and Programming instructor. Generate multiple choice questions
based on the following context. Each question should have 4 options with only one correct answer.

Context: {context}

Topic focus: {topic}
Number of questions: {num_questions}

## INSTRUCTIONS:
- Create diverse questions that test deep understanding of Machine Learning concepts
- Feel free to include code snippets directly within question text where appropriate
- Not every question needs code - include a natural mix based on what's best for the topic
- When using code, ensure it's relevant to the topic and properly formatted using ```python``` blocks
- Each question must have exactly 4 options labeled A, B, C, D
- Make questions challenging but fair, testing understanding rather than memorization
- Ensure any code examples are realistic, error-free, and demonstrate actual ML practices

## QUESTION EXAMPLES:
1. Conceptual: "What is the primary advantage of using gradient boosting over random forests?"
2. Code-based: "Consider the following scikit-learn code:
```python
from sklearn.ensemble import RandomForestClassifier
model = RandomForestClassifier(n_estimators=100, max_depth=5)
model.fit(X_train, y_train)
```
What would be the effect of increasing max_depth to 15?"

## FORMAT REQUIREMENTS:
- Format code within question text using markdown code blocks with `````` tags
- Label options as A, B, C, D (include the letter in the option text)
- Format your response as valid JSON matching the specified schema
- Vary question types: conceptual understanding, code interpretation, practical application, etc.

## JSON SCHEMA:
{{
"questions": [
{{
"question": "Question text here, potentially including code snippets",
"options": ["A. Option 1", "B. Option 2", "C. Option 3", "D. Option 4"],
"correct_answer": "A. Option 1",
}}
]
}}

            Generate questions that represent real-world ML knowledge and skills."""
        ),
        (
            "human",
            "Generate MCQ questions in JSON format. Include some questions with code snippets where appropriate."
        )
    ])

    # Combine context from relevant documents
    context = "\n".join([doc.page_content for doc in search_results])

    # If context is too short, generate using just the topic
    if len(context) < 200:
        context = f"Generate questions about {topic} in Machine Learning."

    # Create chain for MCQ generation
    output_parser = JsonOutputParser(pydantic_object=MCQSet)
    chain = mcq_prompt | llm | output_parser

    # Generate MCQs
    try:
        response = chain.invoke({
            "context": context,
            "topic": topic,
            "num_questions": num_questions
        })
        return response
    except Exception as e:
        # Fallback with simpler context if parsing fails
        try:
            response = chain.invoke({
                "context": f"Generate questions about {topic} in Machine Learning.",
                "topic": topic,
                "num_questions": num_questions
            })
            return response
        except Exception as nested_e:
            raise Exception(f"MCQ generation failed: {str(nested_e)}. Original error: {str(e)}")
