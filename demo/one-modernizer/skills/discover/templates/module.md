# {{MODULE_NAME}}

## Purpose

{{One paragraph: what this module does and why it exists}}

## Source Files

| File     | Language | Lines     | Role                      |
| -------- | -------- | --------- | ------------------------- |
| {{path}} | {{lang}} | {{count}} | {{primary/helper/config}} |

## Data Structures

{{List key records, copybooks, structs, classes this module defines or consumes}}

- `{{STRUCTURE_NAME}}` — {{description, field count, where defined}}

## Data Flow

### Inbound

- {{Source}} → {{what data, format, frequency}}

### Outbound

- {{Destination}} → {{what data, format, frequency}}

## Business Rules

| #   | Rule            | Source Location | Confidence                   |
| --- | --------------- | --------------- | ---------------------------- |
| 1   | {{description}} | {{file:line}}   | {{clear/inferred/ambiguous}} |

## Dependencies

### Calls (downstream)

- {{module/program/service}} — {{why}}

### Called by (upstream)

- {{module/program/service}} — {{why}}

## External Interfaces

| Type                      | Target   | Details                               |
| ------------------------- | -------- | ------------------------------------- |
| {{DB/File/MQ/API/Screen}} | {{name}} | {{format, frequency, error handling}} |

## Complexity Assessment

**Rating**: {{Simple / Moderate / Complex}}

**Justification**: {{Why — LOC, cyclomatic complexity, coupling, business logic density}}

## Unknowns

- {{Any ambiguous logic, undocumented behavior, or missing context}}
