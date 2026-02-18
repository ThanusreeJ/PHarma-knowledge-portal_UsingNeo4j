"""
Company Knowledge Page (Multi-Document RAG with Neo4j)
"""
import streamlit as st
import pandas as pd
from utils.rag_pipeline import (
    ingest_document, ingest_documents_batch, get_rag_context,
    get_documents_list, delete_document, clear_all_documents
)
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
import config


def show():
    st.markdown('<h2 class="gradient-header">🏢 Multi-Document Knowledge Base</h2>', unsafe_allow_html=True)
    st.markdown("Upload multiple pharmaceutical documents and ask  questions across all of them using Neo4j graph RAG.")

    # Sidebar for upload and document management
    with st.sidebar:
        st.markdown("### 📂 Document Upload")
        
        uploaded_files = st.file_uploader(
            "Upload PDF Documents", 
            type=['pdf'],
            accept_multiple_files=True,
            help="Upload one or more PDF documents to add to your knowledge base"
        )
        
        if uploaded_files and st.button("📥 Process Documents", use_container_width=True):
            with st.spinner(f"Processing {len(uploaded_files)} document(s)... This may take 30-90 seconds."):
                if len(uploaded_files) == 1:
                    success, message = ingest_document(uploaded_files[0], uploaded_files[0].name)
                else:
                    filenames = [f.name for f in uploaded_files]
                    success, message = ingest_documents_batch(uploaded_files, filenames)
                
                if success:
                    st.success(message)
                else:
                    st.error(message)
        
        st.markdown("---")
        st.markdown("### 📚 Document Library")
        
        # Get and display documents
        docs = get_documents_list()
        
        if docs:
            st.info(f"**Total Documents:** {len(docs)}")
            
            # Document table with selection
            df = pd.DataFrame(docs)
            if 'upload_date' in df.columns:
                # Convert Neo4j DateTime to string (it's already in ISO format)
                df['upload_date'] = df['upload_date'].astype(str).str[:16].str.replace('T', ' ')
            
            # Display documents
            for idx, doc in enumerate(docs):
                with st.expander(f"📄 {doc.get('filename', 'Unknown')}"):
                    st.write(f"**Type:** {doc.get('doc_type', 'unknown')}")
                    st.write(f"**Uploaded:** {doc.get('upload_date', 'N/A')}")
                    st.write(f"**Chunks:** {doc.get('chunk_count', 0)}")
                    
                    if st.button(f"🗑️ Delete", key=f"del_{idx}", use_container_width=True):
                        success, msg = delete_document(doc['filename'])
                        if success:
                            st.success(msg)
                            st.rerun()
                        else:
                            st.error(msg)
            
            st.markdown("---")
            
            if st.button("🗑️ Clear All Documents", use_container_width=True, type="secondary"):
                if st.session_state.get('confirm_clear', False):
                    success, msg = clear_all_documents()
                    if success:
                        st.success(msg)
                        st.session_state.confirm_clear = False
                        st.rerun()
                    else:
                        st.error(msg)
                else:
                    st.session_state.confirm_clear = True
                    st.warning("⚠️ Click again to confirm deletion of ALL documents")
        else:
            st.info("No documents uploaded yet. Upload PDFs above to get started!")
        
        # Neo4j Browser Link
        st.markdown("---")
        st.markdown("### 🔍 Explore Graph")
        st.markdown("""
        Open [Neo4j Browser](http://localhost:7474) to visualize your knowledge graph.
        
        **Recommended Queries:**
        ```cypher
        // View all documents
        MATCH (d:Document) RETURN d
        
        // View entities
        MATCH (e:Entity) RETURN e LIMIT 25
        
        // Cross-doc relationships
        MATCH (c1:Chunk)-[s:SIMILAR_TO]->(c2:Chunk)
        RETURN c1, s, c2 LIMIT 10
        ```
        """)

    # Main chat interface
    st.markdown("---")
    
    # Check if context exists
    if not docs:
        st.info("👈 Please upload documents in the sidebar to start chatting.")
        st.markdown("""
        ### 💡 Multi-Document RAG Capabilities
        
        Once you upload documents, you can:
        - **Ask questions across multiple documents** - "Compare the results to the protocol"
        - **Find cross-references** - "What is ARIA-E and what was its incidence?"
        - **Synthesize information** - "Explain the mechanism and how it relates to the trial results"
        
        The system will automatically find relevant passages from **all uploaded documents** and synthesize the answer.
        """)
        return

    # Initialize chat history
    if "rag_chat_history" not in st.session_state:
        st.session_state.rag_chat_history = []

    # Display history
    for message in st.session_state.rag_chat_history:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Input
    if prompt := st.chat_input("Ask questions across all your documents..."):
        # User message
        st.session_state.rag_chat_history.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # AI Response
        with st.chat_message("assistant"):
            with st.spinner("Searching across all documents..."):
                try:
                    llm = ChatGroq(
                        groq_api_key=config.GROQ_API_KEY,
                        model_name="llama-3.3-70b-versatile",
                        temperature=0.3
                    )
                    
                    # Get multi-document context
                    context = get_rag_context(prompt, top_k=15, max_docs=5)
                    
                    if not context:
                        st.warning("No relevant information found in the documents.")
                        answer = "I couldn't find relevant information in the uploaded documents to answer your question."
                    else:
                        # Enhanced prompt for multi-doc synthesis
                        prompt_template = ChatPromptTemplate.from_template(
                            """You are a pharmaceutical knowledge assistant analyzing multiple documents.
                            
Answer the question based ONLY on the provided context from the documents.
If the answer requires information from multiple sources, synthesize them clearly.
Always cite which document(s) you're referencing.
If the answer is not in the context, say so - do not hallucinate.

<context>
{context}
</context>

Question: {input}

Provide a clear, well-structured answer with source citations."""
                        )
                        
                        rag_chain = (
                            {"context": lambda x: context, "input": RunnablePassthrough()}
                            | prompt_template
                            | llm
                            | StrOutputParser()
                        )
                        
                        answer = rag_chain.invoke(prompt)
                    
                    st.markdown(answer)
                    st.session_state.rag_chat_history.append({"role": "assistant", "content": answer})
                    
                except Exception as e:
                    error_msg = f"Error generating response: {str(e)}"
                    st.error(error_msg)
                    st.session_state.rag_chat_history.append({"role": "assistant", "content": error_msg})
    
    # Clear chat button in main area
    if st.session_state.rag_chat_history:
        st.markdown("---")
        if st.button("🗑️ Clear Chat History"):
            st.session_state.rag_chat_history = []
            st.rerun()
