# 💻 Contributing Guide

Welcome! This guide helps new contributors get started quickly.

## 🧰 Prerequisites
- Python 3.11+
- `uv` package manager
- Google API Key (for Gemini Flash 3)

## 🔧 Setup

```bash
# Clone the repository
git clone https://github.com/anandmehak/Project-1-Education-EdTech---Generative-AI-Tutor-Adaptive-Learning-Platform.git
cd ai-course-tutor

# Create .env file
echo "GOOGLE_API_KEY=your_key_here" > .env

# Install dependencies
uv sync
```

## 🏃‍♂️ Running the App

```bash
# Start the API
uv run uvicorn backend.main:app --reload --port 8000
```

Access:
- **API Docs**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **Health**: [http://localhost:8000/health](http://localhost:8000/health)

## 🧪 Running Tests

```bash
# Run core test suite
uv run python tests/test_week1_improved.py

# Run individual test
uv run python -c "from tests.test_week1_improved import test_01_config_loads; test_01_config_loads()"
```

## 📁 Project Structure

```text
ai-course-tutor/
├── backend/
│   ├── main.py               # FastAPI app
│   ├── config.py             # Environment loader
│   ├── models/schemas.py     # Pydantic response models
│   ├── ingestion/
│   │   ├── pdf_parser.py     # PDF text extraction
│   │   ├── chunker.py        # Text splitting
│   │   ├── embedder.py       # Cloud Gemini embeddings
│   │   └── pipeline.py       # Orchestration
│   └── database/
│       └── vector_store.py   # ChromaDB interface
├── tests/
│   └── test_week1_improved.py # Edge case testing
├── uploads/                  # Temporary upload storage
└── chroma_data/              # Persistent vector storage
```

## 📝 Coding Standards
- Write type hints everywhere
- All functions have docstrings
- Error handling for every edge case
- No print statements in production logic
- Use `pathlib.Path` for file paths
- Windows-compatible paths only

## 🌱 Branching Strategy
- `main` — stable, deployable version
- `dev` — integration branch
- **Feature branches**: `feat/upload-validation`, `fix/chunk-size-bug`

Create pull requests into `dev`.

## 🚀 Deployment
Use Docker or run directly with:

```bash
uv run uvicorn backend.main:app --host 0.0.0.0 --port 8000
```
