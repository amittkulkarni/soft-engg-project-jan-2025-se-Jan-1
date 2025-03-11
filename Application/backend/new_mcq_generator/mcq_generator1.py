import json
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from pydantic import BaseModel, Field, SecretStr
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.text_splitter import RecursiveCharacterTextSplitter
from typing import List

# Define the schema for MCQ output
class MCQQuestion(BaseModel):
    question: str = Field(description="The question text")
    options: List[str] = Field(description="List of 4 options")
    correct_answer: str = Field(description="The correct answer")
    explanation: str = Field(description="Explanation of why the answer is correct")

class MCQSet(BaseModel):
    questions: List[MCQQuestion] = Field(description="List of MCQ questions")

# Initialize the pipeline components
def initialize_rag_pipeline(google_api_key: SecretStr | None, persist_directory: str = "mcq_vector_store"):
    # Initialize the Chat LLM (Google Generative AI in this example)
    llm = ChatGoogleGenerativeAI(
        model="gemini-2.0-flash-exp",
        google_api_key="YOUE_GOOGLE_API_KEY",
        temperature=0.7
    )

    # Initialize the embeddings from HuggingFace
    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )

    # Initialize or load the Chroma vector store
    vectorstore = Chroma(
        persist_directory=persist_directory,
        embedding_function=embeddings
    )

    return llm, vectorstore

# Initialize the text splitter to break down large texts
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,      # Maximum size of each chunk (in characters)
    chunk_overlap=200,    # Overlap between chunks to maintain context
    separators=["\n\n", "\n", " ", ""]
)

# Function to add documents into the vector store
def add_documents(vectorstore, documents, metadata=None):
    """
    Adds documents to the vector store after splitting them into manageable chunks.
    :param vectorstore: An instance of Chroma vector store.
    :param documents: List of strings containing text content.
    :param metadata: List of dictionaries with metadata for each document.
    """
    if metadata is None:
        metadata = [{"source": f"doc_{i}"} for i in range(len(documents))]

    split_docs = []
    for doc in documents:
        split_docs.extend(text_splitter.split_text(doc))

    # Add split documents to vector store
    vectorstore.add_texts(
        texts=split_docs,
        metadatas=metadata[:len(split_docs)]  # Adjust metadata to match split chunks
    )

# Function to generate MCQs using the chain
def generate_mcqs(llm, vectorstore, topic: str, num_questions: int = 10):
    """
    Generates multiple-choice questions for the given topic.
    :param llm: The initialized LLM.
    :param vectorstore: The vector store containing context documents.
    :param topic: Topic string to search for context.
    :param num_questions: Number of questions to generate.
    :return: MCQSet instance (or dict) containing questions.
    """
    # Search for relevant documents. If you are not using documents,
    # ensure that your vector store is already populated.
    search_results = vectorstore.similarity_search(
        topic,
        k=num_questions
    )

    # Create the MCQ generation prompt
    mcq_prompt = ChatPromptTemplate.from_messages([
        (
            "system", 
            """You are an expert Machine Learning Practice instructor. Generate multiple choice questions
            based on the following context. Each question should have 4 options with only one correct answer.
            Make sure the questions test understanding rather than just memorization.

            Context: {context}

            Topic focus: {topic}
            Number of questions: {num_questions}"""
        ),
        (
            "human", 
            "Generate MCQ questions in JSON format with question text, options, correct answer, and explanation."
        )
    ])
    
    # Combine context from relevant documents (if available)
    context = "\n".join([doc.page_content for doc in search_results])

    # Create chain for MCQ generation
    output_parser = JsonOutputParser(pydantic_object=MCQSet)
    chain = mcq_prompt | llm | output_parser

    # Generate MCQs
    response = chain.invoke({
        "context": context,
        "topic": topic,
        "num_questions": num_questions
    })

    return response

if __name__ == "__main__":
    google_api_key = "YOUE_GOOGLE_API_KEY"
    llm, vectorstore = initialize_rag_pipeline(google_api_key)
    
 
    topic = "Linear Regression"
    try:
        mcq_response = generate_mcqs(llm, vectorstore, topic, num_questions=5)
        if hasattr(mcq_response, "json"):
            print("MCQ Response:")
            print(mcq_response.json(indent=4))
        else:
            print("MCQ Response:")
            print(json.dumps(mcq_response, indent=4))
    except Exception as e:
        print("An error occurred:", e)
