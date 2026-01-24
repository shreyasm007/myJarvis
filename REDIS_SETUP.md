# Redis Setup Guide

Redis is used for caching embeddings to reduce API calls and improve response times.

## Installation

### Windows (Recommended: Docker)

```powershell
# Install Docker Desktop from https://www.docker.com/products/docker-desktop/

# Run Redis container
docker run -d -p 6379:6379 --name myjarvis-redis redis:latest
```

### Windows (Alternative: MSI Installer)

1. Download Redis for Windows: https://github.com/microsoftarchive/redis/releases
2. Install and start Redis service
3. Default port: 6379

### Linux/Mac

```bash
# Ubuntu/Debian
sudo apt-get install redis-server
sudo systemctl start redis-server

# macOS
brew install redis
brew services start redis
```

## Testing Connection

```powershell
# Test if Redis is running
redis-cli ping
# Should return: PONG

# Or use Python
python -c "import redis; r=redis.Redis(); print(r.ping())"
```

## Configuration

Redis URL in `.env` (optional, defaults to localhost):

```env
REDIS_URL=redis://localhost:6379/0
```

## Cache Statistics

The system caches:
- **Query embeddings**: 7 days TTL (frequently asked questions)
- **Document embeddings**: 30 days TTL (rarely change)

### Benefits

**Without Redis:**
- Every query = API call to Voyage AI
- 10 queries/min = 600 embedding calls/hour
- Slow response times (300-500ms per embedding)

**With Redis:**
- Repeated queries = instant (0ms)
- ~80% cache hit rate for common questions
- Saves API quota and money

### Cache Keys

```
emb:<hash>  # Embedding cache
Format: emb:sha256(model:input_type:text)
```

## Management

```powershell
# Clear all embedding cache
redis-cli --scan --pattern "emb:*" | redis-cli DEL

# Monitor cache activity
redis-cli MONITOR

# Check memory usage
redis-cli INFO memory
```

## Production Notes

- **Redis is optional** - System works without it (slower)
- Falls back gracefully if Redis unavailable
- For production, use Redis Cloud or managed service
- Enable persistence for crash recovery

## Disabling Cache

Set in embeddings client initialization:

```python
embeddings_client = EmbeddingsClient(use_cache=False)
```

Or remove Redis to auto-disable caching.
