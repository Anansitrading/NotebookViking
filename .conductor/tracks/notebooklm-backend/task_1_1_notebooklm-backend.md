# Task 1.1: Create NotebookLMBackend Class

**Phase:** 1
**Sequence:** 1
**Type:** SEQUENTIAL
**Agent Assignment:** code-architect
**Blocking:** Yes
**Parallel With:** None

---

## Dependencies

**Depends On:**
- [x] task_0_1_notebooklm-config (must complete before this)

**Blocks:**
- [ ] task_2_1_viking-fs-routing (cannot start until this completes)
- [ ] task_2_2_async-client-toggle (cannot start until this completes)

**Critical Path:** Yes

---

## Objective

Create `NotebookLMBackend` class that implements `VikingDBInterface`, mapping OpenViking collections to NotebookLM notebooks and using NotebookLM's semantic engine for search operations.

---

## Implementation Steps

1. [ ] Create file `openviking/storage/notebooklm_backend.py`
2. [ ] Import and implement `VikingDBInterface` abstract class
3. [ ] Initialize NotebookLM MCP client in `__init__`:
   ```python
   def __init__(self, config: NotebookLMConfig):
       self.config = config
       self._notebooks: Dict[str, str] = config.notebook_mapping
       # MCP client initialization via notebooklm_mcp_server
   ```
4. [ ] Implement collection management (maps to notebooks):
   - `create_collection` → `notebook_create` or use existing mapping
   - `drop_collection` → `notebook_delete` (with confirmation)
   - `collection_exists` → check notebook_mapping
   - `list_collections` → list mapped notebook names
   - `get_collection_info` → `notebook_describe`
5. [ ] Implement CRUD operations (maps to sources):
   - `insert` → `notebook_add_text` with L1 naming pattern
   - `update` → delete + re-add source
   - `upsert` → check exists, then insert/update
   - `delete` → `source_delete`
   - `get` → `source_get_content`
   - `exists` → check source list
6. [ ] Implement batch operations:
   - `batch_insert` → loop insert calls
   - `batch_upsert` → loop upsert calls
   - `batch_delete` → loop delete calls
   - `remove_by_uri` → filter by URI prefix, delete matching
7. [ ] Implement search operations (KEY - uses NotebookLM's semantic engine):
   - `search` → `notebook_query` with query text
   - `filter` → `notebook_query` with filter in query
   - `scroll` → paginated notebook_query
8. [ ] Implement lifecycle:
   - `clear` → delete all sources in notebook
   - `optimize` → no-op (NotebookLM handles internally)
   - `close` → cleanup
9. [ ] Implement health/status:
   - `health_check` → `notebook_list` success
   - `get_stats` → aggregate notebook stats

---

## Key Design Decisions

### Collection → Notebook Mapping
```python
# viking://resources/{project} → notebook_id from config
# viking://memories/{user} → another notebook_id
# Config-driven, not dynamic creation
```

### Source Naming Convention (OpenViking L0/L1/L2)
```python
# L0: ~100 tokens summary → L0-{context_type}-{uri_hash}-{title}-ACTIVE
# L1: ~2000 tokens core → L1-{context_type}-{uri_hash}-{title}-ACTIVE
# L2: Full content → L2-{context_type}-{uri_hash}-{title}-ACTIVE
```

### Semantic Search via notebook_query
```python
async def search(self, collection, query_vector=None, ...) -> List[Dict]:
    # NotebookLM doesn't use vectors directly
    # Convert query intent to natural language
    notebook_id = self._notebooks.get(collection)
    result = await self._client.notebook_query(notebook_id, query=query_text)
    # Parse result into standard format with _score
```

---

## Verification Requirements

**Type:** TDD

**Requirements:**
- [ ] Test collection CRUD operations
- [ ] Test source insert/get/delete
- [ ] Test semantic search returns scored results
- [ ] Test error handling for missing notebooks

**Acceptance Criteria:**
- NotebookLMBackend passes VikingDBInterface contract tests
- Search operations return semantically relevant results
- L0/L1/L2 naming convention applied to sources

**Automation Script:**
```bash
cd /home/devuser/SneakPeak/OpenViking
uv run pytest tests/storage/test_notebooklm_backend.py -v -m "not slow"
```

---

## Enhancement Queries

**Query 1 (Priority: high):**
```
NotebookLM MCP API patterns for batch source operations and pagination?
```

**Query 2 (Priority: medium):**
```
Converting vector similarity scores to semantic relevance scores for hybrid search?
```

---

## Files Modified/Created

- [ ] `openviking/storage/notebooklm_backend.py` (CREATE)
- [ ] `openviking/storage/__init__.py` (MODIFY - add export)
- [ ] `tests/storage/test_notebooklm_backend.py` (CREATE)

---

## Commit Message

```
feat(storage): implement NotebookLMBackend for semantic storage

Implements VikingDBInterface using NotebookLM as storage backend.
Maps collections to notebooks, uses notebook_query for semantic
search, and applies L0/L1/L2 naming convention for sources.
```

---

## Risk Assessment

**Risk Level:** MEDIUM

**Potential Risks:**
- Risk 1: NotebookLM rate limits → Mitigation: Batch operations, caching
- Risk 2: No vector support → Mitigation: Use notebook_query for semantic search
- Risk 3: Source naming collisions → Mitigation: Include URI hash in name

**Critical Blocker:** No

---

## Context Cost Estimate

**Estimated Tokens:** ~25,000 tokens
**Tool Calls:** 15-20 expected
**Agent Session:** ~45 minutes

---

## Status Tracking

**Status:** [ ] Not Started
**Assigned Agent:**
**Started:**
**Completed:**
**Checkpoint SHA:**
