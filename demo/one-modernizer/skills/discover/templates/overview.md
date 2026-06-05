# {{PROJECT_NAME}} — Migration Overview

## System Summary

{{2-3 paragraphs: what the system does, who uses it, how it's deployed}}

## Tech Stack

| Layer      | Technology           | Version | Notes |
| ---------- | -------------------- | ------- | ----- |
| Language   | {{e.g., COBOL-85}}   |         |       |
| Runtime    | {{e.g., z/OS, CICS}} |         |       |
| Database   | {{e.g., DB2, IMS}}   |         |       |
| Middleware | {{e.g., MQ Series}}  |         |       |
| Build      | {{e.g., JCL, Make}}  |         |       |

## Codebase Statistics

| Metric                                | Value     |
| ------------------------------------- | --------- |
| Total files                           | {{count}} |
| Total LOC                             | {{count}} |
| Modules/Programs                      | {{count}} |
| Shared structures (copybooks/headers) | {{count}} |
| External interfaces                   | {{count}} |

## Entry Points

| Entry Point | Type                     | Trigger                    | Description      |
| ----------- | ------------------------ | -------------------------- | ---------------- |
| {{name}}    | {{batch/online/service}} | {{schedule/event/request}} | {{what it does}} |

## Module Map

{{List each logical module/community with one-line description}}

| Module   | Files     | Responsibility | Complexity                  |
| -------- | --------- | -------------- | --------------------------- |
| {{name}} | {{count}} | {{purpose}}    | {{simple/moderate/complex}} |

## External Interfaces

### Inbound

| Source   | Protocol           | Format     | Frequency    |
| -------- | ------------------ | ---------- | ------------ |
| {{name}} | {{file/MQ/API/DB}} | {{format}} | {{schedule}} |

### Outbound

| Destination | Protocol           | Format     | Frequency    |
| ----------- | ------------------ | ---------- | ------------ |
| {{name}}    | {{file/MQ/API/DB}} | {{format}} | {{schedule}} |

## Key Dependencies

```
{{ASCII or mermaid diagram showing module relationships}}
```

## Risk Areas

| Area                 | Risk                | Reason  |
| -------------------- | ------------------- | ------- |
| {{module/interface}} | {{high/medium/low}} | {{why}} |

## Graph Navigation

The knowledge graph is at `.migration/discovery/graphify-out/graph.json`. Key queries:

- God nodes: {{list top 3-5 most-connected concepts}}
- Communities: {{count}} clusters identified
- See `.migration/discovery/graphify-out/GRAPH_REPORT.md` for full analysis
