
try:
    import streamlit as st
    import tempfile
    import os
    from langchain_community.document_loaders import PyPDFLoader, TextLoader
    print("langchain_community.document_loaders: OK")
    from langchain_text_splitters import RecursiveCharacterTextSplitter
    print("langchain_text_splitters: OK")
    from langchain_community.vectorstores import FAISS
    print("langchain_community.vectorstores: OK")
    from langchain_community.embeddings import HuggingFaceEmbeddings
    print("langchain_community.embeddings: OK")
    from langchain_groq import ChatGroq
    print("langchain_groq: OK")
    from langchain.chains.combine_documents import create_stuff_documents_chain
    print("langchain.chains.combine_documents: OK")
    from langchain_core.prompts import ChatPromptTemplate
    print("langchain_core.prompts: OK")
    from langchain.chains import create_retrieval_chain
    print("langchain.chains: OK")
except ImportError as e:
    print(f"FAILED: {e}")
