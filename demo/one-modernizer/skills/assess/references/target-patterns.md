# Target Architecture Patterns

Common legacy-to-modern technology mappings. Use these as starting points — always validate against the specific system's constraints.

## COBOL → Java/Spring Boot or .NET

| Legacy Pattern                   | Target Pattern                                          |
| -------------------------------- | ------------------------------------------------------- |
| COBOL batch program              | Spring Batch job / .NET Worker Service                  |
| CICS online transaction          | REST API endpoint (Spring MVC / ASP.NET)                |
| VSAM file                        | PostgreSQL table or object storage                      |
| COPY statement (shared copybook) | Shared DTO/model library (Maven module / NuGet package) |
| WORKING-STORAGE variables        | Service state / request-scoped beans                    |
| PERFORM paragraph                | Private method                                          |
| CALL 'PROGRAM'                   | Service-to-service call (HTTP/gRPC) or library call     |
| EXEC SQL (embedded)              | JPA/Hibernate or Dapper                                 |
| EXEC CICS SEND MAP               | REST response / React component                         |
| JCL DD DSN=                      | Cloud storage path (S3, GCS, Azure Blob)                |
| GDG (Generation Data Group)      | Versioned object storage with retention policy          |

**Key decisions**:

- Batch: Keep batch paradigm (Spring Batch) or convert to event-driven?
- CICS screens: REST API + SPA, or server-rendered?
- Copybooks: One shared library or per-service DTOs?

## PL/SQL → Application Layer

| Legacy Pattern         | Target Pattern                                       |
| ---------------------- | ---------------------------------------------------- |
| Stored procedure       | Service method (business logic in application layer) |
| Package (spec + body)  | Service class with interface                         |
| Trigger                | Event handler / domain event subscriber              |
| Cursor loop            | Stream processing / repository query with pagination |
| DBMS_SCHEDULER job     | Orchestrator (Airflow, Temporal, Step Functions)     |
| DBMS_OUTPUT            | Structured logging                                   |
| Autonomous transaction | Saga pattern / outbox pattern                        |
| PRAGMA EXCEPTION_INIT  | Application-level error hierarchy                    |
| Materialized view      | Read model / CQRS query side / cache                 |
| DB link                | Service-to-service API call                          |
| UTL_FILE               | Cloud storage SDK                                    |
| UTL_HTTP               | HTTP client (RestTemplate, HttpClient)               |
| Bulk FORALL/COLLECT    | Batch insert via JDBC/bulk API                       |

**Key decisions**:

- Keep stored procedures for data-intensive operations? Or move everything out?
- Triggers → synchronous event handlers or async event bus?
- How to handle transaction boundaries that span multiple services?

## Oracle → PostgreSQL / Cloud SQL

| Oracle                         | PostgreSQL                                     | Notes                          |
| ------------------------------ | ---------------------------------------------- | ------------------------------ |
| NUMBER(p,s)                    | NUMERIC(p,s)                                   | Direct mapping                 |
| VARCHAR2(n)                    | VARCHAR(n)                                     | Semantics identical            |
| DATE (includes time)           | TIMESTAMP                                      | Oracle DATE has time component |
| CLOB                           | TEXT                                           | No size limit in PG            |
| BLOB                           | BYTEA or large object                          | BYTEA for < 1GB                |
| SEQUENCE.NEXTVAL               | nextval('seq') or GENERATED ALWAYS AS IDENTITY |                                |
| CONNECT BY                     | WITH RECURSIVE                                 | Recursive CTE                  |
| ROWNUM                         | LIMIT/OFFSET or ROW_NUMBER()                   |                                |
| NVL()                          | COALESCE()                                     |                                |
| DECODE()                       | CASE WHEN                                      |                                |
| SYSDATE                        | NOW() or CURRENT_TIMESTAMP                     |                                |
| (+) outer join                 | LEFT/RIGHT JOIN                                | Standard SQL                   |
| MERGE                          | INSERT ... ON CONFLICT                         | Upsert                         |
| DBMS_LOB                       | bytea operations or lo\_\* functions           |                                |
| Partitioning (RANGE/LIST/HASH) | Native partitioning (PG 10+)                   | Declarative syntax             |
| Global temp tables             | Unlogged tables or temp tables                 | Different semantics            |
| Synonyms                       | Schema search_path or views                    |                                |

**Key decisions**:

- Managed (Cloud SQL, RDS, Aurora) or self-hosted?
- Same schema or redesign during migration?
- Online migration (CDC) or offline (dump and load)?

## C++ Monolith → Microservices

| Legacy Pattern                   | Target Pattern                                     |
| -------------------------------- | -------------------------------------------------- |
| Shared memory IPC                | Message queue (Kafka, RabbitMQ, NATS)              |
| DLL/SO dynamic linking           | Container with gRPC/REST interface                 |
| Global variables                 | Service state / configuration service              |
| Callback functions               | Event subscription / webhook                       |
| Thread pool                      | Container orchestration (K8s HPA)                  |
| File-based config (.ini, .cfg)   | ConfigMap / environment variables / config service |
| Socket server                    | Load-balanced service behind ingress               |
| Monolithic build (single binary) | Per-service build pipeline                         |
| Header files (shared interfaces) | Protobuf / OpenAPI schema (contract-first)         |
| Make/CMake build                 | Container build (Dockerfile) + CI/CD               |

**Key decisions**:

- Keep C++ for performance-critical services? Or rewrite in Go/Rust/Java?
- How to decompose: by module boundary, by domain, by data ownership?
- Synchronous (gRPC) or asynchronous (events) communication?

## Mainframe Batch → Cloud

| Legacy Pattern                 | Target Pattern                                    |
| ------------------------------ | ------------------------------------------------- |
| JCL JOB card                   | Workflow definition (Airflow DAG, Step Functions) |
| EXEC PGM= step                 | Task/container in workflow                        |
| DD DSN= (input dataset)        | Cloud storage read (S3/GCS trigger)               |
| DD DSN= (output dataset)       | Cloud storage write                               |
| SORT utility (DFSORT/SYNCSORT) | Spark job / SQL ORDER BY / stream sort            |
| IDCAMS REPRO                   | Data pipeline copy step                           |
| IEBGENER                       | File copy / transform step                        |
| Checkpoint/restart             | Workflow retry with idempotent steps              |
| GDG cycling                    | Object versioning with lifecycle policy           |
| Control-M schedule             | Cloud scheduler (Cloud Scheduler, EventBridge)    |
| Abend handling (COND=)         | Workflow error handling / dead letter queue       |
| SYSOUT/SYSPRINT                | Cloud logging (CloudWatch, Cloud Logging)         |
| Tape/DASD allocation           | Storage class (hot/warm/cold) selection           |

**Key decisions**:

- Keep batch paradigm (scheduled nightly) or move to event-driven (process as data arrives)?
- Orchestrator: managed (Step Functions) or self-hosted (Airflow, Temporal)?
- How to handle the batch window constraint relaxation?

## File-Based Integration → Event-Driven

| Legacy Pattern                   | Target Pattern                             |
| -------------------------------- | ------------------------------------------ |
| Flat file drop (CSV/fixed-width) | Event stream (Kafka topic / Pub-Sub)       |
| Polling for file arrival         | Event trigger / webhook                    |
| File-based ETL                   | Streaming ETL (Kafka Connect, Dataflow)    |
| Batch file transfer (FTP/SFTP)   | API call or event publish                  |
| Header/trailer record validation | Schema validation (Avro, JSON Schema)      |
| Sequence number tracking         | Offset management / exactly-once semantics |
| Manual reconciliation            | Automated reconciliation service           |

## Anti-Patterns in Target Design

- **Distributed monolith**: Microservices that must deploy together and share a database
- **Chatty interfaces**: Too many synchronous calls between services (use events or aggregate)
- **Shared database**: Multiple services writing to the same tables (own your data)
- **Technology tourism**: Picking shiny tech over proven boring tech that fits
- **Over-decomposition**: 50 microservices for a 10-person team (match team topology)
- **Ignoring CAP**: Assuming strong consistency in a distributed system
- **No observability plan**: Migrating to distributed without tracing, metrics, centralized logging
