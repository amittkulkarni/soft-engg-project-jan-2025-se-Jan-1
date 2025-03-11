import os
import glob
import warnings
from typing import List

from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from langchain.docstore.document import Document
from langchain_google_genai import ChatGoogleGenerativeAI

warnings.filterwarnings("ignore", category=DeprecationWarning)

# ------------------- Set API Key for Google Gemini -------------------
os.environ["GOOGLE_API_KEY"] = "YOUR_GOOGLE_API_KEY"  # Replace with your actual key

# ------------------------------------------------------------------------------
# Helper: Load the slides vector store
# ------------------------------------------------------------------------------
def load_slides_vector_store(persist_directory: str = "slides_vector_store") -> Chroma:
    embedding_model = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
    vector_store = Chroma(
        collection_name="slides_embeddings",
        embedding_function=embedding_model,
        persist_directory=persist_directory
    )
    return vector_store

# ------------------------------------------------------------------------------
# Summarize text using Google Gemini
# ------------------------------------------------------------------------------
def summarize_text(text: str) -> str:
    chat_model = ChatGoogleGenerativeAI(model="gemini-1.5-flash")
    prompt = (
        "Summarize the following slides in 200-500 words, focusing on major topics and bullet points."
        "Return your answer in Markdown format with headings, bullet points, and numbered lists, tables if needed."
        "Start the first paragrapg after the heading with 'In week {week},' and start the concluding paragraph with 'In conclusion, week {week}'.\n"
        f"{text}"
    )
    response = chat_model.invoke(prompt)
    return response.content if hasattr(response, "content") else str(response)

# ------------------------------------------------------------------------------
# Summarize a Week's Slides
# ------------------------------------------------------------------------------
def summarize_week_slides(week: str, vector_store: Chroma) -> str:
    # Use a retriever with a metadata filter for "week"
    retriever = vector_store.as_retriever(
        search_kwargs={
            "filter": {"week": week},
            "k": 28  # get up to 100 chunks
        }
    )
    # We query with an empty string to retrieve all documents matching "week"
    docs = retriever.get_relevant_documents("")
    combined_text = "\n".join(doc.page_content for doc in docs)
    if combined_text.strip():
        return summarize_text(combined_text)
    else:
        return f"No content found for week {week} or no text extracted."

# ------------------------------------------------------------------------------
# MAIN: Example usage
# ------------------------------------------------------------------------------
def main():
    # 1) Load the cached slides vector store
    vector_store = load_slides_vector_store("slides_vector_store")

    # 2) Summarize Week 4 slides as an example
    week_str = "6"
    summary = summarize_week_slides(week_str, vector_store)

    print(f"------ WEEK {week_str} SUMMARY ----------------")
    print((summary))
    print("------------------------------------------------")

if __name__ == "__main__":
    main()
