"""
AI Chatbot Page with Multi-Document RAG
"""
import streamlit as st
from groq import Groq
import config
from utils.rag_pipeline import get_rag_context, get_documents_list


def get_groq_response(question: str, chat_history: list, context: str = "") -> str:
    """Get response from Groq AI with optional RAG context"""
    try:
        if not config.GROQ_API_KEY:
            return "⚠️ Please set your GROQ_API_KEY in the .env file to use the chatbot.\\n\\nGet a free API key at: https://console.groq.com/"
        
        client = Groq(api_key=config.GROQ_API_KEY)
        
        # System prompt for pharma domain
        system_prompt = """You are an expert pharmaceutical knowledge assistant with deep expertise in clinical trials, drug mechanisms, and regulatory affairs.

INSTRUCTIONS:
1. Answer based ONLY on the provided context if available. Never hallucinate.
2. Always cite the exact source document in brackets like [document_name.pdf] after each fact.
3. Use rich markdown formatting: headers (##, ###), bullet points, **bold**, tables, and emojis.
4. For COMPARISON questions (protocol vs results, expected vs actual):
   - Use a markdown table to show the comparison side-by-side
   - Clearly label which document each value comes from
   - Add a "🔎 Comparison" section with your judgment
5. For MECHANISM questions: use numbered steps or a flow (→) to show causality
6. For SAFETY questions: separate by severity levels using bullet points
7. Always end with a clear conclusion or summary section
8. Use emojis: 📘 Protocol/Plan, 📊 Results/Data, 🔬 Mechanism, ⚠️ Safety, 🏁 Conclusion, 🔎 Comparison

Provide accurate, helpful responses. Keep responses concise but informative.
Always remind users to consult healthcare professionals for medical advice."""
        
        # Build messages
        messages = [{"role": "system", "content": system_prompt}]
        
        # Add chat history
        for msg in chat_history[-10:]:  # Last 10 messages for context
            messages.append(msg)
        
        # Add current question with context if available
        if context:
            user_content = f"""Based on the following context from uploaded documents:\n\n{context}\n\n---\n\nQuestion: {question}"""
        else:
            user_content = question
        
        messages.append({"role": "user", "content": user_content})
        
        # Get response
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=messages,
            temperature=0.7 if not context else 0.3,  # Lower temp for RAG
            max_tokens=1024
        )
        
        return response.choices[0].message.content
        
    except Exception as e:
        return f"❌ Error: {str(e)}\\n\\nPlease check your GROQ_API_KEY configuration."


def show():
    st.markdown('<h2 class="gradient-header">💬 Pharma Knowledge Chatbot</h2>', unsafe_allow_html=True)
    st.markdown("Ask questions about drugs, clinical trials, research, and pharma industry")
    
    # Initialize chat history if not exists
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
    
    # RAG / Knowledge Base Section in Sidebar
    with st.sidebar:
        st.markdown("---")
        
        # Show document count
        docs = get_documents_list()
        
        if docs:
            st.markdown(f"### 📚 Knowledge Base")
            st.success(f"✅ **{len(docs)} documents** loaded")
            st.caption("Go to 'Company Knowledge' tab to manage documents")
        else:
            st.markdown("### 📚 Knowledge Base")
            st.info("No documents uploaded. Go to 'Company Knowledge' tab to upload PDFs.")
    
    # Display chat history
    for message in st.session_state.chat_history:
        role = message["role"]
        content = message["content"]
        
        if role == "user":
            with st.chat_message("user", avatar="👤"):
                st.markdown(content)
        else:
            with st.chat_message("assistant", avatar="🤖"):
                st.markdown(content)
    
    # Chat input
    user_input = st.chat_input("Ask me anything about pharma...")

    if user_input:
        # Display user message
        with st.chat_message("user", avatar="👤"):
            st.markdown(user_input)
        
        # Add to history
        st.session_state.chat_history.append({
            "role": "user",
            "content": user_input
        })
        
        # Get AI response
        with st.chat_message("assistant", avatar="🤖"):
            with st.spinner("Thinking..."):
                # Try RAG retrieval
                context = ""
                try:
                    if docs:  # Only try RAG if documents exist
                        context = get_rag_context(user_input, top_k=15, max_docs=5)
                        if context:
                            st.caption("🔍 Retrieved information from uploaded documents")
                except Exception as e:
                    st.caption(f"⚠️ RAG retrieval failed: {e}. Using base knowledge.")
                
                # Get response
                response = get_groq_response(user_input, st.session_state.chat_history[:-1], context)
                st.markdown(response)
        
        # Add to history
        st.session_state.chat_history.append({
            "role": "assistant",
            "content": response
        })
        
        st.rerun()
    
    # Sidebar with example questions
    with st.sidebar:
        st.markdown("---")
        st.markdown("### 💡 Example Questions")
        
        # Dynamic examples based on whether docs are loaded
        if docs:
            examples = [
                "Summarize the key findings from the documents",
                "What safety concerns are mentioned?",
                "Explain the mechanism of action",
                "Compare results across documents",
            ]
        else:
            examples = [
                "What is metformin used for?",
                "Explain Phase 3 clinical trials",
                "What are biologics?",
                "How does FDA drug approval work?",
                "Latest in cancer immunotherapy"
            ]
        
        for example in examples:
            if st.button(f"💬 {example}", use_container_width=True, key=f"ex_{example}"):
                st.session_state.example_question = example
                st.rerun()
        
        st.markdown("---")
        
        if st.button("🗑️ Clear Chat History", use_container_width=True, type="secondary"):
            st.session_state.chat_history = []
            st.rerun()
    
    # Show placeholder if no messages
    if not st.session_state.chat_history:
        if docs:
            st.info(f"""
            👋 **Welcome to the Pharma Knowledge Chatbot with Multi-Document RAG!**
            
            You currently have **{len(docs)} documents** in your knowledge base.
            
            I can help you:
            - Answer questions based on YOUR uploaded documents
            - Synthesize information across multiple documents
            - Compare and contrast findings
            - Explain complex pharmaceutical concepts
            
            Try asking about content from your uploaded documents!
            """)
        else:
            st.info("""
            👋 **Welcome to the Pharma Knowledge Chatbot!**
            
            I can help you with:
            - Drug information and usage
            - Clinical trial explanations
            - Regulatory guidance
            - Research paper insights
            - Industry trends and news
            
            💡 **Tip:** Upload documents in the 'Company Knowledge' tab to ask questions about YOUR specific documents!
            
            Try asking a question below or click an example on the sidebar!
            """)
        
        # Check if API key is set
        if not config.GROQ_API_KEY:
            st.warning("""
            ⚠️ **Groq API Key Required**
            
            To use the chatbot, get a free API key at https://console.groq.com/
            
            Then create a `.env` file with:
            ```
            GROQ_API_KEY=your_key_here
            ```
            """)
