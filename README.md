# 🎓 AI Course Tutor

> An AI-powered personalized tutoring system that answers student questions **strictly from uploaded course material**, preventing hallucinations.

Built with FastAPI + ChromaDB + Local Embeddings + Gemini Flash 3.

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Python Version](https://img.shields.io/badge/python-3.11+-blue)]()

## ✨ Features

- **No Hallucinations**: Answers only from your syllabus
- **Fast Ingestion**: Parse PDFs -> Chunks -> Vector DB in seconds
- **Edge Case Safe**: Handles scanned, corrupted, password-protected PDFs
- **Swagger UI**: Fully documented API at `/docs`
- **Persistent Storage**: Knowledge survives restarts
- **Tested**: 10+ edge cases covered in test suite

## 📦 Tech Stack

| Layer | Technology |
|------|------------|
| Backend | FastAPI |
| LLM | Gemini Flash 3 |
| Embeddings | sentence-transformers (local) |
| Vector DB | ChromaDB (persistent) |
| Language | Python 3.11 |
| Packaging | uv |

## ▶️ Quick Start

```bash
# Clone the repo
git clone https://github.com/anandmehak/Project-1-Education-EdTech---Generative-AI-Tutor-Adaptive-Learning-Platform.git
cd ai-course-tutor

# Install dependencies
uv sync

# Start the API server
uv run uvicorn backend.main:app --reload --port 8000
```

Open Swagger UI: [http://localhost:8000/docs](http://localhost:8000/docs)

## 🧪 Test Suite

```bash
# Run all tests
uv run python tests/test_week1_improved.py
```

## 🛠️ API Endpoints

| Method | Endpoint | Purpose |
|--------|----------|---------|
| GET | /health | Check if API is running |
| POST | /upload | Upload a PDF syllabus |
| GET | /stats | View knowledge base size |
| GET | /inspect | Browse stored text chunks |
| DELETE | /reset | Clear vector database |

## 🤝 Contributing
See [CONTRIBUTING.md](CONTRIBUTING.md) for setup and workflow.

## 📄 Overview
See [PROJECT_OVERVIEW.md](PROJECT_OVERVIEW.md) for full architecture.

## 📜 License
MIT

Made with ❤️ for students who deserve better tutors.
