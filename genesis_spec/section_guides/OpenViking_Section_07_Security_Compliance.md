# OpenViking Genesis Specification - Section 07: Security & Compliance

**Version**: 1.0.0
**Last Updated**: 2026-02-05
**Status**: Production Ready

---

## 7.1 Security Model

### Security Layers

```
+---------------------------------------------------------------+
|                      APPLICATION LAYER                         |
|  - Input validation (Pydantic models)                          |
|  - URI sanitization                                            |
|  - Query parameter validation                                  |
+---------------------------------------------------------------+
                              |
+---------------------------------------------------------------+
|                       SERVICE LAYER                            |
|  - API key management (environment variables)                  |
|  - Rate limiting (external service quotas)                     |
|  - Timeout controls                                            |
+---------------------------------------------------------------+
                              |
+---------------------------------------------------------------+
|                       STORAGE LAYER                            |
|  - File path validation (AGFS)                                 |
|  - Collection isolation                                        |
|  - No direct SQL (DSL-based filtering)                         |
+---------------------------------------------------------------+
                              |
+---------------------------------------------------------------+
|                      NETWORK LAYER                             |
|  - HTTPS for external APIs                                     |
|  - Local-only AGFS by default                                  |
|  - No credential transmission in logs                          |
+---------------------------------------------------------------+
```

---

## 7.2 Threat Model

### STRIDE Analysis

| Threat | Category | Risk | Mitigation |
|--------|----------|------|------------|
| API key exposure | Spoofing | HIGH | Env vars only, no logging |
| Malicious file upload | Tampering | MEDIUM | Content validation, sandboxed parsing |
| Path traversal | Information Disclosure | MEDIUM | URI validation, prefix checks |
| Denial of service | DoS | LOW | Timeout limits, queue capacity |
| Prompt injection | Elevation | MEDIUM | Input sanitization, output validation |
| Vector manipulation | Tampering | LOW | Immutable embeddings, hash verification |

### Trust Boundaries

```
+------------------+     +------------------+     +------------------+
|   Untrusted      |     |    Partially     |     |     Trusted      |
|                  |     |    Trusted       |     |                  |
|  - User input    |---->|  - Parsed files  |---->|  - VikingDB      |
|  - URLs          |     |  - LLM output    |     |  - AGFS local    |
|  - File content  |     |  - Embeddings    |     |  - Config        |
+------------------+     +------------------+     +------------------+
```

---

## 7.3 Authentication

### API Key Management

```python
# Supported environment variables
OPENVIKING_CONFIG_FILE        # Path to config JSON
OPENVIKING_EMBEDDING_API_KEY  # Embedding service key
OPENAI_API_KEY                # OpenAI fallback
ARK_API_KEY                   # Volcengine fallback
```

### Key Priority Resolution

```python
def resolve_api_key():
    # 1. Config file explicit key
    if config.embedding.api_key:
        return config.embedding.api_key

    # 2. OpenViking-specific env var
    if os.getenv("OPENVIKING_EMBEDDING_API_KEY"):
        return os.getenv("OPENVIKING_EMBEDDING_API_KEY")

    # 3. Service-specific env var
    if config.embedding.backend == "openai":
        return os.getenv("OPENAI_API_KEY")
    elif config.embedding.backend == "volcengine":
        return os.getenv("ARK_API_KEY")

    raise ValueError("No API key configured")
```

### NotebookLM Authentication

- Uses browser cookies stored by `notebooklm-mcp-auth` CLI
- Credentials stored in `~/.notebooklm-mcp/` directory
- Subprocess isolation prevents credential leakage

---

## 7.4 Authorization

### Access Control Model

OpenViking uses a **single-user model** with scope-based organization:

| Scope | Access | Purpose |
|-------|--------|---------|
| `viking://user/` | User-owned | Personal memories, preferences |
| `viking://agent/` | Agent-owned | Skills, task memories |
| `viking://resources/` | Shared | Documents, repos, web pages |
| `viking://session/` | Session-scoped | Conversation history |

### Permission Enforcement

```python
# URI validation ensures scope boundaries
def validate_uri(uri: str) -> bool:
    parsed = VikingURI(uri)
    valid_scopes = ["user", "agent", "resources", "session"]
    return parsed.scope in valid_scopes
```

### No Multi-Tenancy

- Current design: Single user per OpenViking instance
- No user-to-user isolation
- No role-based access control
- Suitable for: Personal AI assistants, single-agent systems

---

## 7.5 Data Protection

### Sensitive Data Handling

| Data Type | Protection Method |
|-----------|-------------------|
| API keys | Environment variables, never logged |
| Session content | Local storage only, not transmitted |
| Embeddings | Sent to external API over HTTPS |
| User memories | Stored locally, no cloud sync |
| File content | Processed locally, parsed results stored |

### Encryption

- **In Transit**: HTTPS for all external API calls
- **At Rest**: No built-in encryption (relies on filesystem)
- **Recommendation**: Use encrypted filesystem for sensitive deployments

### Data Sanitization

```python
# Content sanitization before LLM processing
def sanitize_for_llm(content: str) -> str:
    # Remove potential prompt injection patterns
    content = content.replace("```system", "")
    content = content.replace("[INST]", "")
    # Truncate to prevent context overflow
    if len(content) > MAX_CONTENT_LENGTH:
        content = content[:MAX_CONTENT_LENGTH] + "..."
    return content
```

---

## 7.6 Audit Logging

### Log Levels

| Level | Content | Sensitivity |
|-------|---------|-------------|
| DEBUG | Internal state, URIs | Low |
| INFO | Operations completed | Low |
| WARNING | Non-fatal errors | Low |
| ERROR | Operation failures | Medium |

### What is NOT Logged

- API keys (masked or excluded)
- Full message content (only metadata)
- Personal identifiers
- Raw file content

### Log Configuration

```python
# Default safe logging
log_level: str = "WARNING"  # Minimal by default
log_format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
log_output: str = "stdout"  # No file persistence by default
```

---

## 7.7 Compliance Requirements

### Data Residency

- **Local Mode**: All data stays on local filesystem
- **Service Mode**: Data transmitted to configured endpoints
- **External APIs**: Check provider data residency policies

### GDPR Considerations

| Requirement | Implementation |
|-------------|----------------|
| Right to Access | Export via `.ovpack` files |
| Right to Erasure | `rm` command with `recursive=True` |
| Data Minimization | L0/L1 summarization reduces stored content |
| Purpose Limitation | Scope-based organization |

### PII Handling

- No automatic PII detection
- User responsible for content classification
- Recommendation: Don't store sensitive PII in memories

---

## 7.8 Quality Checklist

- [x] Threat model documented
- [x] Auth/authz explained
- [x] Data protection specified
- [x] Audit requirements defined
- [x] Compliance considerations noted
- [x] No credentials in code or logs
