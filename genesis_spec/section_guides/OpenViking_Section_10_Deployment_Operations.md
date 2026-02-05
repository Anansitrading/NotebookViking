# OpenViking Genesis Specification - Section 10: Deployment & Operations

**Version**: 1.0.0
**Last Updated**: 2026-02-05
**Status**: Production Ready

---

## 10.1 Deployment Architecture

### Deployment Modes

```
+------------------------------------------------------------------+
|                    OPENVIKING DEPLOYMENT MODES                    |
+------------------------------------------------------------------+

+---------------------------+     +---------------------------+
|     EMBEDDED MODE         |     |     SERVICE MODE          |
+---------------------------+     +---------------------------+
|  - Single Python process  |     |  - Standalone service     |
|  - Direct library import  |     |  - HTTP/gRPC API          |
|  - Local storage only     |     |  - Multi-client support   |
|  - AsyncOpenViking()      |     |  - Container-ready        |
+---------------------------+     +---------------------------+
        |                                   |
        v                                   v
+---------------------------+     +---------------------------+
|    USE CASES              |     |    USE CASES              |
|  - Jupyter notebooks      |     |  - Production services    |
|  - CLI applications       |     |  - Microservice arch      |
|  - Local AI assistants    |     |  - Team deployments       |
+---------------------------+     +---------------------------+
```

### Component Dependencies

```
+------------------------------------------------------------------+
|                     RUNTIME DEPENDENCIES                          |
+------------------------------------------------------------------+

Required:
+-------------------+     +-------------------+     +-------------------+
|   Python 3.9+     |     |      AGFS         |     |    VikingDB       |
|   (Runtime)       |     |  (File Storage)   |     | (Vector Storage)  |
+-------------------+     +-------------------+     +-------------------+

Optional:
+-------------------+     +-------------------+     +-------------------+
|   NotebookLM      |     |   Redis/Valkey    |     |    OpenAI API     |
|   (Alt Backend)   |     |  (Session Cache)  |     |   (Embeddings)    |
+-------------------+     +-------------------+     +-------------------+
```

---

## 10.2 Installation

### Package Installation

```bash
# From PyPI (when published)
pip install openviking

# From source
git clone https://github.com/volcengine/OpenViking.git
cd OpenViking
pip install -e ".[dev]"

# With optional dependencies
pip install openviking[notebooklm]  # NotebookLM backend
pip install openviking[audio]       # Audio parsing support
pip install openviking[video]       # Video parsing support
```

### AGFS Setup

```bash
# Start AGFS service (required)
agfs start --port 8080 --data-dir /path/to/storage

# Or use Docker
docker run -d \
  -p 8080:8080 \
  -v /data:/data \
  volcengine/agfs:latest
```

### Configuration

```bash
# Set environment variables
export OPENVIKING_CONFIG_FILE=/path/to/config.json
export OPENAI_API_KEY=sk-...

# Or use config file
cat > ~/.openviking/config.json << EOF
{
  "user": "default_user",
  "storage": {
    "agfs_host": "localhost",
    "agfs_port": 8080,
    "agfs_data_path": "/data/openviking"
  },
  "embedding": {
    "backend": "openai",
    "model": "text-embedding-3-small"
  }
}
EOF
```

---

## 10.3 Docker Deployment

### Dockerfile

```dockerfile
# Dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY openviking/ ./openviking/
COPY setup.py .

# Install package
RUN pip install -e .

# Create data directories
RUN mkdir -p /data/openviking /data/agfs

# Expose ports
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s \
  CMD curl -f http://localhost:8000/health || exit 1

# Start command
CMD ["python", "-m", "openviking.server", "--host", "0.0.0.0", "--port", "8000"]
```

### Docker Compose

```yaml
# docker-compose.yml
version: '3.8'

services:
  openviking:
    build: .
    ports:
      - "8000:8000"
    environment:
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - OPENVIKING_LOG_LEVEL=INFO
    volumes:
      - openviking-data:/data/openviking
    depends_on:
      - agfs
    restart: unless-stopped

  agfs:
    image: volcengine/agfs:latest
    ports:
      - "8080:8080"
    volumes:
      - agfs-data:/data
    restart: unless-stopped

volumes:
  openviking-data:
  agfs-data:
```

### Container Commands

```bash
# Build and start
docker-compose up -d --build

# View logs
docker-compose logs -f openviking

# Stop
docker-compose down

# With persistence cleanup
docker-compose down -v
```

---

## 10.4 Environment Configuration

### Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `OPENVIKING_CONFIG_FILE` | No | `~/.openviking/config.json` | Config file path |
| `OPENVIKING_EMBEDDING_API_KEY` | Yes* | - | Embedding service key |
| `OPENAI_API_KEY` | Yes* | - | OpenAI API key (fallback) |
| `ARK_API_KEY` | Yes* | - | Volcengine key (fallback) |
| `OPENVIKING_LOG_LEVEL` | No | `WARNING` | Log verbosity |
| `OPENVIKING_DATA_PATH` | No | `./data` | Local data directory |

*One of the API key variables required for embeddings.

### Configuration File Schema

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "type": "object",
  "properties": {
    "user": {"type": "string"},
    "storage": {
      "type": "object",
      "properties": {
        "agfs_host": {"type": "string", "default": "localhost"},
        "agfs_port": {"type": "integer", "default": 8080},
        "agfs_data_path": {"type": "string"}
      }
    },
    "storage_backend": {
      "type": "string",
      "enum": ["vikingdb", "notebooklm"],
      "default": "vikingdb"
    },
    "embedding": {
      "type": "object",
      "properties": {
        "backend": {"type": "string", "enum": ["openai", "volcengine"]},
        "model": {"type": "string"},
        "api_key": {"type": "string"}
      }
    },
    "log_level": {
      "type": "string",
      "enum": ["DEBUG", "INFO", "WARNING", "ERROR"],
      "default": "WARNING"
    }
  }
}
```

---

## 10.5 Operations Runbook

### Startup Sequence

```
1. Start AGFS service
   $ agfs start --port 8080

2. Verify AGFS health
   $ curl http://localhost:8080/health

3. Start OpenViking (embedded)
   >>> from openviking import AsyncOpenViking
   >>> client = AsyncOpenViking()
   >>> await client.initialize()

4. Verify client health
   >>> await client.health_check()
```

### Shutdown Sequence

```
1. Stop accepting new requests

2. Wait for queue processing
   >>> await client.wait_processed(timeout=60)

3. Close client connections
   >>> await client.close()

4. Stop AGFS service
   $ agfs stop
```

### Backup Procedures

```bash
# Backup AGFS data
tar -czvf backup-agfs-$(date +%Y%m%d).tar.gz /data/agfs

# Export OpenViking collections
python -c "
import asyncio
from openviking import AsyncOpenViking

async def backup():
    client = AsyncOpenViking()
    await client.initialize()
    await client.export_ovpack('viking://resources/', '/backups/resources.ovpack')
    await client.export_ovpack('viking://user/', '/backups/user.ovpack')
    await client.close()

asyncio.run(backup())
"

# Verify backup integrity
ls -la /backups/*.ovpack
```

### Recovery Procedures

```bash
# Restore AGFS data
tar -xzvf backup-agfs-20260205.tar.gz -C /data/

# Import OpenViking collections
python -c "
import asyncio
from openviking import AsyncOpenViking

async def restore():
    client = AsyncOpenViking()
    await client.initialize()
    await client.import_ovpack('/backups/resources.ovpack', 'viking://resources/', force=True, vectorize=True)
    await client.import_ovpack('/backups/user.ovpack', 'viking://user/', force=True, vectorize=True)
    await client.close()

asyncio.run(restore())
"
```

---

## 10.6 Scaling Considerations

### Vertical Scaling

| Resource | Recommendation | Impact |
|----------|----------------|--------|
| CPU | 4+ cores | Faster parsing, embedding |
| Memory | 8GB+ | Larger queue buffers |
| Storage | SSD | Faster AGFS operations |
| Network | Low latency | Faster API calls |

### Horizontal Scaling

```
Current Limitations:
- Single AGFS instance (no distributed mode)
- Singleton client pattern (single process)
- In-memory queues (not distributed)

Future Scaling:
- Distributed AGFS with replication
- Load-balanced API service
- Redis/Valkey queue backend
- Vector database clustering
```

### Performance Tuning

```python
# Increase queue workers
config = {
    "queue": {
        "semantic_workers": 4,      # Default: 2
        "embedding_workers": 8,     # Default: 4
        "max_queue_size": 10000     # Default: 1000
    }
}

# Batch processing
config = {
    "embedding": {
        "batch_size": 100,          # Default: 50
        "max_concurrent": 10        # Default: 5
    }
}

# Memory optimization
config = {
    "parse": {
        "max_file_size_mb": 50,     # Default: 100
        "chunk_size_tokens": 512    # Default: 1024
    }
}
```

---

## 10.7 Maintenance Tasks

### Daily Tasks

| Task | Command | Schedule |
|------|---------|----------|
| Health check | `curl /health` | Every 5 min |
| Log rotation | `logrotate /etc/logrotate.d/openviking` | Daily |
| Queue monitoring | `client.observers["queue"].get_status_table()` | Hourly |

### Weekly Tasks

| Task | Command | Schedule |
|------|---------|----------|
| Index optimization | `await client._vikingdb_manager.optimize("context")` | Weekly |
| Storage cleanup | `find /data -mtime +30 -delete` | Weekly |
| Backup verification | `tar -tvf backup.tar.gz` | Weekly |

### Monthly Tasks

| Task | Command | Schedule |
|------|---------|----------|
| Full backup | See backup procedures | Monthly |
| Performance review | Check metrics dashboard | Monthly |
| Dependency updates | `pip install -U openviking` | Monthly |

---

## 10.8 Troubleshooting

### Common Issues

| Issue | Symptom | Resolution |
|-------|---------|------------|
| AGFS not running | Connection refused | Start AGFS service |
| API key invalid | 401 Unauthorized | Check environment variables |
| Queue blocked | Items stuck in pending | Check error logs, restart workers |
| Memory exhausted | OOM errors | Reduce batch size, increase RAM |
| Slow searches | High latency | Optimize indexes, check network |

### Diagnostic Commands

```bash
# Check AGFS status
curl http://localhost:8080/health

# Check OpenViking logs
tail -f /var/log/openviking/app.log

# Check queue status
python -c "
from openviking import AsyncOpenViking
import asyncio

async def status():
    client = AsyncOpenViking()
    await client.initialize()
    print(client.observers['queue'].get_status_table())
    await client.close()

asyncio.run(status())
"

# Check vector storage
python -c "
from openviking import AsyncOpenViking
import asyncio

async def stats():
    client = AsyncOpenViking()
    await client.initialize()
    print(await client._vikingdb_manager.get_stats())
    await client.close()

asyncio.run(stats())
"
```

---

## 10.9 Quality Checklist

- [x] Installation documented
- [x] Docker deployment ready
- [x] Environment configuration complete
- [x] Operations runbook provided
- [x] Scaling considerations noted
- [x] Troubleshooting guide included
