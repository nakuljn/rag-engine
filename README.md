# 🚀 RAG Engine

A complete **Retrieval-Augmented Generation (RAG) engine** with a clean web interface for uploading documents, creating collections, and performing semantic search.

## ✨ Features

### 📁 File Management
- **Upload Files**: Drag & drop or select files to upload
- **View Files**: See all uploaded files with metadata (name, size, upload date)
- **Delete Files**: Remove files you no longer need

### 📚 Collection Management
- **Create Collections**: Organize your documents into searchable collections
- **Link Content**: Connect uploaded files to collections for semantic search
- **Query Collections**: Perform natural language searches across your documents
- **Smart Search**: Uses BGE-large-en-v1.5 embeddings for accurate results

## 🛠 Tech Stack

- **Frontend**: Gradio with clean, professional UI
- **Backend**: FastAPI with automatic OpenAPI docs
- **Vector Database**: Qdrant (in-memory for HF Spaces)
- **Embeddings**: BGE-large-en-v1.5 (1024 dimensions)
- **Architecture**: Clean layered architecture with service-repository pattern

## 🔄 How to Use

### 1. Upload Files
1. Go to the **"📁 File Management"** tab
2. Click or drag files to the upload area
3. Click **"Upload"** to store your files
4. View all uploaded files in the table below

### 2. Create Collections
1. Switch to the **"📚 Collection Management"** tab
2. Enter a collection name (e.g., "Research Papers", "Documentation")
3. Click **"Create Collection"**

### 3. Link Content to Collections
1. In the **"Link Content"** section:
   - Enter the collection name
   - Select a file from the dropdown
   - Click **"🔗 Link Content"**
2. This will process the file and create searchable embeddings

### 4. Query Your Documents
1. In the **"Query Collection"** section:
   - Enter the collection name
   - Type your search query (e.g., "What is machine learning?")
   - Click **"🔍 Query"**
2. Get relevant results from your documents!

## 📋 Example Workflow

```
1. Upload "machine_learning_guide.pdf" ✅
   → Returns: {"file_id": "uuid123", "filename": "machine_learning_guide.pdf"}

2. Create collection "AI Resources" ✅
   → Collection created in Qdrant database

3. Link PDF to "AI Resources" collection ✅
   → Request: [{"name": "machine_learning_guide.pdf", "id": "uuid123", "field": "text"}]
   → Response: [{"indexing_status": "INDEXING_SUCCESS", "status_code": 200}]

4. Query: "What are neural networks?" ✅
   → Get semantically relevant excerpts from your PDF!

5. Unlink files when done ✅
   → Request: ["uuid123"] to remove from collection
```

## 🏗 Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Gradio UI     │───▶│  FastAPI API    │───▶│ Qdrant Database │
│   (Frontend)    │    │  (Backend)      │    │   (Vectors)     │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 🚀 Deployment

### Hugging Face Spaces
This application runs on **Hugging Face Spaces** with:
- **Gradio frontend** on port 7860 (public interface)
- **FastAPI backend** on port 8000 (internal API)
- **In-memory Qdrant** for vector storage
- **BGE embeddings** for semantic search

### Local Development
```bash
# 1. Copy environment file
cp .env.example .env

# 2. Start Qdrant (for local development)
docker run -p 6333:6333 -v ./qdrant_data:/qdrant/storage qdrant/qdrant

# 3. Install dependencies
pip install -r requirements.txt

# 4. Start the application
python app.py  # Starts both FastAPI backend and Gradio frontend
```

## 🔍 Debug Information

Check the logs in the console for detailed API calls and responses. All requests include timing information and error details for debugging.

## 📚 API Endpoints

The backend exposes a full REST API:

### Files (4 endpoints):
- `POST /api/v1/files` - Upload files (multipart/form-data)
- `GET /api/v1/files` - List all files with metadata
- `GET /api/v1/files/{id}` - Get file info
- `DELETE /api/v1/files/{id}` - Delete file

### Collections (6 endpoints):
- `GET /api/v1/collection/{name}` - Check if collection exists
- `POST /api/v1/collection` - Create collection
- `DELETE /api/v1/collection/{name}` - Delete collection
- `POST /api/v1/{collection}/link-content` - Link multiple files (207 multi-status)
- `POST /api/v1/{collection}/unlink-content` - Remove multiple files (207 multi-status)
- `POST /api/v1/{collection}/query` - Query collection

### Multi-File Operations
The link-content and unlink-content endpoints support batch operations:

**Link Content Request:**
```json
POST /{collection}/link-content
[
  {"name": "document.pdf", "id": "file_uuid_1", "field": "text"},
  {"name": "report.txt", "id": "file_uuid_2", "field": "text"}
]
```

**Link Content Response (207 Multi-Status):**
```json
[
  {
    "name": "document.pdf", "id": "file_uuid_1", "field": "text",
    "created_at": "2023-10-25T10:30:00Z",
    "indexing_status": "INDEXING_SUCCESS", "status_code": 200
  },
  {
    "name": "missing.pdf", "id": "file_uuid_2", "field": "text",
    "indexing_status": "INDEXING_FAILED", "status_code": 404,
    "message": "File not found"
  }
]
```

## 💡 Tips

- **File Types**: Works best with text files (PDF, TXT, MD, etc.)
- **Collection Names**: Use descriptive names for better organization
- **Query Style**: Ask natural questions for best search results
- **File Size**: Keep files reasonably sized for faster processing

---

Built with ❤️ using FastAPI, Gradio, and Qdrant
