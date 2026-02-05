# OpenViking Genesis Specification - Section 01: Introduction

**Version**: 1.0.0
**Last Updated**: 2026-02-05
**Status**: Production Ready

---

## 1.1 Executive Summary

OpenViking is an open-source **Context Database** designed specifically for AI Agents. It addresses the fundamental challenge of agent development: while data is abundant, high-quality context is hard to come by.

Built by ByteDance's Volcengine Viking Team, OpenViking abandons traditional flat vector storage in favor of a **"filesystem paradigm"** that unifies memories, resources, and skills under a coherent hierarchical structure accessible via the `viking://` URI protocol.

**Key Value Propositions:**
- **Unified Context Management**: File system paradigm eliminates fragmentation across memories, resources, and skills
- **Token Efficiency**: L0/L1/L2 tiered loading reduces context consumption by 60-80%
- **Improved Retrieval**: Directory-recursive search combines positioning with semantic matching
- **Observable Operations**: Visualized retrieval trajectories enable debugging and optimization
- **Self-Evolution**: Automatic session management extracts long-term memory from interactions

---

## 1.2 Project Vision

**Mission**: Define a minimalist context interaction paradigm for AI Agents, allowing developers to completely eliminate context management overhead.

**Vision**: Enable agents to build and evolve their "brain" as intuitively as managing local files - navigating context with `ls`, `find`, `read`, and `grep` operations while maintaining semantic understanding beneath the surface.

**Long-Term Goals:**
1. Become the de-facto standard for agent memory and context management
2. Enable agent self-improvement through automatic memory extraction
3. Provide enterprise-grade observability for context retrieval chains
4. Support multi-modal context (text, images, audio, video)

---

## 1.3 Scope Definition

### In Scope

| Domain | Coverage |
|--------|----------|
| **Storage Backends** | VikingDB (vector), NotebookLM (semantic), Local filesystem |
| **Context Types** | Memories (user/agent), Resources, Skills |
| **Search Modes** | Vector similarity, semantic search, hierarchical retrieval |
| **File Formats** | PDF, Markdown, HTML, Code (30+ languages), Images |
| **Model Integrations** | OpenAI, Volcengine (Doubao), Custom embedders/VLMs |
| **Session Management** | Message history, compression, memory extraction |
| **Client Modes** | Embedded (local), Service (remote), Async/Sync |

### Out of Scope

- Real-time streaming updates (batch processing only)
- Multi-tenancy with strict isolation (single-user focus)
- GPU acceleration for embeddings (CPU-based)
- Mobile/browser runtimes (Python server-side only)
- Direct database administration UI

---

## 1.4 Success Criteria

| Metric | Target | Measurement |
|--------|--------|-------------|
| **Retrieval Accuracy** | >85% relevance | Top-5 results contain answer |
| **Token Reduction** | >60% savings | L0/L1 vs full content |
| **Ingestion Speed** | <5s per document | End-to-end processing |
| **Query Latency** | <500ms P95 | Semantic search response |
| **Memory Extraction Precision** | >80% useful | Deduplicated memories |
| **API Compatibility** | 100% coverage | VikingDBInterface implementation |

---

## 1.5 Document Purpose

This Genesis Specification serves as:

1. **Onboarding Guide**: Comprehensive introduction for new developers
2. **Architecture Reference**: Detailed design documentation
3. **Integration Handbook**: API contracts and extension points
4. **Operations Manual**: Deployment, configuration, and troubleshooting
5. **Quality Standard**: Testing strategy and acceptance criteria

**Intended Audience:**
- AI Agent developers integrating context management
- Platform engineers deploying OpenViking infrastructure
- Contributors extending parsers, embedders, or backends
- Researchers studying hierarchical retrieval algorithms

---

## 1.6 Quality Checklist

- [x] Executive summary captures essence
- [x] Vision is clear and inspiring
- [x] Scope boundaries are explicit
- [x] Success criteria are measurable
- [x] Document purpose is defined
- [x] Target audience is identified
