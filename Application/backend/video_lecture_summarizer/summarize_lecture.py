import os
import glob
import warnings
from typing import List, Dict, Any, Optional

from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from langchain.docstore.document import Document
from langchain_google_genai import ChatGoogleGenerativeAI


# Suppress deprecation warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)

# ------------------- Set API Key for Google Gemini -------------------
os.environ["GOOGLE_API_KEY"] = "YOUR_GOOGLE_API_KEY"  # Replace with your actual API key

# ------------------------------------------------------------------------------
# Load Cached Vector Store
# ------------------------------------------------------------------------------
def load_vector_store(persist_directory: str = "vector_store1") -> Chroma:
    embedding_model = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
    vector_store = Chroma(collection_name="pdf_embeddings", embedding_function=embedding_model, persist_directory=persist_directory)
    return vector_store

# ------------------------------------------------------------------------------
# 1) SUMMARIZE CONTENT USING GOOGLE GENERATIVE AI (Google Gemini)
# ------------------------------------------------------------------------------
def summarize_text(text: str) -> str:
    chat_model = ChatGoogleGenerativeAI(
        model="gemini-1.5-flash"
    )

    prompt = (
        "You are a YouTube Video Lecture Summarizer. "
        "Summarize the following video lecture in 250-300 words. "
        "Your summary should be engaging and reflect a typical video lecture summary, highlighting the key points and main ideas in a natural, conversational tone. "
        "Do not mention that the summary is derived from a PDF document. Don't say 'This document...'"
        "Return your answer in Markdown format using headings, paragraphs, bullet points, and numbered lists, tables if necessary:"
        "After the heading, start your response with 'In this Lecture...', 'This Lecture...'"
        "Start the concluding paragraph with 'Prof. Ashish' or 'Ashish sir'.\n"
        f"{text}"
    )
    response = chat_model.invoke(prompt)
    return response.content if hasattr(response, "content") else str(response)

# ------------------------------------------------------------------------------
# 2) GET PDF SUMMARY USING THE CACHED VECTOR STORE
# ------------------------------------------------------------------------------
def get_pdf_summary(source_name: str, vector_store: Chroma) -> str:
    # Use the vector store's retriever with a metadata filter to fetch documents belonging to this PDF
    retriever = vector_store.as_retriever(search_kwargs={"filter": {"source": source_name}, "k": 100})
    # Query with an empty string to retrieve all matching documents
    docs = retriever.get_relevant_documents("")
    combined_text = "\n".join([doc.page_content for doc in docs])
    if combined_text.strip():
        return summarize_text(combined_text)
    else:
        return "No video lecture found for summarization."

# ------------------------------------------------------------------------------
# MAIN SCRIPT FOR SUMMARIZATION
# ------------------------------------------------------------------------------
def main():
    
    # Load the cached vector store
    vector_store = load_vector_store(persist_directory="vector_store")
    
    lec_num = "Week_1_Lecture_1" + ".pdf"
    
    summary = get_pdf_summary(lec_num, vector_store)
    print("-----------------------------SUMMARY -----------------------------")
    print((summary))
    print("------------------------------------------------------------------------")

if __name__ == "__main__":
    main()
