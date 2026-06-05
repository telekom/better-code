# Feature: {{FEATURE_NAME}}

## Business Capability

{{What this feature does for users/business in 2-3 sentences}}

## Current Implementation

### Modules

| Module   | Role                | Complexity                  | Source                        |
| -------- | ------------------- | --------------------------- | ----------------------------- |
| {{name}} | {{primary/support}} | {{Simple/Moderate/Complex}} | discovery/modules/{{name}}.md |

### Data Flow

{{How data moves through this feature: entry → processing → storage → output}}

### External Interfaces

| Type                      | Target   | Protocol     | Notes                         |
| ------------------------- | -------- | ------------ | ----------------------------- |
| {{DB/API/MQ/File/Screen}} | {{name}} | {{protocol}} | {{frequency, error handling}} |

## Migration Strategy

### Approach: {{Rewrite / Refactor / Replace / Replatform / Retain / Retire}}

### Target Design

{{How this feature should work in the target system — which service(s), which patterns, what technology}}

### Feature Parity

| Current Behavior     | Target Behavior     | Gap/Change           |
| -------------------- | ------------------- | -------------------- |
| {{what it does now}} | {{what it will do}} | {{what's different}} |

### Data Migration

{{How data moves from legacy to target — ETL, dual-write, CDC, bulk load}}

## Dependencies

### Depends On (migrate these first)

- {{feature}} — {{why: shared DB, API call, shared data structure}}

### Depended Upon By

- {{feature}} — {{why}}

## Risks

- {{specific risk with severity: High/Medium/Low and mitigation strategy}}

## Priority

- **Business Value**: {{Critical / High / Medium / Low}}
- **Usage Frequency**: {{High / Medium / Low / Dead}} — {{source: runtime data or estimate}}
- **Migration Complexity**: {{S / M / L / XL}}
- **Recommended Wave**: {{1 / 2 / 3 / ... / Retain / Retire}}
