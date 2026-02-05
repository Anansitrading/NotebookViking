# OpenViking Genesis Specification

**Version**: 1.0.0
**Generated**: 2026-02-05
**Status**: Production Ready

---

## Overview

This Genesis Specification provides comprehensive documentation of the OpenViking codebase, optimized for AI agent consumption. It follows a 12-section format covering all aspects from product requirements to deployment operations.

## Sections

| Section | Title | Description |
|---------|-------|-------------|
| [01](./section_guides/OpenViking_Section_01_Introduction.md) | Introduction | Executive summary, vision, scope, stakeholders |
| [02](./section_guides/OpenViking_Section_02_Product_Requirements.md) | Product Requirements | 30 FRs, 15 NFRs, user stories, acceptance criteria |
| [03](./section_guides/OpenViking_Section_03_Technology_Stack.md) | Technology Stack | Dependencies, runtime requirements, version matrix |
| [04](./section_guides/OpenViking_Section_04_Process_Flowcharts.md) | Process Flowcharts | ASCII diagrams for all major workflows |
| [05](./section_guides/OpenViking_Section_05_Architecture_Design.md) | Architecture Design | Module structure, patterns, APIs, ADRs |
| [06](./section_guides/OpenViking_Section_06_Data_Models.md) | Data Models | Entity definitions, schemas, relationships |
| [07](./section_guides/OpenViking_Section_07_Security_Compliance.md) | Security & Compliance | Threat model, auth, data protection |
| [08](./section_guides/OpenViking_Section_08_Testing_Strategy.md) | Testing Strategy | Test pyramid, examples, CI integration |
| [09](./section_guides/OpenViking_Section_09_Monitoring_Observability.md) | Monitoring & Observability | Metrics, traces, alerts, dashboards |
| [10](./section_guides/OpenViking_Section_10_Deployment_Operations.md) | Deployment & Operations | Docker, config, runbooks, scaling |
| [11](./section_guides/OpenViking_Section_11_Documentation_Knowledge.md) | Documentation & Knowledge | Doc tiers, API docs, knowledge lifecycle |
| [12](./section_guides/OpenViking_Section_12_Reference_Collections.md) | Reference Collections | Code examples, error codes, glossary |

## Quick Navigation

### For New Contributors
1. Start with [Section 01: Introduction](./section_guides/OpenViking_Section_01_Introduction.md)
2. Review [Section 05: Architecture](./section_guides/OpenViking_Section_05_Architecture_Design.md)
3. Check [Section 08: Testing](./section_guides/OpenViking_Section_08_Testing_Strategy.md)

### For AI Agents
1. Read [Section 05: Architecture](./section_guides/OpenViking_Section_05_Architecture_Design.md) for module structure
2. Reference [Section 06: Data Models](./section_guides/OpenViking_Section_06_Data_Models.md) for entity schemas
3. Use [Section 12: Reference](./section_guides/OpenViking_Section_12_Reference_Collections.md) for code examples

### For Operators
1. Follow [Section 10: Deployment](./section_guides/OpenViking_Section_10_Deployment_Operations.md) for setup
2. Monitor via [Section 09: Observability](./section_guides/OpenViking_Section_09_Monitoring_Observability.md)
3. Secure with [Section 07: Security](./section_guides/OpenViking_Section_07_Security_Compliance.md)

## Key Concepts

### Viking URI Scheme
```
viking://[scope]/[path]/[name]

Scopes: user, agent, resources, session
```

### Tiered Summarization
- **L0**: Abstract (~100 tokens) - One-sentence summary
- **L1**: Overview (~2000 tokens) - Key concepts and features
- **L2**: Full Content - Complete documentation

### Storage Backends
- **VikingDB**: Vector database for fast semantic search
- **NotebookLM**: Google's LLM-native semantic understanding

## Document Conventions

- **ASCII Diagrams**: Used for portability across environments
- **Code Examples**: Python 3.9+ with async/await patterns
- **Tables**: Used for structured reference data
- **Checklists**: Quality gates at end of each section

## Maintenance

This specification should be updated when:
- Major features are added
- APIs change
- Architecture decisions are made
- New deployment modes are supported

## License

Same license as OpenViking main project.
