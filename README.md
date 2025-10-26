# AI-Powered Knowledge Base Search & Enrichment

A lightweight **Retrieval-Augmented Generation (RAG)** system that lets users upload documents, search them in natural language, get AI-generated answers, and receive smart suggestions when information is incomplete.

---

## Architecture

```
┌────────────┐     ┌────────────┐     ┌────────────┐     ┌────────────┐
│ Gradio UI  │ ─▶  │ FastAPI API│ ─▶  │ Qdrant DB  │ ─▶  │ LLM Engine │
│ (Frontend) │     │ (Backend)  │     │ (Vectors)  │     │ (Answer +  │
│            │     │            │     │            │     │  Critic)   │
└────────────┘     └────────────┘     └────────────┘     └────────────┘
```

* **Frontend:** Gradio (3 tabs — File, Collection, Chat)
* **Backend:** FastAPI REST API
* **Vector DB:** Qdrant (semantic search)
* **LLM Layer:** Answer generator + Critic evaluator

---

## Functionality

| Feature                | Description                                         |
| ---------------------- | --------------------------------------------------- |
| **Upload Documents**   | Add PDFs or text files via UI or API                |
| **Create Collections** | Group related files for search                      |
| **Link Content**       | Process files into embeddings (BGE-large-en-v1.5)   |
| **Ask Questions**      | Natural language query across documents             |
| **Reranker**           | Improves relevance of retrieved chunks              |
| **Critic Head**        | Evaluates if the answer is complete or uncertain    |
| **Auto-Enrichment**    | Suggests topics or documents to fill knowledge gaps |

---

## How It Works

1. **Upload & Index** — Files are embedded using **BGE-large-en-v1.5** and stored in **Qdrant**.
2. **Query** — A user asks a natural-language question.
3. **Retrieve** — Top-matching chunks are fetched via vector similarity.
4. **Rerank** — Results are refined using a **CrossEncoder**.
5. **Generate** — The **LLM** produces an answer using retrieved context.
6. **Critic Evaluate** — A critic model checks for missing information and suggests enrichment areas.

---

## Example Output

```json
{
  "answer": "LearnLM is part of Gemini 2.5 designed to infuse AI with learning science principles.",
  "confidence": 0.82,
  "is_relevant": true,
  "critic": {
    "confidence": 0.6,
    "missing_info": "Lacks examples of LearnLM in Google products.",
    "enrichment_suggestions": [
      "Add details about LearnLM applications in Search and Classroom.",
      "Include its underlying learning science principles."
    ]
  }
}
```

---

## Limitations

| Limitation                        | Reason                                       |
| --------------------------------- | -------------------------------------------- |
| **High Query Latency (~20–30s)**  | Sequential model loading and CPU inference   |
| **In-memory Qdrant on HF Spaces** | No persistence between restarts              |
| **Limited Auto-Enrichment**       | Placeholder logic (suggestive, not fetching) |
| **Single-threaded LLM calls**     | Slower for long or multi-query workflows     |

---

## Next Steps

1. **Optimize Latency** — Move to async or batched inference with GPU backend.
2. **Persistent Vector DB** — Use managed Qdrant or Pinecone cloud instance.
3. **Expand Enrichment Engine** — Integrate Wikipedia / ArXiv fetcher for missing info.
4. **Add Feedback Loop** — Allow user rating to fine-tune critic.
5. **Auto-Enrichment** — Fetch missing data from trusted external sources for validation.
6. **User Feedback Integration** — Allow users to rate answer quality and use this signal to improve model reliability.
7. **Deploy Production-Grade Stack** — Split frontend/backend, add auth & caching.

---

## Summary

✅ **End-to-End RAG Pipeline**
✅ **Structured AI Responses** (Answer + Confidence + Critic)
✅ **Smart Completeness Detection**
✅ **Knowledge Enrichment Suggestions**

---
