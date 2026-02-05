# Wave 2: Integration (ASYNC)

**Type:** ASYNC
**Duration:** ~35 minutes total (parallel)
**Parallel Agents:** 2
**Blocking:** No

---

## Tasks in This Wave

### Async Tasks (can run in parallel)
- [ ] [task_2_1_viking-fs-routing](./task_2_1_viking-fs-routing.md) - Update VikingFS for NotebookLM routing
- [ ] [task_2_2_async-client-toggle](./task_2_2_async-client-toggle.md) - Add backend toggle to async client

---

## Wave Dependencies

**Previous Wave:** Wave 1 (NotebookLMBackend must exist)
**Next Wave:** Wave 3 (starts after ALL tasks in this wave complete)

---

## Parallelization Strategy

**Max Concurrent Agents:** 2
**Resource Conflicts:** None - different files
**Coordination Points:** Both must complete before Wave 3

### Agent Assignment
```bash
# Terminal 1 (Agent A):
cd /home/devuser/SneakPeak/OpenViking
# Implement task_2_1_viking-fs-routing

# Terminal 2 (Agent B):
cd /home/devuser/SneakPeak/OpenViking
# Implement task_2_2_async-client-toggle
```

---

## Success Criteria

- VikingFS.find() can route to NotebookLM
- OpenViking client supports backend selection
- Both tasks pass their unit tests
- No merge conflicts between changes
