# Deployment Guide

## Quick Start

### 1. Set Up API Keys

Create accounts and get API keys for:

1. **Groq** (https://console.groq.com)
   - Sign up → API Keys → Create API Key
   
2. **Voyage AI** (https://www.voyageai.com)
   - Sign up → Dashboard → API Keys
   
3. **Qdrant Cloud** (https://cloud.qdrant.io)
   - Sign up → Create Cluster → Get URL and API Key

### 2. Configure Environment

Copy `.env.example` to `.env` and fill in your keys:

```bash
cp .env.example .env
```

Edit `.env`:
```
GROQ_API_KEY=gsk_your_key_here
VOYAGE_API_KEY=pa-your_key_here
QDRANT_URL=https://your-cluster.cloud.qdrant.io
QDRANT_API_KEY=your_qdrant_key_here
```

### 3. Prepare Your Documents

Replace `backend/data/documents/sample_portfolio.md` with your actual portfolio content.

You can add multiple files (`.txt`, `.md`). The ingestion script will process all of them.

### 4. Ingest Documents

```bash
# Activate virtual environment
.venv\Scripts\activate  # Windows
# or
source .venv/bin/activate  # Linux/Mac

# Run ingestion
python -m scripts.ingest
```

### 5. Test Locally

```bash
uvicorn backend.main:app --reload
```

Visit `http://localhost:8000/docs` to test the API.

---

## Deploy to HuggingFace Spaces

### 1. Create a Space

1. Go to https://huggingface.co/spaces
2. Click "Create new Space"
3. Name: `portfolio-chatbot` (or your choice)
4. SDK: **Docker**
5. Click "Create Space"

### 2. Add Secrets

In your Space → Settings → Repository secrets, add:

| Secret Name | Value |
|------------|-------|
| GROQ_API_KEY | Your Groq API key |
| VOYAGE_API_KEY | Your Voyage AI API key |
| QDRANT_URL | Your Qdrant cluster URL |
| QDRANT_API_KEY | Your Qdrant API key |
| QDRANT_COLLECTION_NAME | portfolio |
| CORS_ORIGINS | https://your-portfolio-site.com,https://huggingface.co |
| APP_ENV | production |
| LOG_LEVEL | INFO |

### 3. Push Code

**Option A: Git CLI**
```bash
git remote add hf https://huggingface.co/spaces/YOUR_USERNAME/portfolio-chatbot
git push hf main
```

**Option B: HuggingFace Hub CLI**
```bash
pip install huggingface_hub
huggingface-cli login
huggingface-cli upload YOUR_USERNAME/portfolio-chatbot . . --repo-type space
```

### 4. Wait for Build

Your Space will build automatically. Check the "Logs" tab for progress.

Once running, your API will be at:
```
https://YOUR_USERNAME-portfolio-chatbot.hf.space
```

---

## Embed the Widget

Add this script tag to your portfolio website:

```html
<script 
  src="https://YOUR_USERNAME-portfolio-chatbot.hf.space/widget/chat-widget.js"
  data-api-url="https://YOUR_USERNAME-portfolio-chatbot.hf.space"
  data-title="Ask me anything!"
  data-primary-color="#4F46E5"
  data-position="right">
</script>
```

### Widget Options

| Attribute | Description | Default |
|-----------|-------------|---------|
| data-api-url | Your HF Space URL | Required |
| data-title | Chat window title | "Chat with me" |
| data-placeholder | Input placeholder | "Type your message..." |
| data-primary-color | Theme color | "#4F46E5" |
| data-position | "left" or "right" | "right" |

---

## API Reference

### Health Check
```
GET /api/v1/health
```

### Chat (Non-streaming)
```
POST /api/v1/chat
Content-Type: application/json

{
  "message": "What skills do you have?",
  "conversation_id": "optional-uuid"
}
```

### Chat (Streaming)
```
POST /api/v1/chat/stream
Content-Type: application/json

{
  "message": "Tell me about your experience"
}
```

Returns Server-Sent Events (SSE).

### Stats
```
GET /api/v1/stats
```

---

## Troubleshooting

### "No relevant context found"

Your documents haven't been ingested yet, or the query doesn't match any content.

**Solution:** Run the ingestion script with your portfolio content.

### CORS Errors

Your portfolio site isn't in the allowed origins.

**Solution:** Add your site to `CORS_ORIGINS` in HF Space secrets.

### Rate Limit Errors

Groq has rate limits on the free tier.

**Solution:** Wait a minute and try again, or implement request queuing.

### Widget Not Showing

Check browser console for JavaScript errors.

**Solution:** Ensure the script URL is correct and CORS is configured.

---

## Architecture

```
┌─────────────────┐     ┌──────────────────────────────────────┐
│  Your Website   │     │         HuggingFace Space            │
│  (Portfolio)    │────▶│  ┌──────────────────────────────┐   │
│                 │     │  │      FastAPI Backend         │   │
│  Chat Widget    │     │  │  ┌─────────┐ ┌───────────┐  │   │
│  (JavaScript)   │     │  │  │ Voyage  │ │   Groq    │  │   │
└─────────────────┘     │  │  │   AI    │ │    LLM    │  │   │
                        │  │  └────┬────┘ └─────┬─────┘  │   │
                        │  │       │            │        │   │
                        │  │  ┌────▼────────────▼────┐   │   │
                        │  │  │    RAG Chain         │   │   │
                        │  │  └─────────┬───────────┘   │   │
                        │  └────────────│───────────────┘   │
                        └───────────────│───────────────────┘
                                        │
                        ┌───────────────▼───────────────┐
                        │      Qdrant Cloud             │
                        │      (Vector Database)        │
                        └───────────────────────────────┘
```

---

## Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Run with hot reload
uvicorn backend.main:app --reload

# View logs
tail -f logs/app.log
```

---

## License

MIT License - Feel free to use this for your portfolio!
