# Extraction Patterns by Language

How to identify business rules, flows, data models, and error handling in each legacy language.

## COBOL

### Business Rules

| Code Pattern                    | Rule Type              | Example                                    |
| ------------------------------- | ---------------------- | ------------------------------------------ |
| `IF condition`                  | validation/routing     | `IF WS-AMOUNT > WS-CREDIT-LIMIT`           |
| `EVALUATE TRUE`                 | routing (multi-branch) | `EVALUATE TRUE WHEN condition...`          |
| `88-level condition names`      | validation             | `88 VALID-STATUS VALUE 'A' 'B' 'C'`        |
| `COMPUTE` with business formula | calculation            | `COMPUTE WS-TAX = WS-AMOUNT * WS-TAX-RATE` |
| `MOVE` with conditional context | state-transition       | `MOVE 'APPROVED' TO WS-ORDER-STATUS`       |
| `INSPECT/STRING/UNSTRING`       | transformation         | Data format conversion                     |

### Sequence Flows

- `PERFORM paragraph-name` — flow step (call within program)
- `CALL 'PROGRAM'` — inter-program call (cross-module flow)
- `EXEC CICS SEND/RECEIVE` — user interaction boundary
- `EXEC SQL` — database interaction step
- `EXEC CICS LINK/XCTL` — transaction routing

### Data Model

- `COPY copybook-name` — shared data structure (look up the .cpy file)
- `01 level` in WORKING-STORAGE — local data structure
- `01 level` in LINKAGE SECTION — interface contract (parameters)
- `FD` entries — file record layouts
- `EXEC SQL DECLARE cursor` — result set structure

### Error Handling

- `EXEC SQL` followed by `IF SQLCODE NOT = 0` — DB error
- `EXEC CICS HANDLE CONDITION` — CICS error routing
- `ON SIZE ERROR` — arithmetic overflow
- `INVALID KEY` — file I/O error
- `AT END` — end-of-file / end-of-cursor

### Performance Patterns (note but don't extract as rules)

- `SEARCH ALL` — binary search (indexed table)
- `PERFORM VARYING` with large iteration — batch loop
- `START/READ NEXT` — sequential file processing

---

## PL/SQL

### Business Rules

| Code Pattern              | Rule Type              | Example                                 |
| ------------------------- | ---------------------- | --------------------------------------- |
| `IF condition THEN`       | validation/routing     | `IF v_balance < v_withdrawal THEN`      |
| `CASE WHEN`               | routing                | Multi-branch business logic             |
| `CHECK constraint`        | validation             | `CONSTRAINT chk_amt CHECK (amount > 0)` |
| `BEFORE/AFTER trigger`    | state-transition       | Automatic state changes on DML          |
| Function with calculation | calculation            | `RETURN v_base * v_rate * v_factor`     |
| `RAISE_APPLICATION_ERROR` | validation (rejection) | Business rule violation                 |

### Sequence Flows

- Procedure/function calls — flow steps
- `DBMS_SCHEDULER` jobs — batch triggers
- Cursor open/fetch/close loops — iteration patterns
- `AUTONOMOUS_TRANSACTION` — independent sub-flow
- `PIPE ROW` — streaming output

### Data Model

- `CREATE TABLE` — entity definition
- `%ROWTYPE` / `%TYPE` — type inheritance
- `TYPE ... IS RECORD` — composite structure
- `TYPE ... IS TABLE OF` — collection type
- Package-level variables — shared state

### Error Handling

- `EXCEPTION WHEN` blocks — named exception handlers
- `WHEN OTHERS THEN` — catch-all
- `PRAGMA EXCEPTION_INIT` — custom error codes
- `SQLCODE` / `SQLERRM` — error introspection
- `RAISE` / `RAISE_APPLICATION_ERROR` — error propagation

---

## C / C++

### Business Rules

| Code Pattern                             | Rule Type          | Example                       |
| ---------------------------------------- | ------------------ | ----------------------------- |
| `if (condition)`                         | validation/routing | `if (amount > limit)`         |
| `switch/case`                            | routing            | Multi-branch dispatch         |
| `assert()`                               | validation (debug) | Invariant enforcement         |
| Arithmetic expressions                   | calculation        | `tax = base * rate`           |
| Enum comparisons                         | state-transition   | `if (state == STATE_PENDING)` |
| `#define` / `const` with business values | configuration      | Thresholds, limits, rates     |

### Sequence Flows

- Function calls — flow steps
- Callback function pointers — event-driven flow
- `main()` → init → process → cleanup — lifecycle
- Thread creation / `pthread_create` — parallel flows
- Signal handlers — interrupt flows

### Data Model

- `struct` / `class` — entity definition
- `typedef` — type aliases (often domain-meaningful)
- Header file (`.h`) declarations — interface contracts
- `enum` — state/status definitions
- Array/linked list of structs — collections

### Error Handling

- Return code checking (`if (ret != 0)`) — C-style errors
- `errno` inspection — system error handling
- `try/catch` (C++) — exception handling
- `goto cleanup` pattern — resource cleanup on error
- `setjmp/longjmp` — non-local error recovery (rare)

---

## Java

### Business Rules

| Code Pattern                      | Rule Type          | Example                            |
| --------------------------------- | ------------------ | ---------------------------------- |
| `if/else`                         | validation/routing | `if (!user.hasPermission(action))` |
| `switch` / pattern matching       | routing            | Multi-branch logic                 |
| `@Valid` / `@NotNull` / `@Size`   | validation         | Bean validation annotations        |
| Stream `.filter()` with predicate | validation/routing | `orders.filter(o -> o.isValid())`  |
| Business method with return value | calculation        | `calculateDiscount(order)`         |
| State pattern / enum transitions  | state-transition   | `order.transitionTo(SHIPPED)`      |

### Sequence Flows

- Method calls — flow steps
- `@Transactional` boundary — transaction scope
- `@Async` / `CompletableFuture` — async flows
- Event listeners (`@EventListener`) — event-driven
- REST controller methods — API entry points
- `@Scheduled` — batch/cron triggers

### Data Model

- `@Entity` classes — JPA entities (DB-mapped)
- DTOs / Records — transfer objects
- `@Embeddable` — value objects
- Interface definitions — contracts
- `enum` — status/type definitions

### Error Handling

- `try/catch` — exception handling
- `@ExceptionHandler` / `@ControllerAdvice` — global error mapping
- Custom exception classes — domain errors
- `Optional.orElseThrow()` — null handling
- `@Retryable` — retry logic

---

## JCL (Job Control Language)

### Business Rules

- `COND=` parameter — conditional step execution
- `IF/THEN/ELSE/ENDIF` — step-level branching
- `RC` (return code) checks — success/failure routing

### Sequence Flows

- `//stepname EXEC PGM=` — each step is a flow step
- Step ordering (top to bottom) — sequential execution
- `PROC` calls — reusable sub-flows
- `INCLUDE MEMBER=` — shared step templates

### Data Model

- `DD DSN=` — dataset (file) references
- `DISP=(status,normal,abend)` — read/write/create semantics
- `DCB=(RECFM=,LRECL=,BLKSIZE=)` — record format definition
- `GDG` references — versioned datasets

### Error Handling

- `COND=` — skip on prior step failure
- `IF (stepname.RC > 4)` — explicit RC checking
- `//*` RESTART instructions — manual recovery
- `DISP=(,CATLG,DELETE)` — cleanup on abend

---

## General Extraction Tips

1. **Start with entry points**: Find where the feature begins (API endpoint, CICS transaction, batch job start, main())
2. **Follow the call chain**: Trace from entry to exit, noting each decision point
3. **Identify the "happy path" first**: Then go back for error/alternative paths
4. **Look for magic numbers**: Constants that encode business rules (thresholds, limits, rates)
5. **Check configuration**: Properties files, environment variables, DB config tables that affect behavior
6. **Cross-reference comments carefully**: Comments may describe INTENDED behavior, not actual behavior — always trust the code
7. **Watch for dead code**: Commented-out or unreachable code may contain historical business rules — note but mark as "inactive"
