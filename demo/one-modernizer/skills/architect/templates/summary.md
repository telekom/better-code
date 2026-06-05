# Architecture Summary: {{FEATURE_NAME}}

## Target Platform

{{Runtime, cloud provider, key infrastructure choices}}

## Services

| Service  | Responsibility   | Tech Stack    | Data Owned          | Flows Handled     |
| -------- | ---------------- | ------------- | ------------------- | ----------------- |
| {{name}} | {{what it does}} | {{framework}} | {{tables/entities}} | {{FLOW-xxx list}} |

## Technology Stack

- **Language**: {{language}}
- **Framework**: {{framework + version}}
- **Database**: {{DB + managed/self-hosted}}
- **Messaging**: {{broker or "none"}}
- **API Style**: {{REST/gRPC/GraphQL/events}}
- **Deployment**: {{K8s/serverless/PaaS/VM}}

## Architecture Decisions (ADRs)

| #   | Decision  | Status     |
| --- | --------- | ---------- |
| 001 | {{title}} | {{status}} |
| 002 | {{title}} | {{status}} |

## Mapping Completeness

| Category        | Mapped | Total     | Coverage |
| --------------- | ------ | --------- | -------- |
| Business Rules  | {{n}}  | {{total}} | {{%}}    |
| Flows           | {{n}}  | {{total}} | {{%}}    |
| Data Structures | {{n}}  | {{total}} | {{%}}    |
| Errors          | {{n}}  | {{total}} | {{%}}    |
| Interfaces      | {{n}}  | {{total}} | {{%}}    |

## Project Structure

```
{{scaffold overview — top-level folders and services}}
```

## Diagrams

See `diagrams.md` for:

- C4 Context (system boundary + external systems)
- C4 Container (services, databases, queues)
- C4 Component (per service internals)
- Data flow (sequence diagrams)
- Deployment view
