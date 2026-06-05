# Legacy Code Analysis Reference

## Language-Specific Patterns to Detect

For detailed COBOL and C/C++ extraction patterns (business rules, flows, data model, error handling), see the decompose skill's `references/extraction-patterns.md`. This file covers detection cues for module-boundary identification during discovery.

### COBOL (module-boundary cues)

- `COPY` → copybook inclusion = shared data structure boundary
- `CALL` → external program invocation = inter-module edge
- `EXEC CICS LINK/XCTL` → transaction routing = service boundary
- `LINKAGE SECTION` → inter-program interface (API contract)
- `FD` / `SD` → file/sort descriptions (I/O boundaries)

### C/C++ (module-boundary cues)

- `#include "local.h"` → dependency mapping (skip system `<>` includes)
- `extern` → cross-module interfaces
- Socket/pipe calls → IPC boundaries
- Shared library exports → public API surface

### VB6/COM

- `CreateObject`/`New` → COM component instantiation
- `Public Sub/Function` → exposed interface
- `Private` → internal implementation
- `Property Get/Set/Let` → data access patterns
- `DoEvents` → UI event loop interaction
- `On Error` → error handling (often missing)
- `.cls`/`.bas`/`.frm` → module type classification

### Fortran

- `COMMON` blocks → shared global state
- `SUBROUTINE`/`FUNCTION` → callable units
- `MODULE` → encapsulation boundaries
- `INCLUDE` → shared definitions
- Array operations → numerical computation cores
- `OPEN`/`READ`/`WRITE` → file I/O interfaces

## Complexity Indicators

| Signal                                   | Meaning                                         |
| ---------------------------------------- | ----------------------------------------------- |
| Deeply nested conditionals (>4 levels)   | High cyclomatic complexity                      |
| Large switch/evaluate blocks (>20 cases) | Decision table — may need strategy pattern      |
| Multiple GOTO / ALTER                    | Spaghetti flow — needs careful untangling       |
| Shared mutable state (COMMON, global)    | Tight coupling between modules                  |
| Copy-pasted code blocks                  | Candidates for extraction into shared utilities |
| Dead code (unreachable paragraphs)       | Document but don't migrate                      |
| Magic numbers / hardcoded literals       | Business rules needing extraction               |

## Copybook/Header Resolution

### COBOL Copybook Resolution Strategy

1. **Locate COPY statements**: `COPY member-name` (with optional `OF/IN library`)
2. **Search paths** (in order):
   - Same directory as the program
   - `COPYLIB/` or `copylib/` subdirectory
   - `copybooks/` subdirectory
   - Any directory containing `.cpy` files
   - User-specified `--include-path` locations
3. **Resolve nested copies**: Copybooks can COPY other copybooks — follow the chain
4. **Build composite structure**: Expand all COPYs inline to see the full WORKING-STORAGE/LINKAGE layout
5. **Track sharing**: Map which programs share which copybooks — these form coupling clusters

### C/C++ Include Resolution Strategy

1. **Local includes only**: `#include "file.h"` (skip system `<>` includes)
2. **Search paths** (in order):
   - Directory of the including file
   - Project `include/` or `inc/` directory
   - User-specified `--include-path` locations
3. **Follow chains**: Headers include other headers — build the full tree
4. **Identify shared types**: Structs/classes defined in widely-included headers are shared data contracts

### Impact Analysis

When a copybook/header changes:

- Count of programs affected = change impact radius
- High impact (>10 programs) = needs careful migration sequencing
- Shared structures often define the "API contract" between modules

## External Interface Categories

| Type          | What to Document                           |
| ------------- | ------------------------------------------ |
| File I/O      | Format, encoding, record layout, frequency |
| Database      | Tables, queries, transaction boundaries    |
| Message Queue | Queue names, message format, sync/async    |
| API/Service   | Endpoint, protocol, auth, payload          |
| Screen/UI     | Fields, validation rules, navigation flow  |
| Batch Job     | Schedule, dependencies, input/output       |
| Print/Report  | Layout, data sources, distribution         |
