# Master Implementation Plan: OpenViking NotebookLM Backend

**Generated:** 2026-02-05
**Track ID:** notebooklm-backend
**Total Tasks:** 5
**Total Phases:** 4
**Total Waves:** 4
**Estimated Duration:** ~2-3 hours

---

## Quick Navigation

- [Wave 0: Configuration](./wave_0_SEQUENTIAL.md)
- [Wave 1: Backend](./wave_1_SEQUENTIAL.md)
- [Wave 2: Integration](./wave_2_ASYNC.md)
- [Wave 3: Verification](./wave_3_SEQUENTIAL.md)

---

## Project Overview

Implement NotebookLM as a storage backend for OpenViking, replacing vector DB with NotebookLM's semantic engine.

### Key Mapping
| OpenViking Concept | NotebookLM Concept |
|--------------------|-------------------|
| Collection | Notebook |
| Record | Source |
| Vector Search | notebook_query (semantic) |
| URI | Source title with L0/L1/L2 prefix |

### L0/L1/L2 Tiered Naming
```
L0-{context_type}-{uri_hash}-{title}-ACTIVE  (~100 tokens)
L1-{context_type}-{uri_hash}-{title}-ACTIVE  (~2000 tokens)
L2-{context_type}-{uri_hash}-{title}-ACTIVE  (full content)
```

---

## Execution Sequence

### Phase 0: Configuration (SEQUENTIAL)
**Wave 0** - Config Setup (~30 min)
- [x] [task_0_1_notebooklm-config](./task_0_1_notebooklm-config.md) ✅ COMPLETE

**Checkpoint:** `conductor(checkpoint): Complete Phase 0 - Configuration` ✅

---

### Phase 1: Backend (SEQUENTIAL)
**Wave 1** - Core Implementation (~45 min)
- [x] [task_1_1_notebooklm-backend](./task_1_1_notebooklm-backend.md) ✅ COMPLETE

**Checkpoint:** `conductor(checkpoint): Complete Phase 1 - Backend` ✅

---

### Phase 2: Integration (ASYNC)
**Wave 2** - Parallel Integration (~35 min total) **ASYNC**
- [x] [task_2_1_viking-fs-routing](./task_2_1_viking-fs-routing.md) ✅ COMPLETE
- [x] [task_2_2_async-client-toggle](./task_2_2_async-client-toggle.md) ✅ COMPLETE

**Checkpoint:** `conductor(checkpoint): Complete Phase 2 - Integration` ✅

---

### Phase 3: Verification (SEQUENTIAL)
**Wave 3** - Final Testing (~25 min)
- [ ] [task_3_1_integration-tests](./task_3_1_integration-tests.md) (PENDING - requires full env setup)

**Final Checkpoint:** `conductor(checkpoint): Complete Implementation`

---

## Critical Path

Longest dependency chain:

```
task_0_1 → task_1_1 → task_2_1 → task_3_1
                   └→ task_2_2 ↗
```

**Total Sequential Time:** ~2 hours
**Total Parallel Time (Wave 2):** ~35 minutes (2 tasks in parallel)
**Estimated Total:** ~2-2.5 hours

---

## Parallelization Summary

| Wave | Type | Tasks | Max Agents | Duration |
|------|------|-------|------------|----------|
| 0 | SEQUENTIAL | 1 | 1 | ~30 min |
| 1 | SEQUENTIAL | 1 | 1 | ~45 min |
| 2 | ASYNC | 2 | 2 | ~35 min |
| 3 | SEQUENTIAL | 1 | 1 | ~25 min |

---

## Conductor Assignment Commands

### Wave 0-1 (Sequential)
```bash
# Single agent runs these in order
/conductor:implement task_0_1_notebooklm-config
# Wait for completion
/conductor:implement task_1_1_notebooklm-backend
```

### Wave 2 (Async - Manual Spawn)
```bash
# Terminal 1 (Agent A):
cd /home/devuser/SneakPeak/OpenViking
claude
> Implement task_2_1_viking-fs-routing.md

# Terminal 2 (Agent B):
cd /home/devuser/SneakPeak/OpenViking
claude
> Implement task_2_2_async-client-toggle.md
```

### Wave 3 (Sequential)
```bash
# After both Wave 2 tasks complete
/conductor:implement task_3_1_integration-tests
```

---

## Files Overview

### Created Files
- `openviking/utils/config/notebooklm_config.py`
- `openviking/storage/notebooklm_backend.py`
- `tests/utils/config/test_notebooklm_config.py`
- `tests/storage/test_notebooklm_backend.py`
- `tests/storage/test_viking_fs_notebooklm.py`
- `tests/integration/test_notebooklm_integration.py`

### Modified Files
- `openviking/utils/config/__init__.py`
- `openviking/utils/config/open_viking_config.py`
- `openviking/storage/__init__.py`
- `openviking/storage/viking_fs.py`
- `openviking/async_client.py`
- `tests/conftest.py`

---

## Success Metrics

| Metric | Target |
|--------|--------|
| Task Completion Rate | 100% |
| Test Pass Rate | 100% |
| Code Coverage | >80% |
| Backward Compatible | Yes |

---

## Risk Register

| Risk ID | Description | Severity | Mitigation |
|---------|-------------|----------|------------|
| R1 | NotebookLM rate limits | MEDIUM | Batch operations, caching |
| R2 | No vector similarity | LOW | Use semantic search via notebook_query |
| R3 | Source naming collisions | LOW | Include URI hash in source names |

---

**Track ID:** notebooklm-backend
**Plan Version:** 1.1
**Last Updated:** 2026-02-05
**Status:** Implementation Complete (4/5 tasks done, integration tests pending)
