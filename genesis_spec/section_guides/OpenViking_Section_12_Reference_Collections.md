# OpenViking Genesis Specification - Section 12: Reference Collections

**Version**: 1.0.0
**Last Updated**: 2026-02-05
**Status**: Production Ready

---

## 12.1 Code Examples Collection

### Basic Operations

```python
# examples/basic_operations.py
"""Basic OpenViking operations examples."""

import asyncio
from openviking import AsyncOpenViking


async def initialization_example():
    """Initialize and close client properly."""
    client = AsyncOpenViking()
    await client.initialize()

    # ... operations ...

    await client.close()


async def add_resource_examples():
    """Various ways to add resources."""
    client = AsyncOpenViking()
    await client.initialize()

    # Add local file
    result = await client.add_resource(
        path="./documents/readme.md",
        wait=True
    )
    print(f"File added: {result['root_uri']}")

    # Add URL
    result = await client.add_resource(
        path="https://docs.example.com/guide",
        wait=True,
        timeout=60.0
    )

    # Add directory recursively
    result = await client.add_resource(
        path="./project/src/",
        reason="Project source code for context",
        wait=True
    )

    # Add with custom target
    result = await client.add_resource(
        path="./notes.md",
        target="viking://user/notes/personal",
        wait=True
    )

    await client.close()


async def search_examples():
    """Semantic search patterns."""
    client = AsyncOpenViking()
    await client.initialize()

    # Basic search
    results = await client.find("authentication implementation")

    # Scoped search
    results = await client.find(
        query="error handling",
        target_uri="viking://resources/my_project/"
    )

    # With filters
    results = await client.find(
        query="configuration",
        filter={
            "op": "must",
            "field": "context_type",
            "conds": ["resource"]
        },
        limit=5,
        score_threshold=0.3
    )

    # Process results
    for ctx in results.resources:
        print(f"{ctx.title} (score: {ctx.score:.2f})")
        print(f"  URI: {ctx.uri}")
        print(f"  Abstract: {ctx.abstract[:100]}...")

    await client.close()


async def filesystem_examples():
    """File system operations."""
    client = AsyncOpenViking()
    await client.initialize()

    # List directory
    entries = await client.ls("viking://resources/")
    for entry in entries:
        print(f"{entry['name']} - {entry['type']}")

    # Read content
    content = await client.read("viking://resources/project/readme")
    print(content)

    # Get summaries
    abstract = await client.abstract("viking://resources/project/")
    overview = await client.overview("viking://resources/project/")

    # Tree view
    tree = await client.tree("viking://resources/")
    print(tree)

    # Create directory
    await client.mkdir("viking://user/notes/work")

    # Move context
    await client.mv(
        "viking://user/notes/old",
        "viking://user/archive/old"
    )

    # Remove (with confirmation for recursive)
    await client.rm("viking://user/archive/old", recursive=True)

    await client.close()


if __name__ == "__main__":
    asyncio.run(initialization_example())
```

### Session Management

```python
# examples/session_management.py
"""Session and memory extraction examples."""

import asyncio
from openviking import AsyncOpenViking


async def basic_session():
    """Basic session usage."""
    client = AsyncOpenViking()
    await client.initialize()

    session = client.session("conversation_001")

    # Add messages
    await session.add_message("user", "How do I implement caching?")
    await session.add_message(
        "assistant",
        "For caching, consider Redis with TTL-based expiration..."
    )
    await session.add_message("user", "Thanks, I prefer Valkey actually")
    await session.add_message(
        "assistant",
        "Valkey works great! Here's a Valkey-specific implementation..."
    )

    # Commit and extract memories
    memories = await session.commit()

    for memory in memories:
        print(f"Category: {memory.category}")
        print(f"Title: {memory.title}")
        print(f"Priority: {memory.priority}")
        print(f"Content: {memory.l0}")
        print("---")

    await client.close()


async def session_with_context():
    """Session with context retrieval."""
    client = AsyncOpenViking()
    await client.initialize()

    session = client.session("task_session")

    # Search and include context
    results = await client.search(
        query="authentication patterns",
        session=session,  # Attaches context to session
        limit=3
    )

    # Context is automatically included
    context = session.get_context()
    print(f"Session has {len(context)} context items")

    await session.add_message("user", "Implement auth using these patterns")
    await session.add_message("assistant", "[Implementation using context]")

    await session.commit()
    await client.close()


async def session_compression():
    """Long session with compression."""
    client = AsyncOpenViking()
    await client.initialize()

    session = client.session("long_conversation")

    # Add many messages
    for i in range(50):
        await session.add_message("user", f"Question {i}: ...")
        await session.add_message("assistant", f"Answer {i}: ...")

    # Check compression status
    stats = session.get_stats()
    print(f"Messages: {stats['message_count']}")
    print(f"Token estimate: {stats['estimated_tokens']}")
    print(f"Compressed: {stats['compression_active']}")

    # Force compression
    await session.compress()

    # Archived messages moved to history
    print(f"Archives: {stats['archive_count']}")

    await client.close()


if __name__ == "__main__":
    asyncio.run(basic_session())
```

### Relations and Links

```python
# examples/relations.py
"""Context linking and relations examples."""

import asyncio
from openviking import AsyncOpenViking


async def link_contexts():
    """Create relationships between contexts."""
    client = AsyncOpenViking()
    await client.initialize()

    # Link related resources
    await client.link(
        from_uri="viking://resources/auth_service/",
        uris=[
            "viking://resources/user_service/",
            "viking://resources/session_service/"
        ],
        reason="Services that interact with authentication"
    )

    # Get relations
    relations = await client.relations("viking://resources/auth_service/")
    for rel in relations:
        print(f"Related: {rel['uri']} - {rel['reason']}")

    # Remove link
    await client.unlink(
        from_uri="viking://resources/auth_service/",
        uri="viking://resources/session_service/"
    )

    await client.close()


if __name__ == "__main__":
    asyncio.run(link_contexts())
```

### Import/Export

```python
# examples/import_export.py
"""OVPack import and export examples."""

import asyncio
from openviking import AsyncOpenViking


async def export_knowledge():
    """Export knowledge to portable format."""
    client = AsyncOpenViking()
    await client.initialize()

    # Export specific collection
    pack_path = await client.export_ovpack(
        uri="viking://resources/my_project/",
        to="/backups/my_project.ovpack"
    )
    print(f"Exported to: {pack_path}")

    # Export all user memories
    await client.export_ovpack(
        uri="viking://user/",
        to="/backups/user_memories.ovpack"
    )

    await client.close()


async def import_knowledge():
    """Import knowledge from OVPack."""
    client = AsyncOpenViking()
    await client.initialize()

    # Import to new location
    uri = await client.import_ovpack(
        file_path="/backups/my_project.ovpack",
        parent="viking://resources/imported/",
        force=False,  # Don't overwrite existing
        vectorize=True  # Re-generate embeddings
    )
    print(f"Imported to: {uri}")

    await client.close()


if __name__ == "__main__":
    asyncio.run(export_knowledge())
```

---

## 12.2 Configuration Examples

### Minimal Configuration

```json
{
  "user": "default_user",
  "storage": {
    "agfs_host": "localhost",
    "agfs_port": 8080
  },
  "embedding": {
    "backend": "openai",
    "model": "text-embedding-3-small"
  }
}
```

### Full Configuration

```json
{
  "user": "production_user",

  "storage": {
    "agfs_host": "localhost",
    "agfs_port": 8080,
    "agfs_data_path": "/data/openviking"
  },

  "storage_backend": "vikingdb",

  "embedding": {
    "backend": "openai",
    "model": "text-embedding-3-large",
    "dimension": 3072,
    "batch_size": 100,
    "max_concurrent": 10
  },

  "vlm": {
    "backend": "openai",
    "model": "gpt-4o-mini",
    "temperature": 0.7,
    "max_tokens": 4096
  },

  "rerank": {
    "enabled": true,
    "model": "rerank-v2",
    "top_k": 20
  },

  "pdf": {
    "parser": "docling",
    "extract_images": true,
    "ocr_enabled": true
  },

  "code": {
    "parser": "tree-sitter",
    "languages": ["python", "javascript", "typescript"],
    "include_comments": true
  },

  "markdown": {
    "parser": "default",
    "extract_code_blocks": true
  },

  "html": {
    "parser": "readability",
    "extract_links": true
  },

  "auto_generate_l0": true,
  "auto_generate_l1": true,
  "default_search_mode": "thinking",
  "default_search_limit": 10,

  "enable_memory_decay": true,
  "memory_decay_check_interval": 3600,

  "log_level": "INFO",
  "log_format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
  "log_output": "stdout"
}
```

### NotebookLM Backend Configuration

```json
{
  "storage_backend": "notebooklm",

  "notebooklm": {
    "notebook_mapping": {
      "memories": "abc123-def456-ghi789",
      "resources": "xyz789-uvw456-rst123",
      "sessions": "session-notebook-id"
    },
    "default_notebook_id": "abc123-def456-ghi789",
    "tier_config": {
      "L0": 100,
      "L1": 2000,
      "L2": 100000
    },
    "source_naming_pattern": "{tier}-{context_type}-{uri_hash}-{title}-{status}"
  }
}
```

---

## 12.3 Error Codes Reference

### Client Errors (4xx)

| Code | Name | Description | Resolution |
|------|------|-------------|------------|
| `E4001` | InvalidURI | Malformed viking:// URI | Check URI format |
| `E4002` | ResourceNotFound | URI does not exist | Verify URI or create |
| `E4003` | InvalidQuery | Empty or invalid search query | Provide valid query |
| `E4004` | InvalidFilter | Malformed filter DSL | Check filter syntax |
| `E4005` | PermissionDenied | Operation not allowed | Check scope permissions |
| `E4006` | DuplicateResource | Resource already exists | Use force=True or different URI |
| `E4007` | InvalidConfig | Configuration error | Validate config file |
| `E4008` | UnsupportedFormat | File format not supported | Check supported parsers |

### Server Errors (5xx)

| Code | Name | Description | Resolution |
|------|------|-------------|------------|
| `E5001` | StorageUnavailable | VikingDB/AGFS not responding | Check service status |
| `E5002` | EmbeddingFailed | Embedding API error | Check API key, quotas |
| `E5003` | ParseFailed | Content parsing error | Check file format |
| `E5004` | QueueOverflow | Processing queue full | Wait or increase capacity |
| `E5005` | IndexCorrupted | Vector index issue | Rebuild index |
| `E5006` | Timeout | Operation timed out | Increase timeout or retry |
| `E5007` | InternalError | Unexpected error | Check logs, report bug |

### Error Handling Pattern

```python
from openviking import AsyncOpenViking
from openviking.exceptions import (
    OpenVikingError,
    ResourceNotFoundError,
    StorageUnavailableError,
    EmbeddingError
)

async def safe_operation():
    client = AsyncOpenViking()

    try:
        await client.initialize()
        results = await client.find("query")

    except ResourceNotFoundError as e:
        print(f"Resource not found: {e.uri}")
        # Handle missing resource

    except StorageUnavailableError as e:
        print(f"Storage error: {e}")
        # Retry or failover

    except EmbeddingError as e:
        print(f"Embedding failed: {e}")
        # Check API key

    except OpenVikingError as e:
        print(f"OpenViking error [{e.code}]: {e.message}")
        # Generic handling

    finally:
        await client.close()
```

---

## 12.4 Filter DSL Reference

### Basic Operators

```python
# Must match (equality)
{"op": "must", "field": "context_type", "conds": ["memory"]}

# Must not match (exclusion)
{"op": "must_not", "field": "context_type", "conds": ["skill"]}

# Range (numeric)
{"op": "range", "field": "active_count", "gte": 1, "lte": 100}

# Prefix (string)
{"op": "prefix", "field": "uri", "prefix": "viking://resources/"}

# Exists (field presence)
{"op": "exists", "field": "relations"}
```

### Compound Operators

```python
# AND - all conditions must match
{
    "op": "and",
    "conds": [
        {"op": "must", "field": "context_type", "conds": ["resource"]},
        {"op": "must", "field": "is_leaf", "conds": [True]}
    ]
}

# OR - any condition matches
{
    "op": "or",
    "conds": [
        {"op": "must", "field": "scope", "conds": ["user"]},
        {"op": "must", "field": "scope", "conds": ["agent"]}
    ]
}
```

### Complex Filter Example

```python
# Find active memory resources under user scope,
# excluding archived items
filter = {
    "op": "and",
    "conds": [
        {"op": "must", "field": "context_type", "conds": ["memory"]},
        {"op": "prefix", "field": "uri", "prefix": "viking://user/"},
        {"op": "range", "field": "active_count", "gte": 1},
        {"op": "must_not", "field": "meta.archived", "conds": [True]}
    ]
}

results = await client.find(
    query="important decisions",
    filter=filter,
    limit=20
)
```

---

## 12.5 URI Scheme Reference

### URI Format

```
viking://[scope]/[path]/[name]

Scope:
  - user     : User-owned contexts (memories, preferences)
  - agent    : Agent-owned contexts (skills, task memories)
  - resources: Shared contexts (documents, repos, web pages)
  - session  : Session-scoped contexts (conversation history)

Examples:
  viking://user/memories/work
  viking://agent/skills/code_review
  viking://resources/my_project/src/main.py
  viking://session/conv_001/messages
```

### Reserved Paths

| Path | Scope | Purpose |
|------|-------|---------|
| `/memories/` | user | Long-term memories |
| `/preferences/` | user | User preferences |
| `/profile/` | user | User profile info |
| `/skills/` | agent | Registered skills |
| `/tasks/` | agent | Task-specific memories |
| `/messages/` | session | Conversation messages |
| `/history/` | session | Archived messages |

### URI Operations

```python
from openviking.utils.uri import VikingURI

# Parse URI
uri = VikingURI("viking://resources/project/src/main.py")
print(uri.scope)     # "resources"
print(uri.path)      # ["project", "src", "main.py"]
print(uri.name)      # "main.py"
print(uri.parent)    # "viking://resources/project/src/"

# Build URI
uri = VikingURI.build(
    scope="user",
    path=["memories", "work"],
    name="meeting_notes"
)
print(str(uri))  # "viking://resources/memories/work/meeting_notes"

# Validate
VikingURI.validate("viking://resources/test")  # True
VikingURI.validate("invalid://path")  # False
```

---

## 12.6 Glossary

| Term | Definition |
|------|------------|
| **AGFS** | AI Graph File System - hierarchical file storage backend |
| **Context** | Unified record representing any knowledge item |
| **Dense Vector** | High-dimensional embedding for semantic similarity |
| **Embedding** | Numerical representation of text for similarity search |
| **Genesis Specification** | Comprehensive documentation for AI agent consumption |
| **Hierarchical Retrieval** | Multi-level search from directories to leaves |
| **L0/L1/L2** | Tiered summarization (abstract/overview/full) |
| **OVPack** | Portable export format for OpenViking data |
| **ParseResult** | Structured output from content parsing |
| **ResourceNode** | Tree node representing parsed content hierarchy |
| **Scope** | Top-level URI namespace (user/agent/resources/session) |
| **Session** | Conversation context with message history |
| **Sparse Vector** | BM25-style keyword representation for hybrid search |
| **ThinkingTrace** | Debug information about retrieval decisions |
| **URI** | Uniform Resource Identifier in viking:// scheme |
| **VikingDB** | Vector database for semantic storage |
| **VikingFS** | Filesystem abstraction over AGFS |
| **VLM** | Vision-Language Model for multimodal understanding |

---

## 12.7 Quick Reference Card

```
+==================================================================+
|                  OPENVIKING QUICK REFERENCE                       |
+==================================================================+

INITIALIZATION
--------------
from openviking import AsyncOpenViking
client = AsyncOpenViking()
await client.initialize()
await client.close()

ADD RESOURCES
-------------
await client.add_resource("path/file.md", wait=True)
await client.add_resource("https://url", wait=True)

SEARCH
------
results = await client.find("query")
results = await client.find("query", target_uri="viking://resources/")

FILE OPERATIONS
---------------
await client.ls("viking://resources/")           # List
await client.read("viking://resources/file")     # Read content
await client.abstract("viking://resources/dir")  # Get L0 summary
await client.overview("viking://resources/dir")  # Get L1 overview
await client.tree("viking://resources/")         # Tree view

MODIFY
------
await client.mkdir("viking://user/notes/")       # Create dir
await client.rm("viking://user/old/", recursive=True)  # Delete
await client.mv("viking://from/", "viking://to/")  # Move

RELATIONS
---------
await client.link("viking://a/", ["viking://b/"])
await client.relations("viking://a/")

SESSIONS
--------
session = client.session("id")
await session.add_message("user", "text")
await session.commit()

EXPORT/IMPORT
-------------
await client.export_ovpack("viking://resources/", "/path.ovpack")
await client.import_ovpack("/path.ovpack", "viking://resources/")

MONITORING
----------
client.observers["queue"].get_status_table()
client.observers["vikingdb"].get_status_table()

+==================================================================+
```

---

## 12.8 Quality Checklist

- [x] Code examples comprehensive
- [x] Configuration examples provided
- [x] Error codes documented
- [x] Filter DSL reference complete
- [x] URI scheme documented
- [x] Glossary included
- [x] Quick reference card provided
