# Running the RAG Chatbot System

## Architecture

```
┌─────────────────────┐         HTTP API          ┌─────────────────────┐
│  Streamlit Frontend │  ◄──────────────────────► │  FastAPI Backend    │
│  (Port 8501)        │                           │  (Port 8000)        │
│                     │                           │                     │
│  - Chat UI          │                           │  - RAG Chain        │
│  - Analytics        │                           │  - LLM (Groq)       │
│  - Logs Viewer      │                           │  - Embeddings       │
│  - Settings         │                           │  - Retrieval        │
└─────────────────────┘                           └──────────┬──────────┘
                                                             │
                                                             │ HTTP API
                                                             ▼
                                                  ┌─────────────────────┐
                                                  │  Qdrant Cloud       │
                                                  │  (Vector DB)        │
                                                  └─────────────────────┘
```

## Starting the System

### Step 1: Start Backend (FastAPI)

```powershell
# Terminal 1
cd 'C:\Program Files\Repos\learning projects\myJarvis'
.venv\Scripts\activate
uvicorn backend.main:app --reload
```

**Backend will run at:** `http://localhost:8000`
**API Docs:** `http://localhost:8000/docs`

✅ Wait for: `Application startup complete.`

### Step 2: Start Frontend (Streamlit)

```powershell
# Terminal 2 (new terminal)
cd 'C:\Program Files\Repos\learning projects\myJarvis'
.venv\Scripts\activate
streamlit run app.py
```

**Frontend will run at:** `http://localhost:8501`

✅ Both services must be running simultaneously!

---

## Testing the Connection

### 1. Check Backend
Visit `http://localhost:8000/docs`

Test the `/api/v1/health` endpoint - should return:
```json
{"status": "healthy"}
```

### 2. Check Frontend
Visit `http://localhost:8501`

Sidebar should show database stats without errors.

### 3. Test Chat
Ask a question in the chat tab. You should see:
- Response from the LLM
- Retrieved context (if documents are ingested)
- No timeout errors

---

## Troubleshooting

### ❌ "Connection refused" error in Streamlit
**Problem:** Backend is not running  
**Solution:** Start FastAPI backend first (Step 1)

### ❌ "timed out" errors in Streamlit
**Problem:** Streamlit was directly calling backend modules (old code)  
**Solution:** You've already fixed this! Frontend now calls backend via HTTP

### ❌ "404 Not Found" errors
**Problem:** API endpoint doesn't exist  
**Solution:** Check backend is running at correct port (8000)

### ❌ Chat returns "No relevant context"
**Problem:** No documents in Qdrant  
**Solution:** Run ingestion: `python -m scripts.ingest`

---

## Key Differences: Old vs New Architecture

### ❌ Old (Broken)
```python
# Streamlit directly imported backend
from backend.rag.chain import RAGChain
result = RAGChain().process_query(...)  # Direct call
```
**Problem:** Network issues in Streamlit affected Qdrant connection

### ✅ New (Fixed)
```python
# Streamlit calls backend via HTTP
from frontend.api_client import get_api_client
result = get_api_client().chat(...)  # HTTP call
```
**Benefit:** Backend handles all Qdrant connections, Streamlit just displays

---

## Port Reference

| Service          | Port | URL                           |
|------------------|------|-------------------------------|
| FastAPI Backend  | 8000 | http://localhost:8000         |
| API Docs         | 8000 | http://localhost:8000/docs    |
| Streamlit UI     | 8501 | http://localhost:8501         |

---

## Quick Commands

```powershell
# Start backend
uvicorn backend.main:app --reload

# Start frontend (separate terminal)
streamlit run app.py

# Ingest documents
python -m scripts.ingest

# Check health
curl http://localhost:8000/api/v1/health

# Test chat via CLI
curl -X POST http://localhost:8000/api/v1/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "What skills do you have?"}'
```

---

## Production Deployment Notes

When deploying to production:

1. **Backend (FastAPI)** → Deploy to cloud (HuggingFace Spaces, Railway, Render)
2. **Frontend (Streamlit)** → Deploy separately or embed widget instead
3. **Update API URL** in `frontend/api_client.py`:
   ```python
   APIClient(base_url="https://your-backend.hf.space")
   ```

Separate deployments = better scalability and security! 🚀
