# Task 0.1: Create NotebookLMConfig Class

**Phase:** 0
**Sequence:** 1
**Type:** SEQUENTIAL
**Agent Assignment:** code-architect
**Blocking:** Yes
**Parallel With:** None

---

## Dependencies

**Depends On:**
- None (prerequisite task)

**Blocks:**
- [ ] task_1_1_notebooklm-backend (cannot start until this completes)

**Critical Path:** Yes

---

## Objective

Create a `NotebookLMConfig` class to configure the NotebookLM storage backend, following the existing config patterns in OpenViking (e.g., `VectorDBBackendConfig`).

---

## Implementation Steps

1. [ ] Create file `openviking/utils/config/notebooklm_config.py`
2. [ ] Define `NotebookLMConfig` dataclass with fields:
   - `notebook_mapping: Dict[str, str]` - Maps collection names to notebook IDs
   - `default_notebook_id: str` - Fallback notebook for unmapped collections
   - `auth_token_path: Optional[str]` - Path to auth tokens (default: ~/.notebooklm/tokens.json)
   - `tier_mapping: Dict[str, str]` - Maps L0/L1/L2 to source naming patterns
3. [ ] Add validation logic for required fields
4. [ ] Export from `openviking/utils/config/__init__.py`
5. [ ] Add `notebooklm: Optional[NotebookLMConfig]` field to `StorageConfig` or create new backend selector

---

## Verification Requirements

**Type:** TDD

**Requirements:**
- [ ] Unit test for config creation with valid params
- [ ] Unit test for config validation errors
- [ ] Unit test for default values

**Acceptance Criteria:**
- NotebookLMConfig can be instantiated with notebook_mapping
- Invalid configs raise appropriate exceptions
- Config exports correctly from config module

**Automation Script:**
```bash
cd /home/devuser/SneakPeak/OpenViking
uv run pytest tests/utils/config/test_notebooklm_config.py -v
```

---

## Enhancement Queries

**Query 1 (Priority: high):**
```
Best practices for Python dataclass config validation with Pydantic in 2026?
```

---

## Files Modified/Created

- [ ] `openviking/utils/config/notebooklm_config.py` (CREATE)
- [ ] `openviking/utils/config/__init__.py` (MODIFY - add export)
- [ ] `tests/utils/config/test_notebooklm_config.py` (CREATE)

---

## Commit Message

```
feat(config): add NotebookLMConfig for semantic storage backend

Adds configuration class for NotebookLM storage backend with
notebook mapping, tier configuration, and auth token path.
```

---

## Risk Assessment

**Risk Level:** LOW

**Potential Risks:**
- Risk 1: Config schema may need adjustment → Mitigation: Start minimal, extend as needed

**Critical Blocker:** No

---

## Context Cost Estimate

**Estimated Tokens:** ~5,000 tokens
**Tool Calls:** 3-5 expected
**Agent Session:** ~10 minutes

---

## Status Tracking

**Status:** [ ] Not Started
**Assigned Agent:**
**Started:**
**Completed:**
**Checkpoint SHA:**
