import streamlit as st
import os
import tempfile
from main import run_pipeline
from dotenv import load_dotenv

load_dotenv()
import json

# ---------------- SESSION STATE ----------------
if "history" not in st.session_state:
    st.session_state.history = []
if "saved_paths" not in st.session_state:
    st.session_state.saved_paths = []
if "last_user_query" not in st.session_state:
    st.session_state.last_user_query = ""


# ---------------- STYLING ----------------
st.markdown("""
    <style>
        html, body {
            background-color: #001d3d !important;
        }
        .stApp {
            background-color: #001d3d !important;
        }
        .main-title {
            font-size: 2.6rem;
            font-weight: 900;
            text-align: center;
            color: #e0f7fa;
            margin-top: 20px;
        }
        .subtitle {
            font-size: 1.1rem;
            font-style: italic;
            color: #bbdefb;
            text-align: center;
            margin-bottom: 20px;
        }
        .sidebar-header {
            padding: 16px;
            background: #e0f7fa;
            border-radius: 10px;
            margin-bottom: 20px;
        }
        .sidebar-header h3 {
            color: #00203f;
            font-size: 1.4rem;
            margin-bottom: 5px;
        }
        .sidebar-header p {
            font-size: 0.95rem;
            color: #444;
        }
        .bot, .user {
            padding: 12px 16px;
            border-radius: 16px;
            margin: 10px 0;
            max-width: 80%;
            word-wrap: break-word;
            clear: both;
        }
        .user {
            background-color: #c8e6c9;
            margin-left: auto;
            color: #111;
        }
        .bot {
            background-color: #e3f2fd;
            margin-right: auto;
            color: #111;
        }

        /* 🔥 New Additions */
        .user, .bot {
            box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1);
            animation: fadeIn 0.3s ease-in;
        }

        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(5px); }
            to { opacity: 1; transform: translateY(0); }
        }

        .timestamp {
            font-size: 0.75rem;
            text-align: right;
            color: #aaa;
            margin-top: 2px;
        }

        .chat-scroll {
            max-height: 70vh;
            overflow-y: auto;
            padding-right: 8px;
        }

        textarea:focus, input:focus {
            border: 2px solid #4fc3f7 !important;
            box-shadow: 0 0 5px #4fc3f7;
        }
    </style>
""", unsafe_allow_html=True)


# ---------------- SIDEBAR ----------------
st.sidebar.markdown("""
    <div class="sidebar-header">
        <h3>💬 Document RAG MCP Agent</h3>
        <p>Upload documents and chat below</p>
    </div>
""", unsafe_allow_html=True)

page = st.sidebar.radio("Navigation", ["Chat", "FAQs"])

# ---------------- HEADER ----------------
st.markdown('<div class="main-title">📁 DocQ - Document Q&A Chatbot</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Ask anything about your uploaded files.</div>', unsafe_allow_html=True)

# ---------------- FILE UPLOADER ----------------
uploaded_files = st.file_uploader(
    "Upload files (PDF, DOCX, PPTX, CSV, TXT)",
    type=["pdf", "docx", "pptx", "csv", "txt"],
    accept_multiple_files=True
)

if uploaded_files:
    st.session_state.saved_paths = []
    for file in uploaded_files:
        temp_path = os.path.join(tempfile.gettempdir(), file.name)
        with open(temp_path, "wb") as f:
            f.write(file.getbuffer())
        st.session_state.saved_paths.append(temp_path)
    st.success("Files uploaded successfully.")

# ---------------- CHAT PAGE ----------------
if page == "Chat":
    st.markdown('<div style="max-width: 90%; margin: 0 5%;">', unsafe_allow_html=True)

    # Display chat history
    for role, message, contexts in st.session_state.history:
        css_class = "user" if role == "user" else "bot"
        st.markdown(f'<div class="{css_class}">{message}</div>', unsafe_allow_html=True)


        # ⬇️ Only for bot responses, show context chunks
        if role == "bot" and contexts:
            with st.expander("🧠 MCP Message Passed"):
                st.code(
                    json.dumps({
                        "type": "LLM_RESPONSE",
                        "sender": "LLMResponseAgent",
                        "receiver": "CoordinatorAgent",
                        "trace_id": "your_trace_id_here",  # optional
                        "payload": {
                            "retrieved_context": contexts,
                            "query": st.session_state.last_user_query  # save this on each user input
                        }
                    }, indent=2),
                    language="json"
                )


    st.markdown('</div>', unsafe_allow_html=True)

    # Chat input
    user_input = st.chat_input("Ask a question about documents...")

    

    if user_input:
        if st.session_state.saved_paths:
            st.session_state.history.append(("user", user_input, []))
            with st.spinner("Thinking..."):
                final_answer, contexts = run_pipeline(
                    st.session_state.saved_paths,
                    user_input
                )
            st.session_state.history.append(("bot", final_answer, contexts))
            if hasattr(st, "experimental_rerun"):
                st.experimental_rerun()
            else:
                st.rerun()
        else:
            st.warning("\ud83d\udccc Please upload at least one document before asking.")

# ---------------- FAQ PAGE ----------------
elif page == "FAQs":
    st.markdown('<div style="max-width: 750px; background: #e3f2fd; padding: 25px; border-radius: 15px; margin: 2rem auto;">', unsafe_allow_html=True)
    st.markdown("""
    ### Frequently Asked Questions

    **Q: What file types are supported?**  
    A: PDF, DOCX, PPTX, CSV, and TXT files.

    **Q: How does the chatbot work?**  
    A: It uses a Retrieval-Augmented Generation (RAG) pipeline with an agent architecture based on MCP to extract, retrieve, and answer from your uploaded documents.

    **Q: What is MCP (Model Context Protocol)?**  
    A: MCP is a structured protocol that governs message passing between agents like IngestionAgent, RetrievalAgent, LLMResponseAgent, and CoordinatorAgent. Each agent sends/receives structured messages containing type, sender, receiver, and payload.

    **Q: How is my query processed?**  
    A: Your question is passed to the RetrievalAgent → which fetches relevant chunks → then the LLMResponseAgent generates an answer → the CoordinatorAgent returns the final result.

    **Q: What’s inside the '🧠 MCP Message Passed'?**  
    A: It shows the full message payload passed from the LLMResponseAgent to the CoordinatorAgent — including your original query and retrieved context chunks.

    **Q: Is my data secure?**  
    A: Yes. Files are processed locally in your session and are never uploaded to external servers.

    **Q: Can I upload multiple documents?**  
    A: Yes. You can upload and query multiple files at once. They are all indexed together.
    """)
    st.markdown('</div>', unsafe_allow_html=True)