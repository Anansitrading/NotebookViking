# OpenViking Genesis Specification - Section 03: Technology Stack

**Version**: 1.0.0
**Last Updated**: 2026-02-05
**Status**: Production Ready

---

## 3.1 Core Technologies

| Technology | Version | Purpose |
|------------|---------|---------|
| Python | 3.9+ | Primary language |
| Pydantic | 2.0+ | Configuration and data validation |
| httpx | 0.25+ | Async HTTP client |
| OpenAI SDK | 1.0+ | OpenAI API integration |
| FastAPI | 0.128+ | API server framework |
| uvicorn | 0.39+ | ASGI server |

---

## 3.2 Dependencies

### Production Dependencies

| Package | Version | Purpose |
|---------|---------|---------|
| pydantic | >=2.0.0 | Schema validation and config |
| typing-extensions | >=4.5.0 | Type hints backport |
| pyyaml | >=6.0 | YAML configuration parsing |
| httpx | >=0.25.0 | Async HTTP requests |
| pdfplumber | >=0.10.0 | PDF text extraction |
| readabilipy | >=0.2.0 | HTML content extraction |
| markdownify | >=0.11.0 | HTML to Markdown conversion |
| openai | >=1.0.0 | OpenAI embeddings and VLM |
| requests | >=2.28.0 | HTTP requests (sync) |
| json-repair | >=0.25.0 | JSON parsing with error recovery |
| apscheduler | >=3.11.0 | Background task scheduling |
| orjson | >=3.11.4 | Fast JSON serialization |
| volcengine | >=1.0.212 | Volcengine SDK base |
| volcengine-python-sdk[ark] | >=5.0.3 | Doubao model integration |
| pyagfs | >=1.4.0 | AGFS filesystem client |
| psutil | >=7.2.1 | Process monitoring |
| fastapi | >=0.128.0 | REST API framework |
| uvicorn | >=0.39.0 | ASGI server |
| werkzeug | >=3.1.4 | WSGI utilities |
| pandas | >=2.3.3 | Data analysis (observers) |
| xxhash | >=3.0.0 | Fast hashing |

### Development Dependencies

| Package | Version | Purpose |
|---------|---------|---------|
| pytest | >=7.0.0 | Testing framework |
| pytest-asyncio | >=0.21.0 | Async test support |
| pytest-cov | >=4.0.0 | Coverage reporting |
| black | >=23.0.0 | Code formatting |
| isort | >=5.12.0 | Import sorting |
| mypy | >=1.0.0 | Static type checking |
| ruff | >=0.1.0 | Fast linting |
| sphinx | >=7.0.0 | Documentation generation |
| sphinx-rtd-theme | >=1.3.0 | ReadTheDocs theme |
| myst-parser | >=2.0.0 | Markdown in Sphinx |

---

## 3.3 Build Tools

### Build System
- **setuptools** (>=61.0): Package building
- **pybind11** (>=2.10.0): C++ extension binding
- **cmake** (>=3.15): Native code compilation
- **wheel**: Binary distribution

### Configuration Files
- `pyproject.toml`: Project metadata, dependencies, tool configs
- `setup.py`: Legacy build support
- `.python-version`: Python version pinning

### Code Quality Tools
```toml
[tool.black]
line-length = 100
target-version = ["py39", "py310", "py311", "py312"]

[tool.ruff]
line-length = 100
select = ["E", "W", "F", "I", "C", "B"]

[tool.mypy]
python_version = "3.9"
check_untyped_defs = true
```

---

## 3.4 Runtime Requirements

| Requirement | Minimum | Recommended |
|-------------|---------|-------------|
| Python | 3.9 | 3.11+ |
| Memory | 4GB | 16GB |
| Disk | 10GB | 100GB |
| CPU Cores | 2 | 8+ |
| OS | Linux/macOS/Windows | Linux |
| Network | Required | Stable broadband |

### Platform Support
- **Linux**: Full support (primary development platform)
- **macOS**: Full support
- **Windows**: Supported (some C++ extensions may need additional setup)

---

## 3.5 External Services

### Model Services

| Service | Purpose | Required |
|---------|---------|----------|
| OpenAI API | Embeddings + VLM | Optional |
| Volcengine Ark | Doubao embeddings + VLM | Optional |
| Custom OpenAI-compatible | Alternative models | Optional |

### Storage Services

| Service | Purpose | Required |
|---------|---------|----------|
| AGFS | Filesystem storage | Required |
| VikingDB (remote) | Vector database | Optional |
| NotebookLM | Semantic backend | Optional |

### Configuration Example
```json
{
  "embedding": {
    "dense": {
      "api_base": "https://api.openai.com/v1",
      "api_key": "sk-...",
      "backend": "openai",
      "dimension": 3072,
      "model": "text-embedding-3-large"
    }
  },
  "vlm": {
    "api_base": "https://api.openai.com/v1",
    "api_key": "sk-...",
    "backend": "openai",
    "model": "gpt-4o-mini"
  },
  "storage_backend": "vikingdb",
  "notebooklm": {
    "notebook_mapping": {
      "memories": "notebook-id-1",
      "resources": "notebook-id-2"
    }
  }
}
```

---

## 3.6 Quality Checklist

- [x] All dependencies documented
- [x] Versions are pinned (>=minimum)
- [x] Purpose is clear for each dependency
- [x] Runtime requirements specified
- [x] External services documented
- [x] Configuration examples provided
