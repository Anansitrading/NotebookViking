# OpenViking Genesis Specification - Section 04: Process Flowcharts

**Version**: 1.0.0
**Last Updated**: 2026-02-05
**Status**: Production Ready

---

## 4.1 System Overview Flow

```
+------------------------------------------------------------------+
|                    OPENVIKING SYSTEM OVERVIEW                      |
+------------------------------------------------------------------+

                         +----------------+
                         |   User/Agent   |
                         +-------+--------+
                                 |
                    +------------+------------+
                    |                         |
              [Add Resource]            [Search/Find]
                    |                         |
                    v                         v
            +-------+-------+         +-------+-------+
            |  Parse Module |         | Intent Analyzer|
            | PDF/MD/HTML/  |         | Query Planning |
            | Code Parsers  |         +-------+-------+
            +-------+-------+                 |
                    |                         v
                    v                 +-------+-------+
            +-------+-------+         | Hierarchical  |
            | AGFS (Files)  |<------->|  Retriever    |
            +-------+-------+         +-------+-------+
                    |                         |
                    v                         v
            +-------+-------+         +-------+-------+
            | Queue Manager |         | Vector Store  |
            | Semantic/Embed|         | VikingDB/     |
            +-------+-------+         | NotebookLM    |
                    |                 +---------------+
                    v
            +-------+-------+
            | Embedding     |
            | OpenAI/       |
            | Volcengine    |
            +---------------+
```

---

## 4.2 Core Process Flows

### 4.2.1 Resource Addition Flow

```
User: add_resource(path/URL)
          |
          v
+-------------------+
| ResourceProcessor |
+--------+----------+
         |
         v
+-------------------+     +-------------------+
| Detect Resource   |---->| Select Parser     |
| Type (ext/content)|     | (PDF/MD/HTML/Code)|
+-------------------+     +--------+----------+
                                   |
                                   v
                          +--------+----------+
                          | Parse to          |
                          | ResourceNode tree |
                          +--------+----------+
                                   |
                                   v
                          +--------+----------+
                          | Write to AGFS     |
                          | (create dirs,     |
                          |  content.md files)|
                          +--------+----------+
                                   |
                                   v
                          +--------+----------+
                          | Enqueue Semantic  |
                          | Messages          |
                          +--------+----------+
                                   |
                                   v
                          +--------+----------+
                          | SemanticProcessor |
                          | (async dequeue)   |
                          +--------+----------+
                                   |
              +--------------------+--------------------+
              |                                         |
              v                                         v
     +--------+----------+                    +--------+----------+
     | Generate .abstract|                    | Generate .overview|
     | (L0 summary)      |                    | (L1 overview)     |
     +--------+----------+                    +--------+----------+
              |                                         |
              +--------------------+--------------------+
                                   |
                                   v
                          +--------+----------+
                          | Enqueue Embedding |
                          | Messages          |
                          +--------+----------+
                                   |
                                   v
                          +--------+----------+
                          | TextEmbeddingHdlr |
                          | (async dequeue)   |
                          +--------+----------+
                                   |
                                   v
                          +--------+----------+
                          | Generate Vectors  |
                          | (dense + sparse)  |
                          +--------+----------+
                                   |
                                   v
                          +--------+----------+
                          | Store in VikingDB |
                          | (with metadata)   |
                          +-------------------+
```

### 4.2.2 Semantic Search Flow

```
User: find(query, target_uri)
          |
          v
+-------------------+
| VikingFS.find()   |
+--------+----------+
         |
         +------ Is semantic_backend set? ------+
         |                                      |
         | Yes                                  | No
         v                                      v
+--------+----------+               +-----------+---------+
| NotebookLMBackend |               | Get Embedder        |
| ._query()         |               | Embed query text    |
+--------+----------+               +-----------+---------+
         |                                      |
         v                                      v
+--------+----------+               +-----------+---------+
| Subprocess to     |               | HierarchicalRetrv   |
| pipx venv         |               | .retrieve()         |
+--------+----------+               +-----------+---------+
         |                                      |
         v                                      v
+--------+----------+               +-----------+---------+
| NotebookLM        |               | Global search       |
| query() API       |               | (directory nodes)   |
+--------+----------+               +-----------+---------+
         |                                      |
         v                                      v
+--------+----------+               +-----------+---------+
| Parse sources     |               | Recursive drill-down|
| Return results    |               | Score propagation   |
+-------------------+               +-----------+---------+
                                               |
                                               v
                                    +-----------+---------+
                                    | Optional Rerank     |
                                    +-----------+---------+
                                               |
                                               v
                                    +-----------+---------+
                                    | Return FindResult   |
                                    | with MatchedContext |
                                    +---------------------+
```

### 4.2.3 Session Management Flow

```
Session.add_message(role, content)
          |
          v
+-------------------+
| Accumulate in     |
| _messages buffer  |
+--------+----------+
         |
         v
+-------------------+
| Track token count |
| Track turn count  |
+--------+----------+
         |
         +------ Exceeds threshold? ------+
         |                                 |
         | Yes                             | No
         v                                 v
+--------+----------+              +-------+
| Trigger commit()  |              | Wait  |
+--------+----------+              +-------+
         |
         v
+-------------------+
| Archive current   |
| messages to       |
| history/archive_N |
+--------+----------+
         |
         v
+-------------------+
| Generate L0/L1/L2 |
| summaries         |
+--------+----------+
         |
         v
+-------------------+
| MemoryExtractor   |
| (6 categories)    |
+--------+----------+
         |
         v
+-------------------+
| MemoryDeduplicator|
| (vector + LLM)    |
+--------+----------+
         |
         +------ Decision? ------+
         |         |         |   |
         v         v         v   v
     CREATE    UPDATE    MERGE  SKIP
         |         |         |
         v         v         v
+-------------------+
| Write memories to |
| viking://user/    |
| viking://agent/   |
+-------------------+
```

---

## 4.3 Data Flow Diagrams

### 4.3.1 Write Path Data Flow

```
+-------------+     +-------------+     +-------------+
|   Content   |---->|   Parser    |---->| ResourceNode|
| (file/URL)  |     |             |     |   Tree      |
+-------------+     +-------------+     +------+------+
                                               |
                    +-------------+            |
                    |    AGFS     |<-----------+
                    | (file store)|
                    +------+------+
                           |
              +------------+------------+
              |                         |
              v                         v
       +------+------+           +------+------+
       |  Semantic   |           |  Embedding  |
       |   Queue     |           |   Queue     |
       +------+------+           +------+------+
              |                         |
              v                         v
       +------+------+           +------+------+
       |  Semantic   |           |  Embedding  |
       |  Processor  |           |   Handler   |
       +------+------+           +------+------+
              |                         |
              v                         v
       +------+------+           +------+------+
       | .abstract   |           |   Vector    |
       | .overview   |           |   (dense +  |
       |   files     |           |    sparse)  |
       +-------------+           +------+------+
                                        |
                                        v
                                 +------+------+
                                 |  VikingDB   |
                                 |  Collection |
                                 +-------------+
```

### 4.3.2 Read Path Data Flow

```
+-------------+     +-------------+     +-------------+
|   Query     |---->|  Embedder   |---->| Query Vector|
|   Text      |     |             |     |             |
+-------------+     +-------------+     +------+------+
                                               |
                                               v
                                        +------+------+
                                        |  VikingDB   |
                                        |  Search     |
                                        +------+------+
                                               |
                    +-------------+            |
                    |    AGFS     |<-----------+
                    | (read files)|     (URI lookup)
                    +------+------+
                           |
              +------------+------------+
              |            |            |
              v            v            v
       +------+------+ +------+------+ +------+------+
       |  .abstract  | | .overview   | |  content.md |
       |    (L0)     | |   (L1)      | |    (L2)     |
       +-------------+ +-------------+ +-------------+
```

---

## 4.4 State Machines

### 4.4.1 Queue Message States

```
          +--------+
          | QUEUED |
          +---+----+
              |
              | dequeue()
              v
      +-------+--------+
      | IN_PROGRESS    |
      +-------+--------+
              |
      +-------+-------+
      |               |
      v               v
+-----+-----+   +-----+-----+
| PROCESSED |   |   ERROR   |
+-----------+   +-----+-----+
                      |
                      | retry?
                      v
              +-------+--------+
              | RETRY_QUEUED   |
              +----------------+
```

### 4.4.2 Session States

```
          +--------+
          | ACTIVE |
          +---+----+
              |
              | threshold exceeded
              v
      +-------+--------+
      | COMPRESSING    |
      +-------+--------+
              |
              v
      +-------+--------+
      | ARCHIVED       |
      +-------+--------+
              |
              | memory extraction
              v
      +-------+--------+
      | EXTRACTED      |
      +----------------+
```

---

## 4.5 Sequence Diagrams

### 4.5.1 Resource Addition Sequence

```
User          Client         Parser        AGFS         Queue        VikingDB
 |               |              |            |            |             |
 |--add_resource>|              |            |            |             |
 |               |--detect type>|            |            |             |
 |               |<--parser-----|            |            |             |
 |               |--parse------>|            |            |             |
 |               |<--nodes------|            |            |             |
 |               |--write files------------->|            |             |
 |               |<--URIs----------------------|            |             |
 |               |--enqueue semantic--------->|            |             |
 |               |<--ack-----------------------|            |             |
 |               |              |            |--process--->|             |
 |               |              |            |--embed----->|             |
 |               |              |            |             |--insert---->|
 |<--result------|              |            |             |<--ok--------|
 |               |              |            |             |             |
```

---

## 4.6 Quality Checklist

- [x] Main flow is documented
- [x] All major features have flows
- [x] Error paths are shown (retry in queue)
- [x] Diagrams are ASCII-based
- [x] State machines cover key components
- [x] Sequence diagrams show interactions
