# Verification Rules

What to check after generating each file type. Verification runs after EVERY generated file — no exceptions.

## Universal Checks (all file types)

1. **Parseable** — file is syntactically valid for its language
2. **No placeholders** — no TODO, FIXME, "implement me", or empty method bodies
3. **Constitution compliance** — naming, structure, layers match constitution.md
4. **Import integrity** — only imports/references classes that exist (generated earlier or framework-provided)
5. **Spec coverage** — implements ALL spec_refs listed in the task (not partial)

## By File Type

### Entity / Domain Model

- All fields from spec data_model are present with correct types
- Relationships match spec (one-to-many, etc.)
- Constraints present (NOT NULL, unique, checks)
- Target types used (not legacy types)
- Equals/hashCode if needed by framework

### Repository / Data Access

- Query methods match the data access patterns in flows
- Return types match entity types
- Pagination for list queries
- No business logic in repository

### Service / Domain Logic

- Every assigned BR-xxx has implementation logic
- Method signatures match implementation spec exactly
- Dependencies injected (not instantiated)
- Transaction boundaries where specified
- No HTTP/infrastructure concerns in domain layer

### Controller / API Handler

- Endpoint matches mapping (method, path)
- Request/response DTOs defined
- Input validation present
- Error responses mapped to HTTP status codes
- No business logic — delegates to service layer

### DTO / Request-Response

- Fields match the API contract
- Validation annotations present (where applicable)
- Serialization works (constructor, getters, or records)

### Event Publisher / Consumer

- Event name matches blueprint events_published/consumed
- Schema matches contract definition
- Idempotency handling for consumers
- Error/retry handling for failed publishes

### Exception / Error Handler

- Maps to ERR-xxx from spec
- Correct HTTP status code
- Meaningful error message
- Doesn't leak internal details

### Test

- Covers the TC-xxx it claims to cover
- Arrange/Act/Assert structure
- Meaningful assertions (not just "no exception")
- Mocks only what's necessary (unit) or uses real infra (integration)
- Test name describes the scenario

### Migration / DDL

- Table name matches mapping target_table
- Columns match entity fields
- Constraints present (PK, FK, NOT NULL, indexes)
- Reversible (has both up and down)

### Configuration

- Connection strings use environment variables (not hardcoded)
- Sensible defaults for local dev
- No secrets in config files

### Infrastructure (Dockerfile, docker-compose, Helm)

- Multi-stage build (Dockerfile)
- Health check defined
- Resource limits set
- Environment variables for config

## Language-Specific Syntax Checks

### Java

- Compiles: `javac -cp <classpath> <file>` or just verify it parses
- No raw types (use generics)
- No checked exceptions that aren't declared
- Records for DTOs (Java 16+)

### Go

- Builds: `go build ./...` or `go vet`
- Exported types/functions are capitalized
- Errors returned, not panicked
- Context passed where needed

### Python

- Parses: `python -m py_compile <file>`
- Type hints present
- No bare `except:`
- Pydantic models for DTOs

### .NET / C#

- Builds: `dotnet build`
- Nullable reference types enabled
- Async/await for I/O operations
- Records for DTOs (C# 9+)

## Post-Batch Checks (after all tasks in a service complete)

1. **Compile the entire service** — all files together must build
2. **No unused imports** — clean up any dead references
3. **No circular dependencies** — domain doesn't import controller, etc.
4. **API contract consistency** — generated OpenAPI matches actual endpoints
5. **Event schema consistency** — published events match consumer expectations
