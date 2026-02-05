# OpenViking Genesis Specification - Section 05: Architecture Design

**Version**: 1.0.0
**Last Updated**: 2026-02-05
**Status**: Production Ready

---

## 5.1 High-Level Architecture

```
+===========================================================================+
|                           OPENVIKING ARCHITECTURE                          |
+===========================================================================+

+---------------------------------+    +---------------------------------+
|          CLIENT LAYER           |    |         EXTERNAL SERVICES        |
+---------------------------------+    +---------------------------------+
|  AsyncOpenViking / SyncOpenViking |    |  OpenAI API   | Volcengine Ark  |
|  - Singleton (embedded mode)    |    |  NotebookLM   | Custom Models   |
|  - Multi-instance (service mode)|    +---------------------------------+
+-----------------+---------------+
                  |
+-----------------v---------------+
|           CORE LAYER            |
+---------------------------------+
|  VikingFS      | Session        |
|  - URI routing | - Messages     |
|  - File ops    | - Compression  |
|  - Relations   | - Memory ext   |
+-----------------+---------------+
                  |
+-----------------v---------------+
|          STORAGE LAYER          |
+---------------------------------+
|  VikingDBManager                |
|  +---------------------------+  |
|  | VikingVectorIndexBackend  |  |
|  | NotebookLMBackend         |  |
|  +---------------------------+  |
|  | QueueManager              |  |
|  | - SemanticQueue           |  |
|  | - EmbeddingQueue          |  |
|  +---------------------------+  |
+-----------------+---------------+
                  |
+-----------------v---------------+
|        PERSISTENCE LAYER        |
+---------------------------------+
|  AGFS (Files)  | VikingDB Index |
|  - content.md  | - Vectors      |
|  - .abstract   | - Metadata     |
|  - .overview   | - Filters      |
+---------------------------------+
```

---

## 5.2 Module Structure

### openviking/ Package Organization

```
openviking/
+-- __init__.py              # Package exports
+-- client.py                # SyncOpenViking wrapper
+-- async_client.py          # AsyncOpenViking main client
+-- agfs_manager.py          # AGFS subprocess management
|
+-- core/                    # Core utilities
|   +-- context.py           # Context definitions
|   +-- building_tree.py     # Tree construction
|   +-- directories.py       # Directory initialization
|   +-- skill_loader.py      # Skill loading
|   +-- mcp_converter.py     # MCP format conversion
|
+-- models/                  # Model integrations
|   +-- embedder/            # Embedding backends
|   |   +-- base.py          # EmbedderBase interface
|   |   +-- openai_embedders.py
|   |   +-- volcengine_embedders.py
|   |   +-- vikingdb_embedders.py
|   +-- vlm/                 # Vision-Language Models
|       +-- base.py          # VLMBase interface
|       +-- backends/
|           +-- openai_vlm.py
|           +-- volcengine_vlm.py
|
+-- parse/                   # Content parsing
|   +-- base.py              # ResourceNode, ParseResult
|   +-- registry.py          # Parser registry
|   +-- custom.py            # Custom parser support
|   +-- parsers/
|       +-- pdf.py
|       +-- markdown.py
|       +-- html.py
|       +-- code.py
|       +-- text.py
|       +-- media.py
|
+-- retrieve/                # Search & retrieval
|   +-- hierarchical_retriever.py
|   +-- intent_analyzer.py
|   +-- types.py
|
+-- session/                 # Session management
|   +-- session.py           # Session class
|   +-- compressor.py        # SessionCompressor
|   +-- memory_extractor.py  # MemoryExtractor
|   +-- memory_deduplicator.py
|
+-- storage/                 # Storage backends
|   +-- vikingdb_interface.py    # Abstract interface
|   +-- notebooklm_backend.py    # NotebookLM impl
|   +-- viking_fs.py             # Filesystem abstraction
|   +-- collection_schemas.py    # Schema definitions
|   +-- local_fs.py              # Local file operations
|   +-- queuefs/                 # Queue system
|   |   +-- queue_manager.py
|   |   +-- named_queue.py
|   |   +-- embedding_queue.py
|   |   +-- semantic_queue.py
|   +-- observers/               # Monitoring
|   |   +-- base_observer.py
|   |   +-- queue_observer.py
|   |   +-- vikingdb_observer.py
|   +-- vectordb/                # Vector storage
|       +-- collection/
|       +-- project/
|       +-- index/
|
+-- utils/                   # Utilities
    +-- config/              # Configuration
    |   +-- open_viking_config.py
    |   +-- notebooklm_config.py
    |   +-- storage_config.py
    |   +-- embedding_config.py
    +-- uri.py               # VikingURI parsing
    +-- resource_processor.py
    +-- skill_processor.py
```

### Module Responsibilities

| Module | Responsibility |
|--------|----------------|
| **client** | Entry point, initialization, lifecycle management |
| **core** | Context definitions, directory structure, skill loading |
| **models** | Model backend abstractions (embedders, VLMs) |
| **parse** | Content parsing, format detection, tree building |
| **retrieve** | Search algorithms, intent analysis, ranking |
| **session** | Message management, compression, memory extraction |
| **storage** | Vector storage, queues, file systems, observers |
| **utils** | Configuration, URI handling, processors |

---

## 5.3 Design Patterns

| Pattern | Location | Purpose |
|---------|----------|---------|
| **Singleton** | AsyncOpenViking, QueueManager, VikingFS | Global state management |
| **Strategy** | VikingDBInterface implementations | Pluggable storage backends |
| **Factory** | VLMFactory, ParserRegistry | Object creation |
| **Observer** | BaseObserver, QueueObserver | System monitoring |
| **Adapter** | NotebookLMBackend | External service integration |
| **Producer-Consumer** | QueueManager, handlers | Async processing |
| **Template Method** | BaseParser.parse() | Common parsing flow |
| **Registry** | ParserRegistry | Extension management |
| **Facade** | VikingFS | Simplified file operations |
| **Composite** | ResourceNode tree | Hierarchical content |

---

## 5.4 API Design

### Public Client API

```python
class AsyncOpenViking:
    # Lifecycle
    async def initialize() -> None
    async def close() -> None

    # Resources
    async def add_resource(path, target, reason, instruction, wait, timeout) -> Dict
    async def add_skill(data, wait, timeout) -> Dict

    # Search
    async def find(query, target_uri, limit, score_threshold, filter) -> FindResult
    async def search(query, target_uri, session, limit, score_threshold, filter)

    # File Operations
    async def ls(uri, simple, recursive) -> List
    async def read(uri) -> str
    async def abstract(uri) -> str
    async def overview(uri) -> str
    async def glob(pattern, uri) -> Dict
    async def grep(uri, pattern, case_insensitive) -> Dict
    async def tree(uri) -> Dict
    async def mkdir(uri) -> None
    async def rm(uri, recursive) -> None
    async def mv(from_uri, to_uri) -> None

    # Relations
    async def link(from_uri, uris, reason) -> None
    async def unlink(from_uri, uri) -> None
    async def relations(uri) -> List[Dict]

    # Import/Export
    async def export_ovpack(uri, to) -> str
    async def import_ovpack(file_path, parent, force, vectorize) -> str

    # Session
    def session(session_id) -> Session

    # Monitoring
    async def wait_processed(timeout) -> Dict
    @property
    def observers() -> Dict[str, Observer]
```

### VikingDBInterface Contract

```python
class VikingDBInterface(ABC):
    # Collections
    async def create_collection(name, schema) -> bool
    async def drop_collection(name) -> bool
    async def collection_exists(name) -> bool
    async def list_collections() -> List[str]
    async def get_collection_info(name) -> Optional[Dict]

    # CRUD
    async def insert(collection, data) -> str
    async def update(collection, id, data) -> bool
    async def upsert(collection, data) -> str
    async def delete(collection, ids) -> int
    async def get(collection, ids) -> List[Dict]
    async def exists(collection, id) -> bool

    # Batch
    async def batch_insert(collection, data) -> List[str]
    async def batch_upsert(collection, data) -> List[str]
    async def batch_delete(collection, filter) -> int
    async def remove_by_uri(collection, uri) -> int

    # Search
    async def search(collection, query_vector, sparse_query_vector,
                     filter, limit, offset, output_fields, with_vector) -> List[Dict]
    async def filter(collection, filter, limit, offset,
                     output_fields, order_by, order_desc) -> List[Dict]
    async def scroll(collection, filter, limit, cursor, output_fields) -> Tuple
    async def count(collection, filter) -> int

    # Lifecycle
    async def clear(collection) -> bool
    async def optimize(collection) -> bool
    async def close() -> None
    async def health_check() -> bool
    async def get_stats() -> Dict
```

---

## 5.5 Integration Points

### External Service Integrations

```
+-------------------+     +-------------------+
|    OpenViking     |     |  External Service |
+-------------------+     +-------------------+
        |                         |
        | (1) Embeddings          |
        +------------------------>| OpenAI API
        |<------------------------| text-embedding-3-*
        |                         |
        | (2) VLM Completions     |
        +------------------------>| OpenAI / Volcengine
        |<------------------------| gpt-4o / doubao
        |                         |
        | (3) Semantic Search     |
        +------------------------>| NotebookLM
        |<------------------------| query() response
        |                         |
        | (4) File Storage        |
        +------------------------>| AGFS Service
        |<------------------------| File operations
        |                         |
```

### Extension Points

1. **Custom Parser**: Implement `CustomParserProtocol`
2. **Custom Embedder**: Extend `DenseEmbedderBase` or `HybridEmbedderBase`
3. **Custom VLM**: Extend `VLMBase`
4. **Custom Storage**: Implement `VikingDBInterface`
5. **Custom Observer**: Extend `BaseObserver`

---

## 5.6 Architectural Decisions

### ADR-001: Filesystem Paradigm over Flat Storage

**Context**: Traditional RAG uses flat vector storage without hierarchy.

**Decision**: Adopt `viking://` URI filesystem paradigm with directories.

**Rationale**:
- Enables deterministic navigation (ls, cd, find)
- Supports hierarchical summarization (L0/L1/L2)
- Familiar mental model for developers
- Enables recursive retrieval algorithms

**Consequences**:
- Additional complexity in URI management
- Need to sync filesystem and vector store
- More intuitive debugging

### ADR-002: Dual Backend Strategy

**Context**: Vector embeddings vs LLM-native semantic understanding.

**Decision**: Support both VikingVectorIndexBackend and NotebookLMBackend.

**Rationale**:
- Vector search: Fast, controllable, works offline
- NotebookLM: Deeper understanding, no embedding needed
- Users can choose based on use case

**Consequences**:
- Two code paths to maintain
- Configuration complexity
- Flexibility in deployment

### ADR-003: Subprocess Isolation for NotebookLM

**Context**: NotebookLM client lives in pipx venv.

**Decision**: Use subprocess calls to isolated Python environment.

**Rationale**:
- Avoids dependency conflicts
- Clean environment separation
- Leverages existing pipx installation

**Consequences**:
- Higher latency per call
- Process overhead
- Requires pipx setup

---

## 5.7 Quality Checklist

- [x] Architecture is clearly diagrammed
- [x] Modules have defined responsibilities
- [x] Patterns are documented
- [x] Decisions have rationale
- [x] APIs are fully specified
- [x] Extension points are identified
