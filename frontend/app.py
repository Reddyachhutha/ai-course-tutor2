import os
import streamlit as st
import requests

BACKEND_URL = os.getenv("BACKEND_URL", "http://127.0.0.1:8000")

# ---------------- PAGE SETTINGS ---------------- #

st.set_page_config(
    page_title="AI Tutor Platform",
    page_icon="📘",
    layout="wide"
)

# ---------------- SIDEBAR ---------------- #

st.sidebar.title("📚 AI Tutor Platform")

page = st.sidebar.selectbox(
    "Navigation",
    ["Home", "Chatbot", "Quiz Generator"]
)

# ---------------- HOME PAGE ---------------- #

if page == "Home":

    st.title("🎓 Generative AI Tutor & Adaptive Learning Platform")

    st.write("""
    Welcome to the AI Tutor Platform.

    This project is built using:
    - FastAPI
    - Streamlit
    - LangChain
    - ChromaDB
    - Gemini API

    The platform allows students to:
    - Upload study materials
    - Ask questions from PDFs
    - Generate quizzes
    - Learn interactively using AI
    """)

    st.divider()

    col1, col2, col3 = st.columns(3)

    with col1:
        st.info("📄 Upload PDF Notes")

    with col2:
        st.info("🤖 Ask Questions")

    with col3:
        st.info("📝 Generate Quizzes")

    st.divider()

    st.subheader("🚀 Features")

    st.write("""
    ✅ Retrieval-Augmented Generation (RAG)  
    ✅ Conversational AI Tutor  
    ✅ Adaptive Learning Support  
    ✅ PDF-based Question Answering  
    ✅ Quiz Generation  
    """)

# ---------------- CHATBOT PAGE ---------------- #

elif page == "Chatbot":

    st.title("🤖 AI Tutor Chatbot")

    st.write("Upload your study PDF and ask questions related to the content.")

    uploaded_file = st.file_uploader(
        "Upload PDF File",
        type=["pdf"]
    )

    question = st.text_input(
        "Ask your question"
    )

    if st.button("Get Answer"):

        if uploaded_file is not None and question != "":

            with st.spinner("Generating answer from AI Tutor..."):

                try:

                    # -------- Upload PDF -------- #

                    files = {
                        "file": (
                            uploaded_file.name,
                            uploaded_file.getvalue(),
                            "application/pdf"
                        )
                    }

                    upload_response = requests.post(
                        f"{BACKEND_URL}/upload",
                        files=files,
                        timeout=120
                    )

                    # -------- Check Upload -------- #

                    if upload_response.status_code == 200:

                        # -------- Chat Request -------- #

                        payload = {
                            "question": question,
                            "session_id": "student_001"
                        }

                        response = requests.post(
                            f"{BACKEND_URL}/chat",
                            json=payload,
                            timeout=120
                        )

                        # -------- Display Response -------- #

                        if response.status_code == 200:

                            data = response.json()

                            st.success("Answer Generated Successfully")

                            st.write("### 📌 Your Question")
                            st.write(question)

                            st.write("### 🤖 AI Response")
                            st.success(data["answer"])

                            # -------- Sources -------- #

                            if "sources" in data:

                                st.write("### 📚 Sources")

                                for source in data["sources"]:
                                    st.write(f"- {source}")

                        else:
                            st.error("Failed to get response from chatbot backend.")

                    else:
                        st.error("PDF upload failed.")

                except Exception as e:
                    st.error(f"Error: {e}")

        else:
            st.error("Please upload a PDF and ask a question.")

# ---------------- QUIZ GENERATOR PAGE ---------------- #

elif page == "Quiz Generator":

    st.title("📝 Quiz Generator")

    st.write("Generate quizzes based on study topics.")

    topic = st.text_input(
        "Enter Topic Name"
    )

    difficulty = st.selectbox(
        "Select Difficulty",
        ["Easy", "Medium", "Hard"]
    )

    if st.button("Generate Quiz"):

        if topic != "":

            with st.spinner("Generating quiz from AI Tutor..."):
                try:
                    payload = {
                        "topic": topic,
                        "difficulty": difficulty
                    }
                    response = requests.post(
                        f"{BACKEND_URL}/quiz",
                        json=payload,
                        timeout=120
                    )
                    if response.status_code == 200:
                        data = response.json()
                        st.success("Quiz Generated Successfully")
                        st.write(f"### 📌 Topic: {data['topic']}")
                        st.write(f"### 🎯 Difficulty: {data['difficulty']}")
                        st.write("## Quiz Content")
                        st.write(data["quiz"])
                    else:
                        st.error("Failed to generate quiz from backend.")
                except Exception as e:
                    st.error(f"Error: {e}")

        else:
            st.error("Please enter a topic.")


