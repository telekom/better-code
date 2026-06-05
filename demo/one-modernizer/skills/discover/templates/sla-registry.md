# SLA Registry

## Online/Interactive SLAs

| Service/Endpoint | Response Time (p95) | Availability | Measurement Window | Penalty |
| ---------------- | ------------------- | ------------ | ------------------ | ------- |
| {{name}}         | {{ms}}              | {{99.x%}}    | {{monthly}}        | {{$$$}} |

## Batch Processing SLAs

| Job/Chain | Completion Window | Max Duration | Consequence of Miss   |
| --------- | ----------------- | ------------ | --------------------- |
| {{name}}  | {{by HH:MM}}      | {{hours}}    | {{downstream impact}} |

## Integration/Partner SLAs

| Partner/System | Interface    | Commitment        | Direction  |
| -------------- | ------------ | ----------------- | ---------- |
| {{partner}}    | {{API/file}} | {{delivery by X}} | {{in/out}} |

## Data Freshness SLAs

| Data Domain | Max Staleness     | Consumer(s)      | Measurement     |
| ----------- | ----------------- | ---------------- | --------------- |
| {{domain}}  | {{minutes/hours}} | {{who needs it}} | {{how checked}} |

## Recovery Objectives

| System/Module | RTO (Recovery Time) | RPO (Recovery Point) | Current Capability | Gap?       |
| ------------- | ------------------- | -------------------- | ------------------ | ---------- |
| {{name}}      | {{hours}}           | {{minutes/hours}}    | {{actual}}         | {{yes/no}} |

## Seasonal/Peak Considerations

| Period        | Impact      | Adjusted SLA | Freeze Window? |
| ------------- | ----------- | ------------ | -------------- |
| {{month-end}} | {{2x load}} | {{relaxed?}} | {{yes/no}}     |

## Migration Impact on SLAs

- Maximum acceptable downtime during cutover: {{hours}}
- Degraded performance acceptable during transition: {{yes/no, threshold}}
- Parallel-run period required: {{duration}}
- Rollback window after cutover: {{hours}}
