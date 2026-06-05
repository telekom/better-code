# SME Interview Protocol

Use these structured questions based on detected tech stack and the SME's role. Ask interactively — wait for answers before proceeding. Adapt questions based on what you've already learned from the codebase scan.

## Architect / Tech Lead (15 questions)

1. What are the system's major subsystems and how do they communicate? (sync/async, protocols)
2. Which subsystems were designed together vs. bolted on later?
3. What are the hard boundaries the new system must preserve? (regulatory, latency, data isolation)
4. What design decisions would you change if you could start over?
5. Where is the "accidental complexity" — code that exists because of constraints no longer relevant?
6. What are the known single points of failure?
7. What are the scalability limits today? (users, transactions/sec, data volume)
8. What disaster recovery mechanisms exist? (failover, backup, replication)
9. Are there any undocumented protocols or wire formats between subsystems?
10. What shared libraries or frameworks are used across subsystems?
11. What is the deployment topology? (how many instances, regions, load balancing)
12. What monitoring/observability exists? Where are the blind spots?
13. Are there any planned or in-progress changes that would affect migration scope?
14. What past migration or modernization attempts have been made? Why did they succeed/fail?
15. What integrations with external partners/vendors are hardest to change?

## DBA (12 questions)

1. What is the schema evolution history? (how often do DDL changes happen)
2. Which tables are the largest by row count and storage? (top 10)
3. What partitioning strategy is in place? Is it effective?
4. Are there performance-critical stored procedures? Which ones are called most?
5. What indexes are critical for performance? Any covering indexes?
6. What replication topology exists? (DataGuard, GoldenGate, logical replication)
7. Are there any cross-schema or cross-database dependencies? (DB links, synonyms)
8. What data retention/archival policies exist? Are they enforced?
9. What are the backup/recovery RPO and RTO targets? Are they met?
10. Are there known data quality issues? (orphaned records, constraint violations)
11. What application-level locking patterns are used? (SELECT FOR UPDATE, advisory locks)
12. What Oracle features are in heavy use? (Advanced Queuing, Spatial, Text, XMLDB, Streams)

## Operations / SRE (10 questions)

1. What is the deployment process? (manual, CI/CD, blue-green, canary)
2. What batch windows exist and what SLAs do they have?
3. What are the top 5 most common incidents in the past year?
4. What monitoring/alerting tools are in place? What pages people?
5. What runbooks exist? Where are they stored?
6. What capacity planning has been done? When is the next scaling cliff?
7. What manual operational tasks are performed daily/weekly?
8. What is the change management process? (freeze windows, approval gates)
9. How long does a full system restart take? What's the startup dependency order?
10. What are the network/firewall constraints between environments?

## Business Analyst / Product Owner (10 questions)

1. What are the top 5 business processes this system supports?
2. Which processes are revenue-critical vs. back-office?
3. What regulatory frameworks apply? (SOX, PCI-DSS, GDPR, HIPAA, Basel III)
4. What audit trail requirements exist? What must be logged/retained?
5. Are there seasonal peaks? (end of month, quarter close, holiday)
6. What SLAs are contractually committed to customers/partners?
7. What business rules have changed recently or are expected to change?
8. What data is classified as sensitive/PII/restricted?
9. Who are the end users and how do they interact with the system? (screens, reports, APIs)
10. What is the acceptable downtime during migration? (big bang vs. gradual)

## Developer / Module Owner (8 questions)

1. Which modules do you own or know best?
2. What are the hardest parts of this code to understand? Why?
3. Are there known bugs or workarounds that aren't documented anywhere?
4. What code do you know is dead but nobody has removed?
5. What tribal knowledge exists that isn't in any document or comment?
6. What are the testing pain points? What's hard to test and why?
7. What build/deploy shortcuts or tricks does the team rely on?
8. If you could only migrate 3 modules perfectly, which would you choose and why?

## Stack-Specific Triggers

When the codebase contains:

- **COBOL/.cbl** → Ask DBA + Operations questions. Add: "What JCL scheduling tool is used? Who maintains the batch schedule?"
- **Oracle/.pls/.pkb** → Ask DBA questions in full. Add: "Are there any Oracle-specific features we're locked into? (Spatial, Text, AQ)"
- **C/C++** → Ask Architect questions. Add: "What memory management patterns are used? Any custom allocators? Signal handlers?"
- **CICS references** → Add: "What CICS regions exist? What are the transaction IDs and their SLAs?"
- **MQ/messaging** → Add: "What message formats exist? Are there schema registries? What happens if a message is lost?"

## Output Templates

Answers should be captured in:

- `.migration/discovery/ownership-matrix.md` — who owns what
- `.migration/discovery/compliance-constraints.md` — regulatory requirements
- `.migration/discovery/sla-registry.md` — SLA commitments
- `.migration/discovery/unknowns.md` — questions that couldn't be answered (flag these for follow-up)
