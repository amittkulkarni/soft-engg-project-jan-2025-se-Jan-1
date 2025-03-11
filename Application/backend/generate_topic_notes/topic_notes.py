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
os.environ["GOOGLE_API_KEY"] = "YOUR_GOOGLE_API_KEY"  # Replace with your actual API key

# ------------------------------------------------------------------------------
# Helper: Load the notes vector store (which uses base names in metadata)
# ------------------------------------------------------------------------------
def load_notes_vector_store(persist_directory: str = "notes_vector_store") -> Chroma:
    embedding_model = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
    vector_store = Chroma(
        collection_name="notes_embeddings",
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
        "Create concise topic-specific notes in 200-400 words."
        "Conclude with a concluding paragraph, such as 'These are the \"{topic}\" notes for you' or 'These \"{topic}\" notes will help you prepare well'.\n"
        "Use headings, bullet points, short paragraphs, and a table if needed."
        f"{text}"
        )
        
    response = chat_model.invoke(prompt)
    return response.content if hasattr(response, "content") else str(response)

# ------------------------------------------------------------------------------
# ------------------------------------------------------------------------------
def generate_topic_notes(topic: str, vector_store: Chroma) -> str:
    # Retrieve up to 20 relevant chunks from the entire corpus (slides + book)
    retriever = vector_store.as_retriever(search_kwargs={"k": 20})
    docs = retriever.get_relevant_documents(topic)
    combined_text = "\n".join([doc.page_content for doc in docs])
    if combined_text.strip():
        return summarize_text(combined_text)
    else:
        return f"No relevant notes found for the topic '{topic}'."

# ------------------------------------------------------------------------------
# MAIN: Example usage
# ------------------------------------------------------------------------------
def main():
    vector_store = load_notes_vector_store("notes_vector_store")
    
    # For demonstration, let's define a topic
    topic = "Naive Bayes"
    print(f"Generating notes for topic: {topic}")
    notes = generate_topic_notes(topic, vector_store)
    
    print("--------------------- TOPIC NOTES ----------------------")
    print(notes)
    print("--------------------------------------------------------")

if __name__ == "__main__":
    main()
