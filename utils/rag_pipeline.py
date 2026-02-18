import os
from pypdf import PdfReader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from sentence_transformers import SentenceTransformer
import streamlit as st
import re
from typing import List, Tuple, Optional
from .neo4j_manager import Neo4jManager
from .entity_extractor import get_entity_extractor

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

def chunk_text(text, chunk_size=1000, chunk_overlap=200):
    """
    Splits text into chunks.
    """
    if not text:
        return []
    
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        length_function=len
    )
    return splitter.split_text(text)

def generate_embeddings(chunks):
    """
    Generates embeddings for a list of text chunks.
    """
    try:
        model = get_embedding_model()
        return model.encode(chunks).tolist()
    except Exception as e:
        print(f"Embedding Error: {e}")
        return []

def detect_document_type(text: str) -> str:
    """
    Detect document type from content using keywords.
    """
    text_lower = text.lower()
    
    # Keywords for different document types
    if any(keyword in text_lower for keyword in ['clinical trial', 'protocol', 'nct', 'phase 1', 'phase 2', 'phase 3', 'study design']):
        if 'results' in text_lower or 'outcome' in text_lower:
            return 'clinical_trial_results'
        return 'clinical_trial_protocol'
    
    if any(keyword in text_lower for keyword in ['mechanism of action', 'pharmacology', 'pharmacokinetics', 'drug mechanism']):
        return 'drug_mechanism'
    
    if any(keyword in text_lower for keyword in ['abstract', 'introduction', 'methods', 'discussion', 'references']):
        return 'research_paper'
    
    if any(keyword in text_lower for keyword in ['indication', 'dosage', 'administration', 'contraindication', 'warnings']):
        return 'drug_label'
    
    return 'unknown'

def ingest_document(file, filename: str) -> Tuple[bool, str]:
    """
    Full pipeline: Parse -> Chunk -> Embed -> Extract Entities -> Neo4j
    """
    try:
        # 1. Parse
        text = process_pdf(file)
        if not text:
            return False, "Could not extract text from PDF. The file might be empty or scanned (image-only)."
            
        # 2. Detect document type
        doc_type = detect_document_type(text)
        
        # 3. Chunk
        chunks = chunk_text(text)
        if not chunks:
            return False, "Text extraction returned empty content after processing."
        
        # 4. Embed
        embeddings = generate_embeddings(chunks)
        
        # 5. Extract entities
        extractor = get_entity_extractor()
        entities_per_chunk = extractor.extract_entities_batch(chunks)
        
        # 6. Neo4j
        neo = Neo4jManager()
        neo.create_vector_index()  # Ensure index exists
        neo.add_document(filename, chunks, embeddings, doc_type, entities_per_chunk)
        neo.close()
        
        # Count entities
        total_entities = sum(len(extractor.get_entity_set(e)) for e in entities_per_chunk)
        
        return True, f"Successfully processed {filename} ({doc_type}). Created {len(chunks)} chunks with {total_entities} unique entities."
    except Exception as e:
        return False, f"Ingestion Error: {str(e)}"

def ingest_documents_batch(files: List, filenames: List[str]) -> Tuple[bool, str]:
    """
    Process multiple documents and create cross-document relationships.
    
    Args:
        files: List of uploaded file objects
        filenames: List of filenames
        
    Returns:
        Tuple of (success, message)
    """
    if not files or not filenames:
        return False, "No files provided"
    
    if len(files) != len(filenames):
        return False, "File count mismatch"
    
    success_count = 0
    errors = []
    
    # Ingest each document
    for file, filename in zip(files, filenames):
        success, message = ingest_document(file, filename)
        if success:
            success_count += 1
        else:
            errors.append(f"{filename}: {message}")
    
    # Create cross-document relationships if multiple docs uploaded successfully
    if success_count > 1:
        try:
            neo = Neo4jManager()
            rel_count = neo.create_cross_document_links(similarity_threshold=0.75)
            neo.close()
            relationship_msg = f"Created {rel_count} cross-document relationships."
        except Exception as e:
            relationship_msg = f"Warning: Could not create cross-document links: {e}"
    else:
        relationship_msg = ""
    
    # Build result message
    if success_count == len(files):
        return True, f"Successfully processed all {success_count} documents. {relationship_msg}"
    elif success_count > 0:
        error_details = "\n".join(errors)
        return True, f"Processed {success_count}/{len(files)} documents. {relationship_msg}\n\nErrors:\n{error_details}"
    else:
        error_details = "\n".join(errors)
        return False, f"Failed to process all documents:\n{error_details}"

def get_rag_context(query: str, top_k: int = 15, max_docs: int = 5) -> str:
    """
    Retrieves context for a query using multi-document retrieval.
    
    Args:
        query: User question
        top_k: Number of chunks to retrieve
        max_docs: Maximum number of source documents
        
    Returns:
        Context string with source citations
    """
    try:
        model = get_embedding_model()
        query_embedding = model.encode([query])[0].tolist()
        
        neo = Neo4jManager()
        context = neo.get_multi_doc_context(query_embedding, top_k=top_k, max_docs=max_docs)
        neo.close()
        
        return context
    except Exception as e:
        print(f"RAG Error: {e}")
        return ""

def get_documents_list() -> List[dict]:
    """Get list of all uploaded documents"""
    try:
        neo = Neo4jManager()
        docs = neo.get_documents()
        neo.close()
        return docs
    except Exception as e:
        print(f"Error fetching documents: {e}")
        return []

def delete_document(filename: str) -> Tuple[bool, str]:
    """Delete a specific document"""
    try:
        neo = Neo4jManager()
        neo.delete_document(filename)
        neo.close()
        return True, f"Successfully deleted {filename}"
    except Exception as e:
        return False, f"Error deleting document: {e}"

def clear_all_documents() -> Tuple[bool, str]:
    """Clear all documents from Neo4j"""
    try:
        neo = Neo4jManager()
        neo.clear_all_data()
        neo.close()
        return True, "Successfully cleared all documents"
    except Exception as e:
        return False, f"Error clearing documents: {e}"
