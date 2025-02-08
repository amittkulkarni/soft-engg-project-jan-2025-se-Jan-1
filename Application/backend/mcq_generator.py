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

# Initialize components
def initialize_rag_pipeline(google_api_key : SecretStr | None, persist_directory: str = "./chroma_db"):
    # Initialize Gemini
    llm = ChatGoogleGenerativeAI(
        model="gemini-2.0-flash-exp",
        google_api_key=google_api_key,
        temperature=0.7
    )

    # Initialize HuggingFace embeddings
    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )

    # Initialize or load Chroma DB
    vectorstore = Chroma(
        persist_directory=persist_directory,
        embedding_function=embeddings
    )

    return llm, vectorstore


# Initialize the text splitter
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,  # Maximum size of each chunk (in characters)
    chunk_overlap=200,  # Overlap between chunks to maintain context
    separators=["\n\n", "\n", " ", ""],  # Prioritize splitting at paragraphs, then sentences
)


def add_documents(vectorstore, documents, metadata=None):
    """
    Add documents to the vector store after splitting them into manageable chunks.
    documents: List of strings containing Python programming content.
    metadata: List of dictionaries with metadata for each document.
    """
    if metadata is None:
        metadata = [{"source": f"doc_{i}"} for i in range(len(documents))]

    # Split documents into smaller chunks
    split_docs = []
    for doc in documents:
        split_docs.extend(text_splitter.split_text(doc))

    # Add split documents to vector store
    vectorstore.add_texts(
        texts=split_docs,
        metadatas=metadata[:len(split_docs)]  # Adjust metadata to match split chunks
    )


# Function to generate MCQs
def generate_mcqs(llm, vectorstore, topic: str, num_questions: int = 10):

    # Search relevant documents
    search_results = vectorstore.similarity_search(
        topic,
        k=num_questions
    )

    # Create the MCQ generation prompt
    mcq_prompt = ChatPromptTemplate.from_messages([
        ("system", """You are an expert Machine Learning Programming instructor. Generate multiple choice questions
         based on the following context. Each question should have 4 options with only one correct answer.
         Make sure the questions test understanding rather than just memorization.

         Context: {context}

         Topic focus: {topic}
         Number of questions: {num_questions}"""),
        ("human", "Generate MCQ questions in JSON format with question text, options, correct answer, and explanation.")
    ])
    # Combine context from relevant documents
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