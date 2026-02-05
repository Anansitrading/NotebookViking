# Task 3.1: Integration Tests for NotebookLM Backend

**Phase:** 3
**Sequence:** 1
**Type:** SEQUENTIAL
**Agent Assignment:** code-architect
**Blocking:** No
**Parallel With:** None

---

## Dependencies

**Depends On:**
- [x] task_2_1_viking-fs-routing (must complete before this)
- [x] task_2_2_async-client-toggle (must complete before this)

**Blocks:**
- None (final task)

**Critical Path:** No

---

## Objective

Create comprehensive integration tests that verify the full NotebookLM backend flow: config → backend → VikingFS → client.

---

## Implementation Steps

1. [ ] Create integration test file `tests/integration/test_notebooklm_integration.py`
2. [ ] Add test fixtures for NotebookLM configuration:
   ```python
   @pytest.fixture
   def notebooklm_config():
       return NotebookLMConfig(
           notebook_mapping={
               "resources": "test-notebook-id-1",
               "memories": "test-notebook-id-2",
           },
           default_notebook_id="test-default-notebook",
       )
   ```
3. [ ] Test full initialization flow:
   ```python
   async def test_openviking_with_notebooklm_backend():
       config = OpenVikingConfig(
           storage_backend="notebooklm",
           notebooklm=notebooklm_config,
       )
       client = OpenViking(config)
       await client.initialize()
       # Verify backend type
       assert isinstance(client._storage, NotebookLMBackend)
   ```
4. [ ] Test semantic search end-to-end:
   ```python
   async def test_find_via_notebooklm():
       # Setup
       await client.write("viking://resources/docs/readme.md", "...")
       # Search
       result = await client.find("readme documentation")
       # Verify
       assert len(result.resources) > 0
   ```
5. [ ] Test L0/L1/L2 tier storage:
   ```python
   async def test_tiered_storage():
       # Write with abstract and overview
       await client.write_context(
           uri="viking://resources/project",
           content="Full content...",
           abstract="One-liner L0",
           overview="Core procedure L1",
       )
       # Verify tiers stored correctly
       ...
   ```
6. [ ] Add pytest markers for slow/integration tests
7. [ ] Document test environment requirements

---

## Verification Requirements

**Type:** INTEGRATION_TEST

**Requirements:**
- [ ] All integration tests pass with mock NotebookLM
- [ ] Tests can run with real NotebookLM (marked @slow)
- [ ] Test coverage for error cases

**Acceptance Criteria:**
- Integration tests demonstrate full workflow
- Tests are repeatable and isolated
- Documentation for running tests locally

**Automation Script:**
```bash
cd /home/devuser/SneakPeak/OpenViking
# Fast tests with mocks
uv run pytest tests/integration/test_notebooklm_integration.py -v -m "not slow"

# Full tests with real NotebookLM (requires auth)
uv run pytest tests/integration/test_notebooklm_integration.py -v -m "slow"
```

---

## Enhancement Queries

**Query 1 (Priority: low):**
```
pytest async integration test patterns for external API dependencies?
```

---

## Files Modified/Created

- [ ] `tests/integration/test_notebooklm_integration.py` (CREATE)
- [ ] `tests/integration/__init__.py` (CREATE if needed)
- [ ] `tests/conftest.py` (MODIFY - add fixtures)

---

## Commit Message

```
test(integration): add NotebookLM backend integration tests

Adds comprehensive integration tests for NotebookLM backend
including initialization, semantic search, and tiered storage.
Includes both fast mock tests and slow real API tests.
```

---

## Risk Assessment

**Risk Level:** LOW

**Potential Risks:**
- Risk 1: NotebookLM API changes → Mitigation: Mock for fast tests, real API for CI

**Critical Blocker:** No

---

## Context Cost Estimate

**Estimated Tokens:** ~12,000 tokens
**Tool Calls:** 10-12 expected
**Agent Session:** ~25 minutes

---

## Status Tracking

**Status:** [ ] Not Started
**Assigned Agent:**
**Started:**
**Completed:**
**Checkpoint SHA:**
