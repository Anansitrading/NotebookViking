# Task 2.2: Add Backend Toggle to Async Client

**Phase:** 2
**Sequence:** 2
**Type:** ASYNC
**Agent Assignment:** code-architect
**Blocking:** No
**Parallel With:** [task_2_1_viking-fs-routing]

---

## Dependencies

**Depends On:**
- [x] task_1_1_notebooklm-backend (must complete before this)

**Blocks:**
- [ ] task_3_1_integration-tests (cannot start until this completes)

**Critical Path:** No

---

## Objective

Update `OpenViking` async client to support selecting between VikingDB and NotebookLM backends via configuration.

---

## Implementation Steps

1. [ ] Add backend type enum or string literal:
   ```python
   # In config or client
   BACKEND_VIKINGDB = "vikingdb"
   BACKEND_NOTEBOOKLM = "notebooklm"
   ```
2. [ ] Update `OpenVikingConfig` to include backend selection:
   ```python
   @dataclass
   class OpenVikingConfig:
       # ... existing fields ...
       storage_backend: str = "vikingdb"  # "vikingdb" | "notebooklm"
       notebooklm: Optional[NotebookLMConfig] = None
   ```
3. [ ] Update `OpenViking.initialize()` to instantiate correct backend:
   ```python
   async def initialize(self):
       if self.config.storage_backend == "notebooklm":
           from openviking.storage import NotebookLMBackend
           self._storage = NotebookLMBackend(self.config.notebooklm)
       else:
           from openviking.storage import VikingVectorIndexBackend
           self._storage = VikingVectorIndexBackend(self.config.vectordb)

       # Pass to VikingFS
       init_viking_fs(
           vector_store=self._storage if self.config.storage_backend == "vikingdb" else None,
           semantic_backend=self._storage if self.config.storage_backend == "notebooklm" else None,
       )
   ```
4. [ ] Update example configs and documentation

---

## Verification Requirements

**Type:** INTEGRATION_TEST

**Requirements:**
- [ ] Test OpenViking initializes with vikingdb backend (default)
- [ ] Test OpenViking initializes with notebooklm backend
- [ ] Test config validation for notebooklm backend

**Acceptance Criteria:**
- OpenViking can be initialized with either backend
- Backend selection via config, not code changes
- Backward compatible - default is vikingdb

**Automation Script:**
```bash
cd /home/devuser/SneakPeak/OpenViking
uv run pytest tests/test_async_client.py::test_backend_selection -v
```

---

## Enhancement Queries

**Query 1 (Priority: medium):**
```
Python async factory patterns for pluggable storage backends?
```

---

## Files Modified/Created

- [ ] `openviking/utils/config/open_viking_config.py` (MODIFY)
- [ ] `openviking/async_client.py` (MODIFY)
- [ ] `tests/test_async_client.py` (MODIFY - add backend tests)

---

## Commit Message

```
feat(client): add NotebookLM backend toggle to OpenViking

Adds storage_backend config option to select between vikingdb
and notebooklm backends. NotebookLM backend uses semantic search
via notebook_query instead of vector similarity.
```

---

## Risk Assessment

**Risk Level:** LOW

**Potential Risks:**
- Risk 1: Config breaking changes → Mitigation: Default to existing behavior

**Critical Blocker:** No

---

## Context Cost Estimate

**Estimated Tokens:** ~8,000 tokens
**Tool Calls:** 6-8 expected
**Agent Session:** ~15 minutes

---

## Status Tracking

**Status:** [ ] Not Started
**Assigned Agent:**
**Started:**
**Completed:**
**Checkpoint SHA:**
