# OpenViking Genesis Specification - Section 02: Product Requirements

**Version**: 1.0.0
**Last Updated**: 2026-02-05
**Status**: Production Ready

---

## 2.1 Functional Requirements

| ID | Requirement | Priority | Status |
|----|-------------|----------|--------|
| FR-001 | Initialize client with local path or remote URLs | P0 | Implemented |
| FR-002 | Add resources from URL, file path, or directory | P0 | Implemented |
| FR-003 | Semantic search across all context types | P0 | Implemented |
| FR-004 | List directory contents via `ls` command | P0 | Implemented |
| FR-005 | Read file content via `read` command | P0 | Implemented |
| FR-006 | Pattern matching via `glob` command | P0 | Implemented |
| FR-007 | Content search via `grep` command | P0 | Implemented |
| FR-008 | Get abstract (L0) for any URI | P0 | Implemented |
| FR-009 | Get overview (L1) for any URI | P0 | Implemented |
| FR-010 | Create semantic relations between contexts | P0 | Implemented |
| FR-011 | Session message management | P0 | Implemented |
| FR-012 | Session compression and archival | P0 | Implemented |
| FR-013 | Memory extraction from sessions | P0 | Implemented |
| FR-014 | Memory deduplication with LLM decisions | P0 | Implemented |
| FR-015 | Parse PDF documents to structured content | P0 | Implemented |
| FR-016 | Parse Markdown with section chunking | P0 | Implemented |
| FR-017 | Parse HTML with web scraping support | P0 | Implemented |
| FR-018 | Parse code with AST-aware chunking | P0 | Implemented |
| FR-019 | Support OpenAI embeddings | P0 | Implemented |
| FR-020 | Support Volcengine embeddings | P0 | Implemented |
| FR-021 | Export context as .ovpack files | P1 | Implemented |
| FR-022 | Import .ovpack files with vectorization | P1 | Implemented |
| FR-023 | Remove resources recursively | P0 | Implemented |
| FR-024 | Move resources with vector sync | P1 | Implemented |
| FR-025 | Create directories in viking:// tree | P1 | Implemented |
| FR-026 | Add skills with vectorization | P0 | Implemented |
| FR-027 | Intent analysis for query planning | P1 | Implemented |
| FR-028 | Hierarchical recursive retrieval | P0 | Implemented |
| FR-029 | Score propagation in retrieval | P1 | Implemented |
| FR-030 | NotebookLM semantic backend | P1 | Implemented |

---

## 2.2 Non-Functional Requirements

| ID | Category | Requirement | Target |
|----|----------|-------------|--------|
| NFR-001 | Performance | Query latency P95 | <500ms |
| NFR-002 | Performance | Document ingestion throughput | <5s/doc |
| NFR-003 | Performance | Batch embedding speed | >100 texts/s |
| NFR-004 | Scalability | Maximum collections | 1000+ |
| NFR-005 | Scalability | Maximum records per collection | 10M+ |
| NFR-006 | Scalability | Concurrent sessions | 100+ |
| NFR-007 | Reliability | Storage durability | 99.99% |
| NFR-008 | Reliability | Queue message delivery | At-least-once |
| NFR-009 | Reliability | Crash recovery | Auto-resume |
| NFR-010 | Usability | API documentation coverage | 100% |
| NFR-011 | Usability | Error messages clarity | Actionable |
| NFR-012 | Maintainability | Test coverage | >80% |
| NFR-013 | Maintainability | Code documentation | Docstrings |
| NFR-014 | Security | API key handling | Env vars only |
| NFR-015 | Security | No credential logging | Enforced |

---

## 2.3 User Stories

### Agent Developer Stories

**US-001**: As an agent developer, I want to add project documentation as context so that my agent can answer questions about the codebase.

**US-002**: As an agent developer, I want to search for relevant context semantically so that I can inject the right information into prompts.

**US-003**: As an agent developer, I want the system to automatically extract memories from conversations so that the agent improves over time.

**US-004**: As an agent developer, I want to see retrieval trajectories so that I can debug why the agent gave a wrong answer.

**US-005**: As an agent developer, I want to add custom skills so that the agent knows how to perform specialized tasks.

### Platform Engineer Stories

**US-006**: As a platform engineer, I want to deploy OpenViking in embedded mode so that I don't need external services.

**US-007**: As a platform engineer, I want to monitor queue status so that I can ensure ingestion is healthy.

**US-008**: As a platform engineer, I want to configure different model backends so that I can optimize cost vs performance.

### Contributor Stories

**US-009**: As a contributor, I want clear extension points so that I can add new file parsers.

**US-010**: As a contributor, I want a registry pattern so that my custom parser integrates seamlessly.

---

## 2.4 Acceptance Criteria

### AC-001: Resource Addition
- Given a valid URL, file path, or directory
- When `add_resource()` is called
- Then the resource is parsed, vectorized, and searchable

### AC-002: Semantic Search
- Given indexed resources
- When `find(query)` is called
- Then returns ranked results with scores >0.1

### AC-003: Session Compression
- Given a session with >8000 tokens
- When commit is triggered
- Then messages are archived with L0/L1/L2 summaries

### AC-004: Memory Extraction
- Given an archived session
- When memory extraction runs
- Then categorized memories are created with deduplication

### AC-005: NotebookLM Backend
- Given NotebookLM configuration
- When semantic search is performed
- Then queries route through NotebookLM's native query API

---

## 2.5 Quality Checklist

- [x] All major features have FRs
- [x] NFRs cover all quality attributes
- [x] Priorities are assigned
- [x] Acceptance criteria are testable
- [x] User stories cover all personas
