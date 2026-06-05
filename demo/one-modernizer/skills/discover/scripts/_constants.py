"""Shared constants for discovery scripts."""

IGNORE_DIRS = frozenset(
    {
        ".git",
        "node_modules",
        "__pycache__",
        ".venv",
        "venv",
        "dist",
        "build",
        "bin",
        "obj",
        "target",
        ".migration",
        ".idea",
        ".vs",
        "packages",
        ".nuget",
        "vendor",
        "third_party",
    }
)

SOURCE_EXTENSIONS = frozenset(
    {
        ".cs",
        ".java",
        ".py",
        ".go",
        ".rs",
        ".rb",
        ".kt",
        ".scala",
        ".js",
        ".ts",
        ".tsx",
        ".jsx",
        ".vue",
        ".svelte",
        ".c",
        ".cpp",
        ".cc",
        ".h",
        ".hpp",
        ".cbl",
        ".cob",
        ".cpy",
        ".f",
        ".f90",
        ".f95",
        ".for",
        ".vb",
        ".bas",
        ".cls",
        ".frm",
        ".php",
        ".swift",
        ".lua",
        ".zig",
        ".sql",
        ".plsql",
        ".pls",
        ".pkb",
        ".pks",
        ".trg",
        ".fnc",
        ".prc",
        ".jcl",
        ".proc",
        ".sh",
        ".tcl",
        ".xml",
        ".properties",
        ".yaml",
        ".yml",
    }
)

COBOL_EXTENSIONS = frozenset({".cbl", ".cob", ".cpy"})
C_EXTENSIONS = frozenset({".c", ".h", ".cpp", ".cc", ".cxx", ".hpp"})
ORACLE_EXTENSIONS = frozenset({".sql", ".pls", ".pkb", ".pks", ".trg", ".fnc", ".prc"})
JCL_EXTENSIONS = frozenset({".jcl", ".proc"})
