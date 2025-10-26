# AI-Powered Knowledge Base Search & Enrichment

A production-ready **Retrieval-Augmented Generation (RAG)** system that enables users to upload documents, perform natural language searches, receive AI-generated answers, and get intelligent suggestions for knowledge base enrichment when information is incomplete.

## 🎯 Assignment Alignment

This system fully addresses all core requirements of the AI-Powered Knowledge Base Search & Enrichment assignment:

### ✅ Core Requirements Implemented

1. **Document Upload & Storage**: Multi-format file upload with persistent storage and metadata management
2. **Natural Language Search**: Semantic search using state-of-the-art BGE embeddings and vector similarity
3. **AI-Generated Answers**: LLM-powered answer generation using retrieved document context
4. **Completeness Detection**: AI critic system that detects incomplete or uncertain information
5. **Enrichment Suggestions**: Intelligent recommendations for improving the knowledge base

### 🏆 High-Value Features

- **Structured JSON Output**: Returns confidence scores, missing information analysis, and enrichment suggestions
- **Graceful Handling**: Manages irrelevant documents and provides meaningful fallbacks
- **Multi-Status Operations**: Batch processing with individual result tracking (HTTP 207)
- **Real-time Feedback**: Immediate completeness assessment and enrichment guidance

## 🏗 System Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Gradio UI     │───▶│  FastAPI API    │───▶│ Vector Database │───▶│  LLM Services   │
│  (Frontend)     │    │  (REST Layer)   │    │   (Qdrant)      │    │ (Answer+Critic) │
└─────────────────┘    └─────────────────┘    └─────────────────┘    └─────────────────┘

                                ↓
                    ┌─────────────────────────┐
                    │   Knowledge Enrichment   │
                    │   Suggestion Engine      │
                    └─────────────────────────┘
```

## 🧠 AI-Powered Features

### Intelligent Answer Generation
The system uses a multi-stage AI pipeline to generate comprehensive answers:

1. **Semantic Retrieval**: BGE-large-en-v1.5 embeddings for accurate document matching
2. **Context Assembly**: Intelligent chunk selection and deduplication
3. **Answer Synthesis**: LLM-powered answer generation using retrieved context
4. **Quality Assessment**: AI critic evaluation for completeness and accuracy

### Smart Completeness Detection
The integrated **AI Critic** system provides:

```json
{
  "answer": "Machine learning is a subset of artificial intelligence...",
  "confidence": 0.85,
  "is_relevant": true,
  "chunks": [...],
  "critic": {
    "confidence": 0.7,
    "missing_info": "No information about deep learning frameworks or practical applications",
    "enrichment_suggestions": [
      "Add documentation about TensorFlow or PyTorch",
      "Include practical ML implementation examples"
    ]
  }
}
```

### Knowledge Base Enrichment
When information gaps are detected, the system suggests:
- **Additional Document Types**: Specific topics or formats needed
- **Content Areas**: Missing knowledge domains to address
- **Data Sources**: Recommended external resources for enrichment

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Docker (for local Qdrant)

### Local Development
```bash
# 1. Clone and setup
git clone <repository-url>
cd rag-engine
cp .env.example .env

# 2. Start vector database
docker run -p 6333:6333 -v ./qdrant_data:/qdrant/storage qdrant/qdrant

# 3. Install dependencies
pip install -r requirements.txt

# 4. Launch application
python app.py
```

**Access Points:**
- Frontend UI: http://localhost:7860
- REST API: http://localhost:8000
- API Documentation: http://localhost:8000/docs

### Production Deployment
The system is configured for Hugging Face Spaces with automatic environment detection:
- In-memory Qdrant for serverless deployment
- Optimized model loading for faster startup
- Environment-based configuration switching

## 📋 Usage Workflow

### 1. Document Upload
```bash
curl -X POST "http://localhost:8000/api/v1/files" \
  -F "file=@document.pdf"
```

### 2. Collection Creation
```bash
curl -X POST "http://localhost:8000/api/v1/collection" \
  -H "Content-Type: application/json" \
  -d '{"name": "research_papers"}'
```

### 3. Content Linking
```bash
curl -X POST "http://localhost:8000/api/v1/research_papers/link-content" \
  -H "Content-Type: application/json" \
  -d '[{"name": "document.pdf", "file_id": "uuid123", "type": "pdf"}]'
```

### 4. Intelligent Search
```bash
curl -X POST "http://localhost:8000/api/v1/research_papers/query" \
  -H "Content-Type: application/json" \
  -d '{"query": "What are the latest advances in transformer architectures?", "enable_critic": true}'
```

## 🔧 Design Decisions

### Architecture Choices
- **Clean Architecture**: Layered design with clear separation of concerns
- **Service-Repository Pattern**: Business logic isolated from data access
- **RESTful API**: Standard HTTP methods with proper status codes
- **Async Processing**: Non-blocking operations for better performance

### Technology Stack
- **FastAPI**: High-performance async API framework with automatic documentation
- **Qdrant**: Purpose-built vector database for semantic search
- **BGE Embeddings**: State-of-the-art multilingual embedding model
- **Gradio**: Rapid prototyping with professional UI components

### Model Selection
- **BGE-large-en-v1.5**: Chosen for superior performance on retrieval tasks
- **Gemini/GPT Integration**: Configurable LLM backends for answer generation
- **Temperature Control**: Balanced creativity vs. accuracy in responses

## ⚖️ Trade-offs & Constraints

### 24-Hour Development Constraints
1. **Model Choice**: Used pre-trained embeddings instead of fine-tuning for specific domain
2. **Storage**: Implemented file-based storage instead of distributed database
3. **Caching**: Basic in-memory caching instead of Redis/Memcached
4. **Authentication**: Simplified access control for faster development

### Performance Optimizations
- **Batch Processing**: Multi-file operations with individual status tracking
- **Embedding Caching**: Reduced redundant computation
- **Async Architecture**: Non-blocking I/O for better throughput
- **Memory Management**: Efficient vector storage and retrieval

### Scalability Considerations
- **Stateless Design**: Enables horizontal scaling
- **External Vector DB**: Qdrant provides distributed scaling options
- **Modular Services**: Independent scaling of components
- **Configuration Management**: Environment-based deployment flexibility

## 📊 Testing & Validation

### Automated Testing
```bash
# Run test suite
pytest src/tests/

# API endpoint testing
python -m pytest src/tests/test_api.py -v

# Service layer testing
python -m pytest src/tests/test_services.py -v
```

### Manual Testing Scenarios
1. **Document Upload**: Test various file formats (PDF, TXT, MD)
2. **Search Quality**: Validate semantic search accuracy
3. **Completeness Detection**: Verify critic system functionality
4. **Error Handling**: Test edge cases and error conditions

### Performance Benchmarks
- **Upload Speed**: ~2-5 seconds for typical documents
- **Search Latency**: <500ms for most queries
- **Embedding Generation**: ~1-3 seconds depending on document size
- **Critic Evaluation**: ~2-4 seconds for completeness analysis

## 📈 Future Enhancements

### Stretch Goals (Roadmap)
- **Auto-Enrichment**: Integration with external knowledge sources (Wikipedia, academic papers)
- **User Feedback Loop**: Rating system for continuous model improvement
- **Advanced Analytics**: Knowledge gap analysis and trend identification
- **Multi-Modal Support**: Image and video content processing

### Potential Integrations
- **External APIs**: Automated enrichment from trusted sources
- **Collaboration Features**: Multi-user knowledge base management
- **Version Control**: Document change tracking and history
- **Export Capabilities**: Knowledge base export in various formats

## 🔍 API Reference

### Core Endpoints

#### Files Management
- `POST /api/v1/files` - Upload documents
- `GET /api/v1/files` - List all files
- `DELETE /api/v1/files/{id}` - Remove file

#### Collections Management
- `POST /api/v1/collection` - Create collection
- `GET /api/v1/collections` - List all collections
- `DELETE /api/v1/collection/{name}` - Delete collection

#### Content Operations
- `POST /api/v1/{collection}/link-content` - Add documents to collection
- `POST /api/v1/{collection}/unlink-content` - Remove documents
- `POST /api/v1/{collection}/query` - Perform intelligent search

### Response Formats

#### Query Response Structure
```json
{
  "answer": "string",
  "confidence": 0.0-1.0,
  "is_relevant": boolean,
  "chunks": [
    {
      "source": "document_id",
      "text": "relevant_excerpt"
    }
  ],
  "critic": {
    "confidence": 0.0-1.0,
    "missing_info": "string",
    "enrichment_suggestions": ["string"]
  }
}
```

## 🎥 Demo

**[5-minute demo video showcasing the complete workflow from document upload to intelligent search and enrichment suggestions]**

## 🤝 Contributing

### Development Setup
1. Fork the repository
2. Create feature branch: `git checkout -b feature/enhancement`
3. Follow code style: `black src/ && flake8 src/`
4. Add tests for new functionality
5. Submit pull request with detailed description

### Code Quality Standards
- **Type Hints**: Full type annotation coverage
- **Documentation**: Docstrings for all public methods
- **Testing**: Unit tests for critical functionality
- **Code Style**: Black formatter + Flake8 linting

---

**Built for the AI-Powered Knowledge Base Search & Enrichment Assignment**
*Demonstrating production-ready RAG implementation with intelligent completeness detection and enrichment suggestions*