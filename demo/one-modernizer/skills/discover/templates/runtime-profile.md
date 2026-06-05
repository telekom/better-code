# Runtime Profile

## Hot Paths (Most Active)

| Program/Endpoint | Daily Executions | Avg Response | P99 Response | Error Rate |
| ---------------- | ---------------- | ------------ | ------------ | ---------- |
| {{name}}         | {{count}}        | {{ms}}       | {{ms}}       | {{%}}      |

## Dead Code Candidates

| Program  | Evidence                    | Confidence                     | Last Known Execution |
| -------- | --------------------------- | ------------------------------ | -------------------- |
| {{name}} | {{no runtime + no callers}} | {{confirmed/likely/uncertain}} | {{date or never}}    |

## Performance Hotspots

| Component | Metric                   | Current Value | Threshold | At Risk?   |
| --------- | ------------------------ | ------------- | --------- | ---------- |
| {{name}}  | {{response time/CPU/IO}} | {{value}}     | {{SLA}}   | {{yes/no}} |

## Data Volume Profile

| Table/Dataset | Row Count    | Size (GB) | Growth Rate  | Archival?  |
| ------------- | ------------ | --------- | ------------ | ---------- |
| {{name}}      | {{millions}} | {{GB}}    | {{GB/month}} | {{yes/no}} |

## Batch Execution Frequency

| Job      | Schedule      | Avg Duration | Last Run | Status      |
| -------- | ------------- | ------------ | -------- | ----------- |
| {{name}} | {{daily/etc}} | {{minutes}}  | {{date}} | {{ok/fail}} |

## Resource Utilization

| Resource       | Peak Usage | Capacity  | Headroom |
| -------------- | ---------- | --------- | -------- |
| {{CPU/Mem/IO}} | {{%}}      | {{total}} | {{%}}    |
