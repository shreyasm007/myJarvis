# Streamlit Admin Dashboard

## Features

✨ **Interactive Chat** - Test your RAG chatbot with real-time retrieved context display  
📄 **Log Viewer** - Monitor application and conversation logs  
📊 **Analytics** - View conversation statistics and retrieval metrics  
📁 **Document Management** - Check ingested documents and database status  
⚙️ **Live Settings** - Change LLM model, temperature, and retrieval parameters on-the-fly

## Project Structure

```
myJarvis/
├── app.py                      # Main Streamlit entry point
├── frontend/                   # Modular frontend package
│   ├── __init__.py
│   ├── config.py              # Configuration and constants
│   ├── utils.py               # Utility functions
│   ├── sidebar.py             # Sidebar component
│   └── tabs/                  # Tab components
│       ├── __init__.py
│       ├── chat.py            # Chat interface
│       ├── logs.py            # Log viewer
│       ├── analytics.py       # Analytics dashboard
│       └── documents.py       # Document management
```

## Quick Start

```powershell
# Make sure your FastAPI backend is NOT running (Streamlit uses the same modules)

# Activate virtual environment
.venv\Scripts\activate

# Run Streamlit
streamlit run app.py
```

The UI will open at `http://localhost:8501`

## What You Can Do

### 1. Chat Tab
- Ask questions and see responses
- View **retrieved context** from Qdrant in real-time
- See similarity scores for each document
- **Debug why you're getting 0 documents** - you'll see exactly what the retriever finds

### 2. Logs Tab
- View last 100-500 lines of logs
- Color-coded by level (ERROR/WARNING/INFO)
- Separate app logs and conversation logs
- Refresh in real-time

### 3. Analytics Tab
- Total conversations count
- Retrieval success rate
- Query length distribution
- Visual charts and metrics

### 4. Documents Tab
- See all files in `backend/data/documents/`
- Check Qdrant collection stats
- Preview document content
- Verify what's actually ingested

### Sidebar Settings

Change these live without restarting:
- **LLM Model** - Switch between Llama 3.3, Mixtral, Gemma, etc.
- **Temperature** - Control creativity (0.0 = focused, 1.0 = creative)
- **Top K** - Number of documents to retrieve (1-10)
- **Similarity Threshold** - Minimum score to include (0.0-1.0)

## Troubleshooting

### "Found 0 similar documents"

Your documents aren't in Qdrant. Check the **Documents** tab to see:
1. If files exist in `backend/data/documents/`
2. If Qdrant collection has any vectors
3. If ingestion was successful

### Connection Errors

Make sure you're on a network where Qdrant Cloud is accessible (not corporate proxy).

### Import Errors

```powershell
pip install streamlit plotly pandas
```

## Tips

- **Use this instead of terminal logs** - Much easier to read and debug
- **Test different models** - See which gives better answers
- **Tune retrieval** - Adjust Top K and threshold to improve results
- **Monitor conversations** - See what users are asking

---

**Pro Tip**: Leave this running while developing. It's like a debug console for your RAG system! 🚀
