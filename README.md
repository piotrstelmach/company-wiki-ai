# Company Wiki AI Assistant

An intelligent, internal company wiki assistant that provides accurate answers based on corporate documents using RAG (Retrieval-Augmented Generation) and RBAC (Role-Based Access Control).

## 🚀 Overview

This project is a full-stack application designed to help employees find information within company documentation (PDFs, policies, standards) through a natural language interface. It ensures that users only access information relevant to their department or public documents.

## ✨ Key Features

- **RAG (Retrieval-Augmented Generation):** Uses vector search to find relevant document chunks and provides context to the LLM for accurate, hallucination-free answers.
- **RBAC (Role-Based Access Control):** Document access is filtered by `department_id`. Users only see answers based on their own department's documents or general company-wide information (ID `-1`).
- **User Roles:** System supports different user roles (ADMIN, HR, EMPLOYEE) for granular access control and management.
- **Streaming Responses:** Real-time AI response streaming for a smooth user experience.
- **Document Ingestion:** Automated PDF processing, text splitting, and vector embedding.
- **Persistent Chat History:** Stores conversations in PostgreSQL for later retrieval.
- **Modern Tech Stack:** Built with FastAPI, Next.js, Qdrant, and Ollama.

## 🛠️ Tech Stack

### Backend
- **Framework:** FastAPI
- **Database:** PostgreSQL (SQLModel)
- **Vector Store:** Qdrant
- **LLM Orchestration:** LangChain
- **AI Models:** Ollama (Llama/Mistral for chat, Nomic-Embed-Text for embeddings)
- **Authentication:** JWT-based auth

### Frontend
- **Framework:** Next.js (App Router)
- **State Management:** TanStack Query (React Query)
- **Styling:** Tailwind CSS

## 🔐 Role-Based Access Control (RBAC)

The system implements a multi-layered RBAC system to ensure data security and relevance.

### User Roles
| Role | ID | Description |
| :--- | :--: | :--- |
| **ADMIN** | `1` | Full system access, including management of users and all documents. |
| **HR** | `2` | Access to human resources policies and recruitment data. |
| **EMPLOYEE** | `3` | Default role with access to general company policies and their own department's documents. |

### Departments & Filtering (RAG)
When a document is ingested, it is assigned a `department_id`. The AI assistant filters context based on the user's `department_id`.

Default IDs from `seed.py`:
| Department | ID | Purpose |
| :--- | :--: | :--- |
| **Company-Wide** | `-1` | Accessible to everyone (Public). |
| **IT** | `1` | IT-specific documentation. |
| **Human Resources** | `2` | HR policies and internal procedures. |
| **Sales** | `3` | Sales-related materials. |

#### Filtering Logic:
- **Department Match:** User sees documents belonging to their assigned department.
- **Public Access:** Documents with `department_id: -1` are always accessible.
- **Strict Isolation:** The LLM is forbidden from using documents outside the allowed department scope.

## 📂 Project Structure

```text
.
├── backend/            # FastAPI application
│   ├── services/       # Business logic (AI, Chat, File services)
│   ├── scripts/        # Utility scripts (generation, ingestion)
│   ├── models.py       # SQLModel database schemas
│   ├── main.py         # API routes and entry point
│   └── requirements.txt
├── frontend/           # Next.js application
│   ├── app/            # App router pages (Chat, Login, etc.)
│   ├── components/     # UI components
│   └── package.json
├── data/               # Persistent data for Docker (DB, Qdrant, Ollama)
├── test_sources/       # (Ignored) Local folder for PDF documents
├── docker-compose.yml  # Infrastructure setup
├── .env.example       # Example environment variables
└── .gitignore          # Git exclusion rules
```

## 🚦 Getting Started

### Prerequisites
- Docker & Docker Compose
- [Ollama](https://ollama.com/) installed locally (or running in a container)
- Python 3.10+ (for local backend development)
- Node.js & pnpm (for local frontend development)

### 1. Infrastructure Setup
1. Copy the example environment file and fill in the values:
   ```bash
   cp .env.example .env
   ```
2. Start the core services (PostgreSQL, Qdrant):
```bash
docker-compose up -d
```

### 2. Prepare Ollama
Ensure you have the required models pulled in Ollama:
```bash
ollama pull llama3 # or your preferred chat model
ollama pull nomic-embed-text
```

### 3. Backend Setup
1. Navigate to `backend/`:
   ```bash
   cd backend
   ```
2. Create a virtual environment and install dependencies:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```
3. Run the development server:
   ```bash
   bash run_dev.sh
   ```

### 4. Frontend Setup
1. Navigate to `frontend/`:
   ```bash
   cd frontend
   ```
2. Install dependencies:
   ```bash
   pnpm install
   ```
3. Run the development server:
   ```bash
   pnpm dev
   ```

## 📖 Usage

All commands below should be executed from the `backend/` directory with the virtual environment activated.

1. **Register/Login:** Create an account via the frontend or use existing test users.
2. **Seed Data:** Initialize roles, departments, and test users:
   ```bash
   python seed.py
   ```
3. **Generate Samples (Optional):** If you don't have your own PDFs, generate some English samples:
   ```bash
   python scripts/generate_samples.py
   ```
4. **Ingest Documents:** Process and index PDF documents. Each ingestion request requires a `department_id` parameter (use `-1` for public documents).
   ```bash
   python scripts/ingest_docs.py
   ```
5. **Chat:** Open the frontend and ask questions like "What are the remote work policies?" or "How do I onboard a new employee?".
6. **Contextual Answers:** The assistant will search the wiki and provide an answer strictly based on the provided context and the user's role.

## 🧪 Testing
Run the test suite using the provided script:
```bash
bash run_tests.sh
```
