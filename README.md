# Generative AI Tutor & Adaptive Learning Platform

An intelligent, production-grade 1-on-1 AI Tutoring System designed to provide personalized, 24/7 conversational learning support strictly based on specific course curriculums. The platform implements a robust Retrieval-Augmented Generation (RAG) pipeline to improve student comprehension while enforcing strict zero-hallucination guardrails.

---

## 👥 Team Structure & Core Responsibilities

Our development lifecycle follows an enterprise-standard division of labor to ensure robust architecture, code security, and seamless integration:

* **Mehak Anand (Project & QA Lead):** Repository Architecture, Workspace Security Governance, CI/CD Branching Policies, and End-to-End Modular QA Pipeline Validation.
* **Kumar Ravichandran (Backend Engineer):** Core RAG Logic Engine development, Text Processing pipelines, and ChromaDB Vector Storage integration.
* **Lalita Kumari (Frontend Engineer):** Streamlit Web User Interface client design, State Management, and Backend API Endpoint Integration.
* **Reddy (Infrastructure & DevOps Engineer):** Infrastructure setup, GitHub repository initialization, scalable workspace configuration, virtual machine environment management, database and SaaS integration support, multithreading environment setup, secure file upload/download handling, synchronization services, and service-oriented architecture support for deployment workflows.
---

## 🛠️ Project Architecture & Directory Structure

The repository is organized into isolated structural modules to maintain high scalability and code maintainability:

* 📂 **`backend/`** – Powered by **FastAPI**. Contains the server-side logic, API endpoint routes, connection hooks for the Google Gemini AI SDK, and conversational session memory caches.
* 📂 **`frontend/`** – Powered by **Streamlit**. Houses the responsive graphical user interface, file upload components for student PDFs, and the interactive chat window.
* 📂 **`tests/`** – Contains the Quality Assurance validation suites and black-box testing logs used to audit pipeline stability.
* 📂 **`docs/`** – Central repository for technical specifications, architecture blueprints, and weekly ledger tracking assets.

---

## 🚀 Key Technical Milestones (Phase 1 Completed)

### 1. Project Governance & Branch Security (Mehak Anand)
* **Environmental Isolation:** Initialized the project workspace using strict security hygiene, moving live API keys and system credentials into localized, hidden `.env` files protected by `.gitignore` rules.
* **Collaborative Branch Protection:** Established mandatory feature-branching workflows, blocking direct pushes to the `master` branch and requiring structured Pull Requests (PRs) for all merges.
* **Semantic Commit Ledgers:** Enforced standardized logging headers (`feat:`, `fix:`, `docs:`) to maintain an immutable, professional engineering history audit trail.

### 2. Ingestion & Embedding Pipeline (Kumar Ravichandran)
* **Document Parsing:** Implemented structural text extraction utilities to process raw educational PDF workloads and course syllabi.
* **Semantic Text Chunking:** Integrated LangChain's `RecursiveCharacterTextSplitter` to partition raw data into optimized, contextually cohesive token chunks to maximize vector lookup efficiency.
* **Vector Indexing:** Configured local multi-index storage via **ChromaDB** to run high-speed matrix similarity lookups.

### 3. RAG Pipeline & UI Integration (Lalita Kumari & Team)
* **Interface Deployment:** Built a clean, intuitive web interface using Streamlit, allowing seamless multi-document file uploads.
* **Cross-API Integration:** Successfully established end-to-end communication linking frontend user actions directly to the live FastAPI server endpoints.
* **Pedagogical Safety Guardrails:** Audited backend LLM system prompts to enforce strict context limitations, ensuring the AI tutor only outputs answers verified by the uploaded documents along with precise text citations.

---

## 🎯 Phase 2 Roadmap & Next Steps
* Transition layout wireframes into expanded dashboard metrics for tracking student learning progress.
* Incorporate automated automated assessment suites to evaluate context relevance metrics.
* Deploy live cloud hosting pipelines for an interactive final product demonstration.
