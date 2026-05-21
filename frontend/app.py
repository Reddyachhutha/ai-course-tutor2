import streamlit as st

# Page settings
st.set_page_config(
    page_title="AI Tutor",
    page_icon="📘",
    layout="wide"
)

# Sidebar
st.sidebar.title("AI Tutor Platform")

page = st.sidebar.selectbox(
    "Choose Option",
    ["Home", "Chatbot", "Quiz Generator"]
)

# Home Page
if page == "Home":

    st.title("🎓 AI Tutor & Adaptive Learning Platform")

    st.write(
        "This platform helps students learn from uploaded study materials using AI."
    )

    col1, col2, col3 = st.columns(3)

    with col1:
        st.info("📄 Upload PDF Notes")

    with col2:
        st.info("🤖 Ask AI Questions")

    with col3:
        st.info("📝 Generate Quizzes")

    st.subheader("Technology Used")

    st.write(
        """
        - FastAPI
        - Streamlit
        - LangChain
        - ChromaDB
        - Gemini API
        """
    )

# Chatbot Page
elif page == "Chatbot":

    st.title("🤖 AI Tutor Chatbot")

    uploaded_file = st.file_uploader(
        "Upload PDF File",
        type=["pdf"]
    )

    question = st.text_input(
        "Ask your question"
    )

    if st.button("Get Answer"):

        if uploaded_file is not None and question != "":

            with st.spinner("Generating answer..."):

                st.success("Answer Generated")

                st.write("### Your Question")
                st.write(question)

                st.write("### AI Response")

                st.write(
                    "This answer will be generated from the uploaded PDF using RAG and Gemini API."
                )

        else:
            st.error("Please upload a PDF and ask a question.")

# Quiz Generator Page
elif page == "Quiz Generator":

    st.title("📝 Quiz Generator")

    topic = st.text_input(
        "Enter Topic Name"
    )

    difficulty = st.selectbox(
        "Select Difficulty",
        ["Easy", "Medium", "Hard"]
    )

    if st.button("Generate Quiz"):

        if topic != "":

            st.success("Quiz Generated")

            st.write(f"### Topic: {topic}")
            st.write(f"Difficulty: {difficulty}")

            st.write("1. Sample Question One")
            st.write("2. Sample Question Two")
            st.write("3. Sample Question Three")

        else:
            st.error("Please enter a topic.")


