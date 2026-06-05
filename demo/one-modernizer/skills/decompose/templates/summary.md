# Decomposition Summary: {{FEATURE_NAME}}

## Overview

- **Migration Strategy**: {{from assessment}}
- **Target Platform**: {{from assessment}}
- **Modules Analyzed**: {{count}}
- **Source Files Read**: {{count}}

## Extraction Counts

| Category        | Count |
| --------------- | ----- |
| Business Rules  | {{n}} |
| Data Structures | {{n}} |
| Sequence Flows  | {{n}} |
| Error Handlers  | {{n}} |
| Test Cases      | {{n}} |
| Unknowns        | {{n}} |

## Business Rules (Plain English)

### Validations

1. {{BR-001}}: {{description}}
2. {{BR-002}}: {{description}}

### Calculations

1. {{BR-xxx}}: {{description}}

### State Transitions

1. {{BR-xxx}}: {{description}}

### Routing / Authorization / Transformations

1. {{BR-xxx}}: {{description}}

## Data Structures

| Structure | Fields    | Used By Rules | Source        |
| --------- | --------- | ------------- | ------------- |
| {{name}}  | {{count}} | {{rule IDs}}  | {{file:line}} |

## Critical Flows

| Flow     | Steps     | Trigger            | Errors                   |
| -------- | --------- | ------------------ | ------------------------ |
| {{name}} | {{count}} | {{what starts it}} | {{count of error paths}} |

## Test Coverage

- **Rules with tests**: {{n}}/{{total}} ({{%}})
- **Flows with tests**: {{n}}/{{total}} ({{%}})
- **Boundary tests**: {{n}}
- **Negative tests**: {{n}}

## Unknowns & Ambiguities

| #   | Description        | Source        | Impact                  |
| --- | ------------------ | ------------- | ----------------------- |
| 1   | {{what's unclear}} | {{file:line}} | {{what could go wrong}} |

## Diagrams

See `diagrams.md` for:

- Sequence diagrams (one per flow)
- State machine (if state transitions exist)
- Entity relationship diagram
- Activity diagrams for complex branching
