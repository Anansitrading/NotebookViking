# Task 2.1: Update VikingFS for NotebookLM Routing

**Phase:** 2
**Sequence:** 1
**Type:** ASYNC
**Agent Assignment:** code-architect
**Blocking:** No
**Parallel With:** [task_2_2_async-client-toggle]

---

## Dependencies

**Depends On:**
- [x] task_1_1_notebooklm-backend (must complete before this)

**Blocks:**
- [ ] task_3_1_integration-tests (cannot start until this completes)

**Critical Path:** No

---

## Objective

Update `VikingFS.find()` method to optionally route semantic search queries to NotebookLM backend instead of the vector store, based on configuration.

---

## Implementation Steps

1. [ ] Add `semantic_backend` parameter to `VikingFS.__init__`:
   ```python
   def __init__(
       self,
       agfs_url: str = "http://localhost:8080",
       query_embedder: Optional[Any] = None,
       rerank_config: Optional["RerankConfig"] = None,
       vector_store: Optional["VikingDBInterface"] = None,
       semantic_backend: Optional["VikingDBInterface"] = None,  # NEW
       timeout: int = 10,
   ):
   ```
2. [ ] Update `find()` method to use semantic_backend if available:
   ```python
   async def find(self, query: str, ...):
       if self.semantic_backend:
           # Route to NotebookLM for semantic search
           return await self._find_via_notebooklm(query, target_uri, limit, ...)
       else:
           # Existing vector search logic
           ...
   ```
3. [ ] Implement `_find_via_notebooklm()` helper method:
   ```python
   async def _find_via_notebooklm(
       self,
       query: str,
       target_uri: str,
       limit: int,
       score_threshold: Optional[float],
       filter: Optional[Dict],
   ) -> "FindResult":
       # Map target_uri to collection name
       collection = self._uri_to_collection(target_uri)
       # Call semantic_backend.search()
       results = await self.semantic_backend.search(
           collection=collection,
           query_vector=None,  # NotebookLM doesn't use vectors
           filter=self._build_notebooklm_filter(target_uri, filter),
           limit=limit,
       )
       # Convert to FindResult format
       return self._results_to_find_result(results)
   ```
4. [ ] Add URI → collection mapping helper:
   ```python
   def _uri_to_collection(self, uri: str) -> str:
       # viking://resources/project-x → "resources"
       # viking://memories/user-1 → "memories"
       parts = uri.replace("viking://", "").split("/")
       return parts[0] if parts else "default"
   ```
5. [ ] Update `init_viking_fs()` to accept semantic_backend parameter

---

## Verification Requirements

**Type:** INTEGRATION_TEST

**Requirements:**
- [ ] Test find() routes to NotebookLM when semantic_backend set
- [ ] Test find() falls back to vector store when semantic_backend is None
- [ ] Test URI to collection mapping

**Acceptance Criteria:**
- VikingFS.find() can use NotebookLM for semantic search
- Backward compatible - existing vector search still works
- Results format unchanged

**Automation Script:**
```bash
cd /home/devuser/SneakPeak/OpenViking
uv run pytest tests/storage/test_viking_fs_notebooklm.py -v
```

---

## Enhancement Queries

**Query 1 (Priority: medium):**
```
Python URI routing patterns for multi-backend storage abstraction?
```

---

## Files Modified/Created

- [ ] `openviking/storage/viking_fs.py` (MODIFY)
- [ ] `tests/storage/test_viking_fs_notebooklm.py` (CREATE)

---

## Commit Message

```
feat(storage): add NotebookLM routing to VikingFS.find()

Adds optional semantic_backend parameter to VikingFS that routes
find() queries to NotebookLM instead of vector store when configured.
Maintains backward compatibility with existing vector search.
```

---

## Risk Assessment

**Risk Level:** LOW

**Potential Risks:**
- Risk 1: Breaking existing find() behavior → Mitigation: Feature flag, comprehensive tests

**Critical Blocker:** No

---

## Context Cost Estimate

**Estimated Tokens:** ~10,000 tokens
**Tool Calls:** 8-10 expected
**Agent Session:** ~20 minutes

---

## Status Tracking

**Status:** [ ] Not Started
**Assigned Agent:**
**Started:**
**Completed:**
**Checkpoint SHA:**
