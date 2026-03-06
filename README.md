# ComplianceAgent

Enterprise Intelligent Compliance Q&A and Agent Assistant System

## Overview

ComplianceAgent is an enterprise-grade intelligent compliance Q&A system built with Python, LangGraph, and RAG (Retrieval Augmented Generation). It provides:

- **RAG-based Document Retrieval**: Vectorized storage and semantic search for enterprise compliance documents (PDF, Word, Markdown)
- **P-E-R Agent Architecture**: Plan-Execute-Review workflow using LangGraph for complex multi-step tasks
- **MCP Tool Gateway**: Unified tool calling interface with 95%+ success rate
- **Unified Model API Layer**: Support for multiple LLM services (enterprise internal + public cloud APIs)

## Features

### Core Capabilities

- 📄 **Multi-format Document Processing**: Support for PDF, Word (.docx), and Markdown documents
- 🔍 **Semantic Search**: Vector similarity search with re-ranking and citation annotation
- 🤖 **Intelligent Agent**: P-E-R (Plan-Execute-Review) architecture for complex task handling
- 🔧 **Tool Gateway**: MCP protocol-based unified tool calling interface
- 🌐 **Multi-Model Support**: Enterprise internal models (Qwen, ChatGLM) and public cloud APIs (Tongyi, Wenxin, OpenAI)
- 💬 **Multi-turn Conversations**: Context-aware dialogue with history management

### Performance Targets

- System QPS: ≥50 queries/second
- Average Response Time: <3 seconds (P95 <5s)
- Tool Call Success Rate: ≥95%
- Model API Success Rate: ≥99%
- Retrieval Accuracy (Top-5): ≥90%

## Quick Start

### Prerequisites

- Python 3.10 or higher
- Docker and Docker Compose
- Git

### Installation

1. **Clone the repository**:
```bash
git clone https://github.com/your-org/compliance-agent.git
cd compliance-agent
```

2. **Create virtual environment**:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**:
```bash
pip install -e ".[dev]"
```

4. **Configure environment variables**:
```bash
cp .env.example .env
# Edit .env with your configuration
```

5. **Start services with Docker Compose**:
```bash
docker-compose up -d
```

This will start:
- PostgreSQL with pgvector extension (port 5432)
- Redis cache (port 6379)
- ChromaDB vector database (port 8001)
- Compliance Agent API (port 8000)

### Running the Application

**Development mode**:
```bash
uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000
```

**Production mode**:
```bash
gunicorn src.api.main:app -w 4 -k uvicorn.workers.UvicornWorker
```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=html

# Run specific test file
pytest tests/test_rag_retrieval.py
```

## Project Structure

```
compliance-agent/
├── src/                    # Source code
│   ├── rag/               # RAG retrieval module
│   ├── agent/             # P-E-R Agent architecture (LangGraph)
│   ├── mcp/               # MCP tool gateway
│   ├── models/            # Unified model API layer
│   ├── api/               # FastAPI application
│   └── database/          # Database models and operations
├── tests/                 # Test suite
│   ├── unit/             # Unit tests
│   └── integration/      # Integration tests
├── config/                # Configuration files
├── docs/                  # Documentation
├── examples/              # Example usage
├── .ralph/               # Ralph autonomous development files
├── docker-compose.yml    # Docker services configuration
├── Dockerfile           # Container image definition
├── pyproject.toml       # Python project configuration
└── README.md            # This file
```

## API Documentation

Once the server is running, visit:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### Example API Calls

**Upload a document**:
```bash
curl -X POST "http://localhost:8000/api/v1/documents/upload" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "file=@document.pdf"
```

**Ask a question**:
```bash
curl -X POST "http://localhost:8000/api/v1/qa/ask" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "query": "What are the data privacy compliance requirements?",
    "top_k": 10,
    "use_agent": true
  }'
```

## Configuration

Key environment variables (see `.env.example` for full list):

| Variable | Description | Default |
|----------|-------------|---------|
| `DATABASE_URL` | PostgreSQL connection URL | postgresql://... |
| `REDIS_URL` | Redis connection URL | redis://localhost:6379 |
| `CHROMADB_HOST` | ChromaDB host | localhost |
| `CHROMADB_PORT` | ChromaDB port | 8001 |
| `DEFAULT_MODEL` | Default LLM model | qwen |
| `QWEN_API_KEY` | Qwen API key | - |
| `OPENAI_API_KEY` | OpenAI API key (optional) | - |

## Development

### Code Style

This project uses:
- **Black** for code formatting
- **Ruff** for linting
- **MyPy** for type checking

Format code:
```bash
black src/ tests/
ruff check src/ tests/ --fix
mypy src/
```

### Pre-commit Hooks

Install pre-commit hooks:
```bash
pre-commit install
```

## Architecture

### System Architecture

```
┌─────────────────────────────────────────────────────┐
│                   User Interface Layer               │
│         (Web UI / Enterprise WeChat / DingTalk)      │
└────────────────────┬────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────┐
│                  API Gateway Layer                   │
│              (FastAPI + Auth + Rate Limiting)        │
└────────────────────┬────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────┐
│              Agent Orchestration Layer (LangGraph)   │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐          │
│  │  Plan    │→ │ Execute  │→ │  Review  │          │
│  └──────────┘  └──────────┘  └──────────┘          │
└────────────────────┬────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────┐
│              MCP Tool Gateway Layer                  │
│  ┌─────────┐ ┌─────────┐ ┌─────────────────┐        │
│  │RAG检索  │ │数据库查询│ │  模型 API 调用  │        │
│  └─────────┘ └─────────┘ └─────────────────┘        │
└────────────────────┬────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────┐
│              Model Service Layer (External API)      │
│  ┌─────────────────┐ ┌─────────────────┐            │
│  │ Enterprise Model│ │ Public Cloud API│            │
│  │ (Qwen/ChatGLM)  │ │ (Tongyi/Wenxin) │            │
│  └─────────────────┘ └─────────────────┘            │
└────────────────────┬────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────┐
│                  Data Layer                          │
│  ┌─────────┐ ┌─────────┐ ┌─────────┐               │
│  │Vector DB│ │Relational│ │  Cache  │               │
│  └─────────┘ │Database  │ └─────────┘               │
└─────────────────────────────────────────────────────┘
```

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'feat: Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

MIT License - see LICENSE file for details

## Support

For issues and questions:
- GitHub Issues: https://github.com/your-org/compliance-agent/issues
- Documentation: https://compliance-agent.readthedocs.io

## Roadmap

### Phase 1: Basic Infrastructure ✅
- Project structure and dependencies
- Docker Compose for local development
- Basic configuration management

### Phase 2: RAG Foundation (In Progress)
- Document processing pipeline
- Vector database integration
- Semantic search implementation

### Phase 3: P-E-R Agent (Planned)
- LangGraph state management
- Plan-Execute-Review workflow
- Context management for long documents

### Phase 4: MCP Tool Gateway (Planned)
- Unified tool calling interface
- Parameter validation
- Error handling and retry logic

### Phase 5: Model API Layer (Planned)
- Multi-model support
- Intelligent routing
- Prompt template management

## Acknowledgments

Built with:
- [LangGraph](https://github.com/langchain-ai/langgraph) - Agent orchestration
- [LangChain](https://github.com/langchain-ai/langchain) - LLM application framework
- [FastAPI](https://fastapi.tiangolo.com/) - Modern web framework
- [ChromaDB](https://www.trychroma.com/) - Vector database
- [pgvector](https://github.com/pgvector/pgvector) - Vector similarity search for PostgreSQL
