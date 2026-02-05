# OpenViking Genesis Specification - Section 09: Monitoring & Observability

**Version**: 1.0.0
**Last Updated**: 2026-02-05
**Status**: Production Ready

---

## 9.1 Observability Architecture

### Three Pillars

```
+------------------------------------------------------------------+
|                    OPENVIKING OBSERVABILITY                       |
+------------------------------------------------------------------+

+-------------------+    +-------------------+    +-------------------+
|      LOGS         |    |     METRICS       |    |     TRACES        |
+-------------------+    +-------------------+    +-------------------+
| - Operation logs  |    | - Queue stats     |    | - Retrieval path  |
| - Error details   |    | - Collection info |    | - Search journey  |
| - Debug info      |    | - Token usage     |    | - Processing flow |
+-------------------+    +-------------------+    +-------------------+
        |                        |                        |
        v                        v                        v
+------------------------------------------------------------------+
|                        OBSERVER SYSTEM                            |
|  +----------------+  +----------------+  +----------------+       |
|  | QueueObserver  |  |VikingDBObserver|  |  VLMObserver   |       |
|  +----------------+  +----------------+  +----------------+       |
+------------------------------------------------------------------+
```

---

## 9.2 Logging

### Log Levels

| Level | Usage | Example |
|-------|-------|---------|
| DEBUG | Detailed internal state | `Embedding vector dim: 1024` |
| INFO | Normal operations | `Created collection: context` |
| WARNING | Non-fatal issues | `Collection already exists` |
| ERROR | Operation failures | `Failed to connect to AGFS` |
| CRITICAL | System failures | `Storage backend unavailable` |

### Logger Configuration

```python
# openviking/utils/__init__.py

import logging

def get_logger(name: str) -> logging.Logger:
    """Get configured logger for module."""
    logger = logging.getLogger(name)
    return logger

# Configuration from OpenVikingConfig
config = {
    "log_level": "WARNING",
    "log_format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    "log_output": "stdout"
}
```

### Structured Logging Pattern

```python
# Good logging examples
logger.info(f"Added resource: uri={uri}, count={count}")
logger.warning(f"Collection '{name}' already exists, skipping creation")
logger.error(f"Failed to parse file: path={path}, error={str(e)}")

# Debug with context
logger.debug(f"Search parameters: query={query[:50]}, limit={limit}, filter={filter}")
```

### Log Sanitization

```python
# NEVER log sensitive data
# Bad:
logger.debug(f"API key: {api_key}")

# Good:
logger.debug(f"API key configured: {bool(api_key)}")
```

---

## 9.3 Metrics

### Queue Metrics

```python
class QueueObserver(BaseObserver):
    """Monitors queue processing status."""

    def get_status_table(self) -> pd.DataFrame:
        """
        Returns DataFrame with columns:
        - queue_name: str
        - pending: int
        - in_progress: int
        - processed: int
        - error_count: int
        - errors: List[str]
        """
```

### VikingDB Metrics

```python
class VikingDBObserver(BaseObserver):
    """Monitors vector storage status."""

    def get_status_table(self) -> pd.DataFrame:
        """
        Returns DataFrame with columns:
        - collection_name: str
        - record_count: int
        - index_count: int
        - vector_dim: int
        - status: str
        """
```

### Token Usage Metrics

```python
class TokenUsageTracker:
    """Tracks LLM token consumption."""

    def get_token_usage() -> Dict:
        """
        Returns:
        {
            "openai": {
                "gpt-4o-mini": {
                    "prompt_tokens": int,
                    "completion_tokens": int
                }
            },
            "volcengine": {...}
        }
        """

    def get_token_usage_summary() -> Dict:
        """
        Returns:
        {
            "total_prompt_tokens": int,
            "total_completion_tokens": int,
            "total_tokens": int,
            "by_backend": {...}
        }
        """
```

---

## 9.4 Distributed Tracing

### Retrieval Trace

```python
class ThinkingTrace:
    """Captures retrieval decision path."""

    steps: List[TraceStep]

    class TraceStep:
        action: str          # "global_search", "recursive_search", "rerank"
        input: Dict          # Query, filters
        output: Dict         # Results, scores
        duration_ms: float   # Processing time
        metadata: Dict       # Additional context
```

### Trace Example

```python
# Accessing trace in search results
results = await client.find("what is this project")

if results.trace:
    for step in results.trace.steps:
        print(f"Step: {step.action}")
        print(f"  Duration: {step.duration_ms}ms")
        print(f"  Results: {len(step.output.get('results', []))}")
```

### Queue Processing Trace

```
SemanticMsg enqueued
    |
    +-> SemanticProcessor.on_dequeue()
         |
         +-> VikingFS.ls() [10ms]
         +-> Generate abstract [200ms]
         +-> Generate overview [150ms]
         +-> EmbeddingMsg enqueued
              |
              +-> TextEmbeddingHandler.on_dequeue()
                   |
                   +-> Embedder.embed() [50ms]
                   +-> VikingDB.insert() [20ms]
```

---

## 9.5 Health Checks

### Client Health

```python
async def health_check() -> Dict[str, bool]:
    """Check all subsystem health."""
    return {
        "client_initialized": client._initialized,
        "viking_fs_ready": client._viking_fs is not None,
        "vikingdb_healthy": await client._vikingdb_manager.health_check(),
        "agfs_connected": client._agfs_manager.is_running(),
        "embedder_configured": client._embedder is not None
    }
```

### Observer Health

```python
class BaseObserver(ABC):
    @abstractmethod
    def is_healthy(self) -> bool:
        """Returns True if subsystem is healthy."""
        pass

    @abstractmethod
    def has_errors(self) -> bool:
        """Returns True if errors detected."""
        pass
```

### Liveness vs Readiness

| Check | Type | Failure Action |
|-------|------|----------------|
| AGFS running | Liveness | Restart process |
| Collections exist | Readiness | Wait for init |
| Queue not blocked | Liveness | Alert |
| Embedder responds | Readiness | Retry config |

---

## 9.6 Alerting

### Alert Conditions

| Condition | Severity | Threshold | Action |
|-----------|----------|-----------|--------|
| Queue error rate | HIGH | >5% | Investigate parsing |
| Queue backlog | MEDIUM | >1000 pending | Scale processing |
| API error rate | HIGH | >10% | Check credentials |
| Memory usage | MEDIUM | >80% RSS | Consider cleanup |
| Response latency | LOW | P95 >1s | Optimize queries |

### Manual Alert Check

```python
# Check for errors
observers = client.observers
for name, obs in observers.items():
    if obs.has_errors():
        print(f"ALERT: {name} has errors")
        print(obs.get_status_table())
```

---

## 9.7 Dashboards

### Queue Status Dashboard (pandas)

```python
# Get queue status
queue_obs = client.observers["queue"]
df = queue_obs.get_status_table()

# Display
print(df.to_string())

# Output:
#   queue_name    pending  in_progress  processed  error_count
# 0 semantic      0        0            150        2
# 1 embedding     5        1            145        0
```

### Collection Status Dashboard

```python
# Get storage status
vikingdb_obs = client.observers["vikingdb"]
df = vikingdb_obs.get_status_table()

# Output:
#   collection  record_count  index_count  vector_dim  status
# 0 context     1523          4            1024        active
```

### Token Usage Dashboard

```python
# Get token usage
vlm_obs = client.observers["vlm"]
summary = vlm_obs.get_token_usage_summary()

print(f"Total tokens used: {summary['total_tokens']}")
print(f"  Prompt: {summary['total_prompt_tokens']}")
print(f"  Completion: {summary['total_completion_tokens']}")
```

---

## 9.8 Quality Checklist

- [x] Logging strategy defined
- [x] Key metrics identified
- [x] Health checks documented
- [x] Alert conditions specified
- [x] Dashboard examples provided
- [x] Trace format documented
