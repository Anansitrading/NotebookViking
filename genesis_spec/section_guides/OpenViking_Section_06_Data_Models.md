# OpenViking Genesis Specification - Section 06: Data Models

**Version**: 1.0.0
**Last Updated**: 2026-02-05
**Status**: Production Ready

---

## 6.1 Core Entities

### Context (Primary Entity)

The unified context record stored in VikingDB.

```python
class Context:
    # Identity
    id: str                      # UUID
    uri: str                     # viking://scope/path
    parent_uri: Optional[str]    # Parent directory URI

    # Classification
    context_type: str            # "memory", "resource", "skill"
    scope: str                   # "user", "agent", "resources"

    # Content
    title: str                   # Display title
    abstract: str                # L0 summary (~100 tokens)
    overview: str                # L1 overview (~2000 tokens)
    content_hash: str            # Hash of full content

    # Vectors
    dense_vector: List[float]    # Dense embedding (1024-3072 dim)
    sparse_vector: Dict[str,float]  # Sparse BM25-style (optional)

    # Metadata
    is_leaf: bool                # True for files, False for directories
    is_dir: bool                 # True for directories
    active_count: int            # Usage frequency
    last_accessed: datetime      # Last access time
    created_at: datetime         # Creation time
    updated_at: datetime         # Last update time

    # Extended
    meta: Dict[str, Any]         # Custom metadata
    relations: List[str]         # Linked URIs
```

### ResourceNode (Parse Output)

Hierarchical representation of parsed content.

```python
class ResourceNode:
    type: NodeType               # ROOT, SECTION
    title: Optional[str]         # Section title
    level: int                   # Nesting level (0=root)
    content_type: str            # "text", "image", "video", "audio"

    # Content references
    detail_file: Optional[str]   # Temp UUID.md filename
    content_path: Optional[Path] # Final content.md path

    # Hierarchy
    children: List[ResourceNode] # Child nodes

    # Metadata
    meta: Dict[str, Any]         # Parser-specific data
    auxiliary_files: Dict[str,str]  # Multimodal attachments
```

### ParseResult (Parser Output)

Container for parsing results.

```python
class ParseResult:
    root: ResourceNode           # Root of content tree
    source_path: Optional[str]   # Original file/URL
    source_format: Optional[str] # "pdf", "markdown", "html", etc.
    parser_name: Optional[str]   # Parser identifier
    parser_version: str          # Parser version
    parse_time: float            # Processing duration
    parse_timestamp: datetime    # When parsed
    meta: Dict[str, Any]         # Additional metadata
    warnings: List[str]          # Parse warnings
```

### Session Entities

```python
class Message:
    role: str                    # "user", "assistant", "system"
    content: str                 # Message text
    timestamp: datetime          # When created
    metadata: Dict[str, Any]     # Attachments, tool calls, etc.

class CandidateMemory:
    category: str                # PROFILE, PREFERENCES, ENTITIES, EVENTS, CASES, PATTERNS
    title: str                   # Memory title
    l0: str                      # Abstract (~100 tokens)
    l1: str                      # Overview (~500 tokens)
    l2: str                      # Full content
    priority: int                # 1-5 importance

class DeduplicationDecision:
    action: str                  # CREATE, UPDATE, MERGE, SKIP
    target_uri: Optional[str]    # Existing memory URI (for UPDATE/MERGE)
    merged_content: Optional[str]  # New content (for MERGE)
    reason: str                  # LLM explanation
```

---

## 6.2 Entity Relationships

```
+------------------+
|     Context      |
+------------------+
        |
        | parent_uri (N:1)
        v
+------------------+
|     Context      |  (directory)
|   is_dir=True    |
+------------------+
        |
        | children (1:N)
        v
+------------------+
|     Context      |  (files/subdirs)
+------------------+

+------------------+     relations (N:M)     +------------------+
|     Context      |<----------------------->|     Context      |
+------------------+                         +------------------+

+------------------+     extracts (1:N)      +------------------+
|     Session      |------------------------>|  CandidateMemory |
+------------------+                         +------------------+
        |
        | archives (1:N)
        v
+------------------+
|  MessageArchive  |
|  history/arch_N  |
+------------------+
```

---

## 6.3 Database Schema

### VikingDB Context Collection

```python
CONTEXT_COLLECTION_SCHEMA = {
    "name": "context",
    "vector_dim": 1024,  # or 3072 for OpenAI
    "distance": "cosine",
    "fields": [
        # Identity
        {"name": "id", "type": "string", "indexed": True},
        {"name": "uri", "type": "string", "indexed": True},
        {"name": "parent_uri", "type": "string", "indexed": True},

        # Classification
        {"name": "context_type", "type": "string", "indexed": True},
        {"name": "scope", "type": "string", "indexed": True},

        # Content
        {"name": "title", "type": "string", "indexed": False},
        {"name": "abstract", "type": "text", "indexed": False},
        {"name": "overview", "type": "text", "indexed": False},
        {"name": "content_hash", "type": "string", "indexed": True},

        # Hierarchy
        {"name": "is_leaf", "type": "bool", "indexed": True},
        {"name": "is_dir", "type": "bool", "indexed": True},

        # Metadata
        {"name": "active_count", "type": "integer", "indexed": True},
        {"name": "last_accessed", "type": "datetime", "indexed": True},
        {"name": "created_at", "type": "datetime", "indexed": False},
        {"name": "updated_at", "type": "datetime", "indexed": False},

        # Extended
        {"name": "meta", "type": "json", "indexed": False},
        {"name": "relations", "type": "list[string]", "indexed": False},
    ],
    "indexes": [
        {"field": "uri", "type": "keyword"},
        {"field": "parent_uri", "type": "keyword"},
        {"field": "context_type", "type": "keyword"},
        {"field": "scope", "type": "keyword"},
    ]
}
```

### Filter DSL Examples

```python
# Find all memories
filter = {
    "op": "must",
    "field": "context_type",
    "conds": ["memory"]
}

# Find resources under specific path
filter = {
    "op": "prefix",
    "field": "uri",
    "prefix": "viking://resources/my_project"
}

# Find active directories
filter = {
    "op": "and",
    "conds": [
        {"op": "must", "field": "is_dir", "conds": [True]},
        {"op": "range", "field": "active_count", "gte": 1}
    ]
}
```

---

## 6.4 API Schemas

### Add Resource Request

```python
class AddResourceRequest:
    path: str                    # URL, file path, or directory
    target: Optional[str]        # Target URI (default: auto-generated)
    reason: str = ""             # Why adding this resource
    instruction: str = ""        # Processing instructions
    wait: bool = False           # Wait for completion
    timeout: Optional[float]     # Wait timeout in seconds
```

### Add Resource Response

```python
class AddResourceResponse:
    root_uri: str                # Created root URI
    count: int                   # Number of contexts created
    queue_status: Optional[Dict] # Queue processing status if wait=True
```

### Find Request

```python
class FindRequest:
    query: str                   # Search query
    target_uri: str = ""         # Target scope URI
    limit: int = 10              # Max results
    score_threshold: Optional[float] = 0.1  # Min score
    filter: Optional[Dict]       # Additional filters
```

### Find Response

```python
class FindResult:
    resources: List[MatchedContext]  # Matched contexts
    trace: Optional[ThinkingTrace]   # Debug trace

class MatchedContext:
    uri: str                     # Context URI
    title: str                   # Context title
    abstract: str                # L0 summary
    score: float                 # Relevance score
    context_type: str            # Type classification
    relations: List[RelatedContext]  # Related contexts
```

---

## 6.5 Configuration Schema

### OpenVikingConfig

```python
class OpenVikingConfig(BaseModel):
    # User
    user: str = "default_user"

    # Storage
    storage: StorageConfig
    storage_backend: str = "vikingdb"  # "vikingdb" | "notebooklm"
    notebooklm: Optional[NotebookLMConfig]

    # Models
    embedding: EmbeddingConfig
    vlm: VLMConfig
    rerank: RerankConfig

    # Parsers
    pdf: PDFConfig
    code: CodeConfig
    image: ImageConfig
    audio: AudioConfig
    video: VideoConfig
    markdown: MarkdownConfig
    html: HTMLConfig
    text: TextConfig

    # Features
    auto_generate_l0: bool = True
    auto_generate_l1: bool = True
    default_search_mode: str = "thinking"
    default_search_limit: int = 3
    enable_memory_decay: bool = True
    memory_decay_check_interval: int = 3600

    # Logging
    log_level: str = "WARNING"
    log_format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    log_output: str = "stdout"
```

### NotebookLMConfig

```python
class NotebookLMConfig(BaseModel):
    notebook_mapping: Dict[str, str] = {}  # collection -> notebook_id
    default_notebook_id: Optional[str]
    tier_config: Dict[str, int] = {
        "L0": 100,    # Max tokens for L0
        "L1": 2000,   # Max tokens for L1
        "L2": 100000  # Max tokens for L2
    }
    source_naming_pattern: str = "{tier}-{context_type}-{uri_hash}-{title}-{status}"
```

---

## 6.6 Quality Checklist

- [x] All entities documented
- [x] Field types are specified
- [x] Relationships are clear
- [x] Validation rules included (via Pydantic)
- [x] API schemas match implementation
- [x] Configuration is comprehensive
