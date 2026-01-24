---
title: Portfolio RAG Chatbot
emoji: 💬
colorFrom: blue
colorTo: indigo
sdk: docker
pinned: false
license: mit
---

# Portfolio RAG Chatbot

A professional RAG-powered chatbot for portfolio websites.

## Features

- **Retrieval-Augmented Generation**: Uses Voyage AI embeddings and Qdrant vector store
- **LLM Inference**: Powered by Groq API with Llama 3.3 70B
- **Streaming Responses**: Real-time streaming for better UX
- **Production Logging**: Comprehensive logging for monitoring and debugging
- **Embeddable Widget**: Easy-to-embed chat widget for any website

## API Endpoints

- `GET /api/v1/health` - Health check
- `POST /api/v1/chat` - Send a chat message
- `POST /api/v1/chat/stream` - Send a chat message with streaming response
- `GET /api/v1/stats` - Get vector store statistics

## Environment Variables

Configure the following secrets in your HuggingFace Space:

- `GROQ_API_KEY` - Groq API key
- `VOYAGE_API_KEY` - Voyage AI API key
- `QDRANT_URL` - Qdrant Cloud cluster URL
- `QDRANT_API_KEY` - Qdrant Cloud API key
- `QDRANT_COLLECTION_NAME` - Collection name (default: portfolio)
- `CORS_ORIGINS` - Comma-separated list of allowed origins
- `APP_ENV` - Environment (development/production)
- `LOG_LEVEL` - Logging level (DEBUG/INFO/WARNING/ERROR)
