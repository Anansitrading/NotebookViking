# OpenViking Genesis Specification - Section 11: Documentation & Knowledge Management

**Version**: 1.0.0
**Last Updated**: 2026-02-05
**Status**: Production Ready

---

## 11.1 Documentation Architecture

### Documentation Tiers

```
+------------------------------------------------------------------+
|                    OPENVIKING DOCUMENTATION                       |
+------------------------------------------------------------------+

+---------------------------+
|    L0: Quick Reference    |  (Developers needing fast answers)
|  - API cheat sheet        |
|  - Common patterns        |
|  - Error codes            |
+---------------------------+
            |
+---------------------------+
|    L1: User Guides        |  (Users learning the system)
|  - Getting started        |
|  - Tutorials              |
|  - Use case examples      |
+---------------------------+
            |
+---------------------------+
|    L2: Reference Docs     |  (Developers building integrations)
|  - Full API reference     |
|  - Configuration schema   |
|  - Extension guides       |
+---------------------------+
            |
+---------------------------+
|    L3: Architecture Docs  |  (Contributors and maintainers)
|  - Design decisions       |
|  - Internal architecture  |
|  - Genesis specification  |
+---------------------------+
```

### Documentation Locations

| Type | Location | Audience |
|------|----------|----------|
| README | `/README.md` | All users |
| API Reference | `/docs/api/` | Developers |
| Tutorials | `/docs/tutorials/` | New users |
| Architecture | `/docs/architecture/` | Contributors |
| Genesis Spec | `/genesis_spec/` | AI agents |
| Inline Docs | Source code | Developers |

---

## 11.2 API Documentation

### Docstring Standards

```python
# Standard docstring format (Google style)
async def find(
    self,
    query: str,
    target_uri: str = "",
    limit: int = 10,
    score_threshold: Optional[float] = 0.1,
    filter: Optional[Dict] = None
) -> FindResult:
    """Search for relevant contexts using semantic similarity.

    Performs hierarchical retrieval starting from the target scope,
    using dense vector similarity with optional sparse vector
    hybrid search for improved recall.

    Args:
        query: Natural language search query.
        target_uri: Scope to search within (default: all scopes).
            Examples: "viking://resources/", "viking://user/memories/"
        limit: Maximum number of results to return (default: 10).
        score_threshold: Minimum similarity score (0.0-1.0) for
            results to be included. Default 0.1.
        filter: Additional VikingDB filter DSL to apply.
            Example: {"op": "must", "field": "context_type", "conds": ["memory"]}

    Returns:
        FindResult containing:
            - resources: List of MatchedContext with URI, title,
              abstract, score, and relations
            - trace: Optional ThinkingTrace for debugging

    Raises:
        ValueError: If query is empty or target_uri is invalid.
        ConnectionError: If VikingDB is unavailable.

    Example:
        >>> results = await client.find("authentication flow")
        >>> for r in results.resources:
        ...     print(f"{r.title} ({r.score:.2f})")
        Login Handler (0.87)
        Session Manager (0.72)

    Note:
        Results are sorted by relevance score descending.
        Use trace for debugging retrieval decisions.
    """
```

### API Reference Structure

```markdown
# OpenViking API Reference

## Client

### AsyncOpenViking

Main async client for OpenViking operations.

#### Methods

| Method | Description | Returns |
|--------|-------------|---------|
| `initialize()` | Initialize client and storage | None |
| `close()` | Clean shutdown | None |
| `add_resource()` | Add file/URL to storage | Dict |
| `find()` | Semantic search | FindResult |
| `ls()` | List directory contents | List |
| `read()` | Read context content | str |

#### Properties

| Property | Type | Description |
|----------|------|-------------|
| `observers` | Dict[str, Observer] | System monitors |
| `config` | OpenVikingConfig | Current config |

### Example Usage

```python
from openviking import AsyncOpenViking

async def main():
    client = AsyncOpenViking()
    await client.initialize()

    # Add a resource
    result = await client.add_resource(
        "https://example.com/docs",
        wait=True
    )

    # Search
    results = await client.find("main concepts")

    await client.close()
```
```

---

## 11.3 Tutorial Structure

### Getting Started Guide

```markdown
# Getting Started with OpenViking

## Prerequisites

- Python 3.9+
- AGFS service running
- OpenAI or Volcengine API key

## Installation

```bash
pip install openviking
```

## Quick Start

### 1. Initialize the Client

```python
from openviking import AsyncOpenViking
import asyncio

async def main():
    client = AsyncOpenViking()
    await client.initialize()
    print("OpenViking ready!")
    await client.close()

asyncio.run(main())
```

### 2. Add Your First Resource

```python
# Add a local file
result = await client.add_resource("./docs/readme.md", wait=True)
print(f"Added: {result['root_uri']}")

# Add a URL
result = await client.add_resource(
    "https://example.com/documentation",
    wait=True
)
```

### 3. Search Your Knowledge

```python
results = await client.find("how to configure authentication")
for r in results.resources:
    print(f"- {r.title}: {r.abstract[:100]}...")
```

## Next Steps

- [Tutorial: Building a Personal Knowledge Base](./tutorials/knowledge-base.md)
- [Tutorial: AI Assistant Integration](./tutorials/ai-assistant.md)
- [API Reference](./api/index.md)
```

### Tutorial Template

```markdown
# Tutorial: [Title]

**Time**: [X] minutes
**Level**: Beginner / Intermediate / Advanced
**Prerequisites**: [List requirements]

## What You'll Learn

- Point 1
- Point 2
- Point 3

## Setup

[Environment setup instructions]

## Step 1: [Step Title]

[Explanation of what and why]

```python
# Code example
```

[Expected output or screenshot]

## Step 2: [Step Title]

[Continue pattern...]

## Summary

What was accomplished:
- Achievement 1
- Achievement 2

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Problem A | Fix A |
| Problem B | Fix B |

## Next Tutorial

[Link to next tutorial in series]
```

---

## 11.4 Knowledge Management

### Content Lifecycle

```
+------------------------------------------------------------------+
|                    KNOWLEDGE LIFECYCLE                            |
+------------------------------------------------------------------+

  INGEST        PROCESS         STORE           RETRIEVE        DECAY
+--------+    +----------+    +---------+    +------------+    +-------+
|  Add   |--->|  Parse   |--->| Vector  |--->|   Search   |--->| Forget|
| Source |    | Summarize|    | Embed   |    |   Rank     |    |       |
+--------+    +----------+    +---------+    +------------+    +-------+
    |              |              |               |                |
    v              v              v               v                v
+--------+    +----------+    +---------+    +------------+    +-------+
| Files  |    |   L0/L1  |    | Context |    |  Results   |    | Prune |
| URLs   |    | Summaries|    | Records |    | + Trace    |    | Unused|
| Text   |    |          |    |         |    |            |    |       |
+--------+    +----------+    +---------+    +------------+    +-------+
```

### Memory Categories

| Category | Description | Examples |
|----------|-------------|----------|
| **PROFILE** | User characteristics | Preferences, roles, expertise |
| **PREFERENCES** | Stated likes/dislikes | "Prefer TypeScript", "Avoid patterns X" |
| **ENTITIES** | Named concepts | Projects, tools, people |
| **EVENTS** | Temporal occurrences | Meetings, decisions, milestones |
| **CASES** | Problem-solution pairs | Bug fixes, implementations |
| **PATTERNS** | Behavioral patterns | Coding style, review patterns |

### Tiered Summarization

```python
# L0: Abstract (~100 tokens)
# Single-sentence summary for quick scanning
"Authentication module implementing JWT-based session management
with refresh token rotation for secure API access."

# L1: Overview (~2000 tokens)
# Key concepts, main features, important details
"""
## Authentication Module

### Purpose
Implements secure user authentication using JWT tokens.

### Key Features
- JWT access tokens (15min expiry)
- Refresh token rotation
- Session invalidation
- Rate limiting

### Integration Points
- Middleware: `auth_middleware.py`
- User service: `user_service.py`
- Config: `auth_config.py`
"""

# L2: Full Content
# Complete documentation, code, examples
# (Stored in AGFS, retrieved on demand)
```

---

## 11.5 Changelog Management

### CHANGELOG.md Format

```markdown
# Changelog

All notable changes to OpenViking are documented here.

## [Unreleased]

### Added
- NotebookLM backend integration

### Changed
- Improved hierarchical retrieval algorithm

### Fixed
- Queue processing race condition

## [1.0.0] - 2026-02-05

### Added
- Initial public release
- AsyncOpenViking client
- VikingDB vector storage
- PDF, Markdown, HTML parsing
- Semantic search with traces
- Session management
- Memory extraction

### Known Issues
- Large PDF parsing may timeout
- No distributed AGFS support yet
```

### Version Numbering

| Version | Meaning |
|---------|---------|
| Major (X.0.0) | Breaking API changes |
| Minor (0.X.0) | New features, backward compatible |
| Patch (0.0.X) | Bug fixes only |
| Pre-release | X.Y.Z-alpha, X.Y.Z-beta, X.Y.Z-rc.1 |

---

## 11.6 Genesis Specification

### Genesis Document Structure

```
genesis_spec/
+-- README.md                    # Genesis overview
+-- section_guides/
    +-- OpenViking_Section_01_Introduction.md
    +-- OpenViking_Section_02_Product_Requirements.md
    +-- OpenViking_Section_03_Technology_Stack.md
    +-- OpenViking_Section_04_Process_Flowcharts.md
    +-- OpenViking_Section_05_Architecture_Design.md
    +-- OpenViking_Section_06_Data_Models.md
    +-- OpenViking_Section_07_Security_Compliance.md
    +-- OpenViking_Section_08_Testing_Strategy.md
    +-- OpenViking_Section_09_Monitoring_Observability.md
    +-- OpenViking_Section_10_Deployment_Operations.md
    +-- OpenViking_Section_11_Documentation_Knowledge.md
    +-- OpenViking_Section_12_Reference_Collections.md
```

### Section Template

```markdown
# OpenViking Genesis Specification - Section XX: [Title]

**Version**: 1.0.0
**Last Updated**: YYYY-MM-DD
**Status**: Draft | Review | Production Ready

---

## XX.1 [Subsection Title]

### [Topic]

[Content with diagrams, tables, code examples]

---

## XX.N Quality Checklist

- [ ] Requirement 1
- [ ] Requirement 2
- [ ] Requirement 3
```

---

## 11.7 Documentation Generation

### Automated Docs from Code

```python
# Generate API docs from docstrings
# Using pdoc or sphinx

# pdoc approach
pdoc --html --output-dir docs/api openviking

# sphinx approach
sphinx-apidoc -o docs/source openviking
sphinx-build -b html docs/source docs/build
```

### Documentation CI Pipeline

```yaml
# .github/workflows/docs.yml
name: Documentation

on:
  push:
    branches: [main]
    paths:
      - 'openviking/**'
      - 'docs/**'

jobs:
  build-docs:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Setup Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: |
          pip install -e ".[docs]"

      - name: Build documentation
        run: |
          cd docs && make html

      - name: Deploy to GitHub Pages
        uses: peaceiris/actions-gh-pages@v3
        with:
          github_token: ${{ secrets.GITHUB_TOKEN }}
          publish_dir: ./docs/_build/html
```

---

## 11.8 Quality Checklist

- [x] Documentation tiers defined
- [x] API documentation standards set
- [x] Tutorial structure established
- [x] Knowledge lifecycle documented
- [x] Changelog format specified
- [x] Genesis structure explained
- [x] Automation pipeline included
