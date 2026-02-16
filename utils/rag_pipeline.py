import os
from pypdf import PdfReader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from sentence_transformers import SentenceTransformer
import streamlit as st
from .neo4j_manager import Neo4jManager

# Initialize model once
@st.cache_resource
def get_embedding_model():
    return SentenceTransformer('all-MiniLM-L6-v2')

def process_pdf(file):
    """
    Extracts text from a PDF file interactively uploaded in Streamlit.
    """
    try:
        file.seek(0)  # Reset pointer
        reader = PdfReader(file)
        text = ""
        for page in reader.pages:
            text += page.extract_text() or ""
        return text
    except Exception as e:
        print(f"Error reading PDF: {e}")
        return ""

# ... existing code ...

def ingest_document(file, filename):
    """
    Full pipeline: Parse -> Chunk -> Embed -> Neo4j
    """
    try:
        # 1. Parse
        text = process_pdf(file)
        if not text:
            return False, "Could not extract text from PDF. The file might be empty or scanned (image-only)."
            
        # 2. Chunk
        chunks = chunk_text(text)
        if not chunks:
            return False, "Text extraction returned empty content after processing."
        
        # 3. Embed
        embeddings = generate_embeddings(chunks)
        
        # 4. Neo4j
        neo = Neo4jManager()
        neo.create_vector_index() # Ensure index exists
        neo.add_document(filename, chunks, embeddings)
        neo.close()
        
        return True, f"Successfully processed {filename}. Created {len(chunks)} chunks in the graph."
    except Exception as e:
        return False, f"Ingestion Error: {str(e)}"

def get_rag_context(query):
    """
    Retrieves context for a query.
    """
    try:
        model = get_embedding_model()
        query_embedding = model.encode([query])[0].tolist()
        
        neo = Neo4jManager()
        context = neo.get_context(query_embedding)
        neo.close()
        
        return context
    except Exception as e:
        print(f"RAG Error: {e}")
        return ""
