# OpenViking Genesis Specification - Section 08: Testing Strategy

**Version**: 1.0.0
**Last Updated**: 2026-02-05
**Status**: Production Ready

---

## 8.1 Testing Philosophy

### Test Pyramid

```
                    +---------------+
                    |     E2E       |  (Few, slow, high confidence)
                    |   Tests       |
                    +-------+-------+
                            |
                +-----------+-----------+
                |    Integration        |  (Some, medium speed)
                |       Tests           |
                +-----------+-----------+
                            |
        +-------------------+-------------------+
        |              Unit Tests               |  (Many, fast)
        +---------------------------------------+
```

### Principles

1. **Test Behavior, Not Implementation**: Focus on public API contracts
2. **Async-First**: All tests support async operations
3. **Isolation**: Each test cleans up its resources
4. **Determinism**: No flaky tests (retry patterns for external services)
5. **Coverage Targets**: >80% line coverage, >70% branch coverage

---

## 8.2 Test Types

| Type | Coverage Target | Tools | Purpose |
|------|-----------------|-------|---------|
| Unit | 85% | pytest | Individual functions/classes |
| Integration | 60% | pytest-asyncio | Module interactions |
| E2E | Key paths | pytest | Full user workflows |
| Benchmark | Performance | pytest-benchmark | Speed regression |
| Property | Edge cases | hypothesis | Invariant testing |

### Test Distribution

```
tests/
+-- client/           # Client API tests
|   +-- test_lifecycle.py
|   +-- test_file_operations.py
|   +-- test_search.py
|   +-- test_resource_management.py
|   +-- test_skill_management.py
|   +-- test_import_export.py
|   +-- test_relations.py
|   +-- test_filesystem.py
|
+-- session/          # Session management tests
|   +-- test_session_lifecycle.py
|   +-- test_session_messages.py
|   +-- test_session_commit.py
|   +-- test_session_context.py
|   +-- test_session_usage.py
|
+-- vectordb/         # Vector storage tests
|   +-- test_filter_ops.py
|   +-- test_crash_recovery.py
|   +-- test_pydantic_validation.py
|   +-- test_recall.py
|   +-- test_collection_large_scale.py
|   +-- test_project_group.py
|   +-- benchmark_stress.py
|
+-- integration/      # Cross-module tests
|   +-- test_full_workflow.py
|
+-- utils/            # Utility tests
|   +-- config/
|       +-- test_notebooklm_config.py
|
+-- misc/             # Miscellaneous tests
|   +-- test_vikingdb_observer.py
|   +-- test_config_validation.py
|
+-- conftest.py       # Shared fixtures
```

---

## 8.3 Test Organization

### Naming Conventions

```python
# File naming
test_{module_name}.py

# Test function naming
def test_{feature}_{scenario}_{expected_outcome}():
    pass

# Examples
def test_add_resource_with_url_creates_context():
    pass

def test_find_with_empty_query_returns_empty():
    pass

def test_session_commit_triggers_memory_extraction():
    pass
```

### Fixture Patterns

```python
# tests/conftest.py

import pytest
from openviking import AsyncOpenViking

@pytest.fixture
async def client(tmp_path):
    """Create isolated OpenViking client."""
    client = AsyncOpenViking(path=str(tmp_path / "data"))
    await client.initialize()
    yield client
    await client.close()

@pytest.fixture
def sample_markdown():
    """Sample markdown content for testing."""
    return """# Test Document

## Section 1
This is section one content.

## Section 2
This is section two content.
"""

@pytest.fixture
async def client_with_resource(client, sample_markdown, tmp_path):
    """Client with pre-loaded resource."""
    md_file = tmp_path / "test.md"
    md_file.write_text(sample_markdown)
    await client.add_resource(str(md_file), wait=True)
    return client
```

---

## 8.4 Test Examples

### Unit Test Example

```python
# tests/utils/config/test_notebooklm_config.py

import pytest
from openviking.utils.config.notebooklm_config import NotebookLMConfig

class TestNotebookLMConfig:
    def test_default_tier_config(self):
        """Test default tier configuration values."""
        config = NotebookLMConfig()
        assert config.tier_config["L0"] == 100
        assert config.tier_config["L1"] == 2000
        assert config.tier_config["L2"] == 100000

    def test_get_notebook_id_with_mapping(self):
        """Test notebook ID retrieval from mapping."""
        config = NotebookLMConfig(
            notebook_mapping={"memories": "abc-123"}
        )
        assert config.get_notebook_id("memories") == "abc-123"

    def test_get_notebook_id_missing_raises(self):
        """Test missing collection raises ValueError."""
        config = NotebookLMConfig()
        with pytest.raises(ValueError, match="No notebook mapping"):
            config.get_notebook_id("nonexistent")

    def test_format_source_name(self):
        """Test source name formatting."""
        config = NotebookLMConfig()
        name = config.format_source_name(
            tier="L1",
            context_type="resource",
            uri_hash="abc123",
            title="Test Doc"
        )
        assert name == "L1-resource-abc123-Test Doc-ACTIVE"
```

### Integration Test Example

```python
# tests/integration/test_full_workflow.py

import pytest

@pytest.mark.asyncio
async def test_full_resource_workflow(client, tmp_path):
    """Test complete resource lifecycle."""
    # Create test file
    test_file = tmp_path / "readme.md"
    test_file.write_text("# Project\n\nThis is a test project.")

    # Add resource
    result = await client.add_resource(str(test_file), wait=True)
    root_uri = result["root_uri"]
    assert root_uri.startswith("viking://resources/")

    # List directory
    entries = await client.ls(root_uri)
    assert len(entries) > 0

    # Read content
    content = await client.read(root_uri)
    assert "test project" in content.lower()

    # Get abstract
    abstract = await client.abstract(root_uri)
    assert len(abstract) > 0

    # Semantic search
    results = await client.find("what is this project")
    assert len(results.resources) > 0
    assert results.resources[0].score > 0.1

    # Remove resource
    await client.rm(root_uri, recursive=True)

    # Verify removal
    with pytest.raises(Exception):
        await client.read(root_uri)
```

### Async Test Pattern

```python
# tests/client/test_search.py

import pytest

@pytest.mark.asyncio
async def test_find_with_target_uri(client_with_resource):
    """Test scoped semantic search."""
    client = client_with_resource

    # Get resources root
    collections = await client.ls("viking://resources/")
    assert len(collections) > 0

    target_uri = collections[0]["uri"]

    # Search within scope
    results = await client.find(
        query="content",
        target_uri=target_uri,
        limit=5
    )

    assert hasattr(results, "resources")
    for r in results.resources:
        assert r.uri.startswith(target_uri) or r.uri == target_uri
```

---

## 8.5 CI/CD Testing

### GitHub Actions Workflow

```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ['3.9', '3.10', '3.11', '3.12']

    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: ${{ matrix.python-version }}

      - name: Install dependencies
        run: |
          pip install -e ".[dev]"

      - name: Run tests
        run: |
          pytest --cov=openviking --cov-report=xml

      - name: Upload coverage
        uses: codecov/codecov-action@v3
```

### Test Commands

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=openviking --cov-report=term-missing

# Run specific test file
pytest tests/client/test_search.py

# Run specific test
pytest tests/client/test_search.py::test_find_with_target_uri

# Run with verbose output
pytest -v

# Run only async tests
pytest -m asyncio
```

---

## 8.6 Coverage Metrics

### Current Targets

| Module | Target | Type |
|--------|--------|------|
| openviking/client.py | 90% | Unit |
| openviking/async_client.py | 85% | Unit |
| openviking/storage/ | 80% | Unit + Integration |
| openviking/parse/ | 75% | Unit |
| openviking/session/ | 80% | Unit |
| openviking/retrieve/ | 70% | Unit + Integration |
| **Overall** | **>80%** | All |

### Coverage Configuration

```toml
# pyproject.toml
[tool.pytest.ini_options]
addopts = "-v --cov=openviking --cov-report=term-missing"

[tool.coverage.run]
source = ["openviking"]
omit = [
    "*/tests/*",
    "*/__pycache__/*",
    "*/third_party/*"
]

[tool.coverage.report]
exclude_lines = [
    "pragma: no cover",
    "def __repr__",
    "raise NotImplementedError",
    "if TYPE_CHECKING:"
]
```

---

## 8.7 Quality Checklist

- [x] Test strategy defined
- [x] Coverage targets set
- [x] Examples provided
- [x] CI integration documented
- [x] Test organization clear
- [x] Fixture patterns established
