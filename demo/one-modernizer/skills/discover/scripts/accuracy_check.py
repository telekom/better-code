#!/usr/bin/env python3
"""Spot-check accuracy of .migration/ docs against actual source code.

Usage: python3 accuracy_check.py [project-root] [--samples N]

For large repos (2M+ LOC), this script:
1. Reads module docs from .migration/modules/
2. Extracts claims (file references, function names, class names, dependencies)
3. Verifies each claim exists in the actual source
4. Reports accuracy score and specific hallucinations

This is critical for catching LLM hallucinations in documentation.
"""

import re
import sys
from pathlib import Path
from collections import defaultdict

sys.path.insert(0, str(Path(__file__).parent))
from _constants import IGNORE_DIRS, SOURCE_EXTENSIONS

DEFAULT_SAMPLES = 50


_KNOWN_TECHNOLOGY_NAMES = frozenset(
    {
        "OCI",
        "JDBC",
        "JMS",
        "JMX",
        "JNDI",
        "JPA",
        "JTA",
        "SOAP",
        "REST",
        "HTTP",
        "HTTPS",
        "TCP",
        "UDP",
        "SSH",
        "FTP",
        "SFTP",
        "SMTP",
        "LDAP",
        "SSL",
        "TLS",
        "XML",
        "JSON",
        "YAML",
        "CSV",
        "HTML",
        "CSS",
        "Spring",
        "Hibernate",
        "Struts",
        "Maven",
        "Gradle",
        "Ant",
        "Log4j",
        "SLF4J",
        "JUnit",
        "Mockito",
        "Tomcat",
        "WebSphere",
        "WebLogic",
        "JBoss",
        "Kafka",
        "RabbitMQ",
        "ActiveMQ",
        "Oracle",
        "MySQL",
        "PostgreSQL",
        "DB2",
        "MSSQL",
        "MongoDB",
        "Redis",
        "Memcached",
        "Elasticsearch",
        "Solr",
        "Docker",
        "Kubernetes",
        "Jenkins",
        "Git",
        "SVN",
        "Linux",
        "Windows",
        "AIX",
        "Solaris",
        "CICS",
        "IMS",
        "MQ",
        "Apache",
        "Nginx",
        "IBM",
        "SAP",
        "Telekom",
        "Java",
        "Python",
        "COBOL",
        "Fortran",
        "JavaScript",
        "TypeScript",
        "curl",
        "wget",
        "grep",
        "awk",
        "sed",
        "bash",
        "sh",
        "cron",
    }
)

_KNOWN_VERSION_PATTERN = re.compile(r"^[Vv]\d+(\.\d+)*$")


def _is_glob_pattern(path: str) -> bool:
    return "*" in path or "?" in path or "[" in path


def _is_technology_or_noise(value: str) -> bool:
    if value in _KNOWN_TECHNOLOGY_NAMES:
        return True
    if _KNOWN_VERSION_PATTERN.match(value):
        return True
    if len(value) <= 2:
        return True
    # Common words that appear in docs but aren't symbols
    if value.lower() in (
        "appear",
        "should",
        "could",
        "would",
        "might",
        "true",
        "false",
        "none",
        "null",
        "void",
        "the",
        "this",
        "that",
        "with",
        "from",
        "unclear",
        "unknown",
        "legacy",
        "deprecated",
        "custom",
        "various",
        "multiple",
        "several",
    ):
        return True
    return False


def extract_claims(doc_path: Path) -> list[dict]:
    """Extract verifiable claims from a module doc."""
    content = doc_path.read_text(encoding="utf-8", errors="ignore")
    claims = []

    # File path claims (e.g., `src/Controllers/UserController.cs`)
    for match in re.finditer(r"`([^`]*(?:/|\\)[^`]*\.\w+)`", content):
        value = match.group(1)
        # Skip glob patterns and line-number suffixed refs
        if _is_glob_pattern(value):
            continue
        # Strip :line-number suffix for verification
        clean = re.sub(r":\d+(-\d+)?$", "", value)
        claims.append(
            {
                "type": "file_exists",
                "value": clean,
                "line": content[: match.start()].count("\n") + 1,
            }
        )

    # Class/struct claims (e.g., "class UserService", "struct Config")
    for match in re.finditer(
        r"`(\w+(?:Controller|Service|Repository|Manager|Handler|Factory|Model|Entity|Dto))`",
        content,
    ):
        value = match.group(1)
        if _is_technology_or_noise(value):
            continue
        claims.append(
            {
                "type": "symbol_exists",
                "value": value,
                "line": content[: match.start()].count("\n") + 1,
            }
        )

    # Method/function claims
    for match in re.finditer(r"`(\w+)\(`", content):
        name = match.group(1)
        if len(name) > 2 and name[0].isupper() and not _is_technology_or_noise(name):
            claims.append(
                {
                    "type": "symbol_exists",
                    "value": name,
                    "line": content[: match.start()].count("\n") + 1,
                }
            )

    # Dependency claims (e.g., "depends on ModuleX", "calls ServiceY")
    for match in re.finditer(
        r"(?:depends on|calls|imports|references|uses)\s+`?(\w+)`?",
        content,
        re.IGNORECASE,
    ):
        value = match.group(1)
        if _is_technology_or_noise(value):
            continue
        claims.append(
            {
                "type": "symbol_exists",
                "value": value,
                "line": content[: match.start()].count("\n") + 1,
            }
        )

    return claims


def build_path_indexes(
    all_paths: set[str],
) -> tuple[dict[str, set[str]], set[str]]:
    """Build filename->paths and lowercase path indexes for O(1) lookups."""
    by_filename: dict[str, set[str]] = defaultdict(set)
    all_lower: set[str] = set()
    for p in all_paths:
        p_lower = p.lower()
        all_lower.add(p_lower)
        filename = p.rsplit("/", 1)[-1].lower()
        by_filename[filename].add(p_lower)
    return by_filename, all_lower


def verify_file_exists_fast(
    file_path: str,
    all_paths: set[str],
    by_filename: dict[str, set[str]],
    all_lower: set[str],
) -> bool:
    """Check file existence against pre-built path indexes (O(1) average, no disk I/O).

    Handles exact matches, suffix matches, and filename+directory-hint matches
    entirely in memory. Use this first; fall back to verify_file_exists for edge cases.
    """
    cleaned = file_path.strip().replace("\\", "/")
    cleaned = re.sub(r":\d+(-\d+)?$", "", cleaned)
    cleaned = re.sub(r"\s*\(.*\)\s*$", "", cleaned)
    cleaned = cleaned.strip("`\"' ")
    if not cleaned:
        return False
    # Exact match
    if cleaned in all_paths:
        return True
    cleaned_lower = cleaned.lower()
    if cleaned_lower in all_lower:
        return True
    # Lookup by filename using the index
    parts = cleaned.split("/")
    filename_lower = parts[-1].lower()
    dir_hint = parts[0].lower() if len(parts) > 1 else None
    candidates = by_filename.get(filename_lower)
    if not candidates:
        return False
    for p_lower in candidates:
        # Suffix match: the claimed path appears at the end of the real path
        if p_lower.endswith(cleaned_lower):
            return True
        # Directory hint match: first claimed path component appears in the real path
        if dir_hint and dir_hint in p_lower:
            return True
    return False


def verify_file_exists(root: Path, file_path: str) -> bool:
    """Check if a claimed file exists in the project.

    Handles: exact paths, partial/abbreviated paths (module/File.java when real
    path is src/module/com/pkg/File.java), and case-insensitive matching.
    """
    cleaned = file_path.strip().replace("\\", "/")
    # Strip line-number suffixes (file.java:42, file.java:10-20)
    cleaned = re.sub(r":\d+(-\d+)?$", "", cleaned)
    # Strip markdown formatting artifacts and parenthetical notes
    cleaned = re.sub(r"\s*\(.*\)\s*$", "", cleaned)
    cleaned = cleaned.strip("`\"' ")
    if not cleaned:
        return False
    # Try exact match
    if (root / cleaned).exists():
        return True
    # Extract filename and directory hint for fuzzy matching
    parts = cleaned.split("/")
    filename = parts[-1]
    dir_hint = parts[0] if len(parts) > 1 else None
    # Find the file by name, then verify directory context matches
    _filename_lower = filename.lower()  # noqa: F841
    for f in root.rglob(filename):
        if not f.is_file():
            continue
        rel = str(f.relative_to(root))
        # Exact suffix match (the claimed partial path appears at the end)
        if rel.replace("\\", "/").lower().endswith(cleaned.lower()):
            return True
        # Directory hint match (the first path component appears somewhere in real path)
        if dir_hint and dir_hint.lower() in rel.lower():
            return True
    return False


def verify_symbol_exists(root: Path, symbol: str, file_index: dict) -> bool:
    """Check if a claimed symbol exists anywhere in source files or file names."""
    if symbol in file_index:
        return True
    # Check if symbol appears in any file path (e.g., DialogManager in .../DialogManager.java)
    symbol_lower = symbol.lower()
    for fpath in file_index:
        if symbol_lower in fpath.lower():
            return True
    # Word-boundary search in file contents
    pattern = re.compile(r"\b" + re.escape(symbol) + r"\b")
    for content in file_index.values():
        if pattern.search(content):
            return True
    return False


def _scan_source_files(
    root: Path, max_content_files: int = 10000
) -> tuple[set[str], dict[str, str]]:
    """Single rglob scan that builds both the path index and content index.

    Returns (all_paths, file_index) where:
    - all_paths: set of all relative source file paths (lightweight, ALL files)
    - file_index: dict of path->content for up to max_content_files (memory-bounded)
    """
    candidates = []
    all_paths: set[str] = set()
    for f in root.rglob("*"):
        if any(part in IGNORE_DIRS for part in f.parts):
            continue
        if f.is_file() and f.suffix.lower() in SOURCE_EXTENSIONS:
            rel = str(f.relative_to(root)).replace("\\", "/")
            all_paths.add(rel)
            try:
                size = f.stat().st_size
                candidates.append((f, rel, size))
            except OSError:
                pass

    # Sort by size ascending — index more files within memory budget
    candidates.sort(key=lambda x: x[2])

    index: dict[str, str] = {}
    total_bytes = 0
    max_bytes = 200_000_000  # 200MB memory cap
    count = 0
    for f, rel, size in candidates:
        if count >= max_content_files or total_bytes + size > max_bytes:
            break
        try:
            index[rel] = f.read_text(encoding="utf-8", errors="ignore")
            total_bytes += size
            count += 1
        except (OSError, UnicodeDecodeError):
            pass

    return all_paths, index


def main():
    root = Path(sys.argv[1] if len(sys.argv) > 1 else ".").resolve()
    max_samples = DEFAULT_SAMPLES
    if "--samples" in sys.argv:
        idx = sys.argv.index("--samples")
        max_samples = int(sys.argv[idx + 1])

    migration_dir = root / ".migration" / "discovery"
    modules_dir = migration_dir / "modules"

    if not migration_dir.exists():
        print("ERROR: .migration/ directory not found.")
        sys.exit(1)

    # Collect all module docs
    doc_files = (
        list(migration_dir.glob("*.md")) + list(modules_dir.glob("*.md"))
        if modules_dir.exists()
        else list(migration_dir.glob("*.md"))
    )

    if not doc_files:
        print("ERROR: No documentation files found in .migration/")
        sys.exit(1)

    # Extract claims from all docs
    all_claims = []
    for doc in doc_files:
        claims = extract_claims(doc)
        for c in claims:
            c["source_doc"] = doc.name
        all_claims.extend(claims)

    if not all_claims:
        print("WARNING: No verifiable claims found in documentation.")
        print(
            "This might mean the docs are too abstract — they should reference specific files and symbols."
        )
        sys.exit(0)

    # Sample if too many
    import random

    if len(all_claims) > max_samples:
        random.seed(42)
        sampled = random.sample(all_claims, max_samples)
    else:
        sampled = all_claims

    # Single scan of the repo — partition into path-index and content-index
    print("Scanning source files...", file=sys.stderr)
    all_paths, file_index = _scan_source_files(root)
    by_filename, all_lower = build_path_indexes(all_paths)
    print(f"  Path index: {len(all_paths)} files.", file=sys.stderr)
    print(f"  Content index: {len(file_index)} files.", file=sys.stderr)

    # Verify each claim
    verified = 0
    failed = []
    for claim in sampled:
        if claim["type"] == "file_exists":
            ok = verify_file_exists_fast(
                claim["value"], all_paths, by_filename, all_lower
            ) or verify_file_exists(root, claim["value"])
        elif claim["type"] == "symbol_exists":
            ok = verify_symbol_exists(root, claim["value"], file_index)
        else:
            ok = True

        if ok:
            verified += 1
        else:
            failed.append(claim)

    total = len(sampled)
    accuracy = (verified / total * 100) if total else 0

    # Output report
    print("# Accuracy Report")
    print("")
    print(f"**Project**: {root.name}")
    print(f"**Claims checked**: {total} (of {len(all_claims)} total)")
    print(f"**Verified**: {verified}")
    print(f"**Failed**: {len(failed)}")
    print(f"**Accuracy**: {accuracy:.1f}%")
    print("")

    if failed:
        print("## Failed Claims (potential hallucinations)")
        print("")
        by_doc = defaultdict(list)
        for f in failed:
            by_doc[f["source_doc"]].append(f)

        for doc_name, claims in sorted(by_doc.items()):
            print(f"### {doc_name}")
            for c in claims:
                print(f"  - [{c['type']}] `{c['value']}` (line {c['line']})")
            print()

    print("## Verdict")
    if accuracy >= 95:
        print(f"✓ High accuracy ({accuracy:.0f}%) — documentation is reliable")
    elif accuracy >= 80:
        print(f"⚠️  Moderate accuracy ({accuracy:.0f}%) — review failed claims above")
    else:
        print(
            f"✗ Low accuracy ({accuracy:.0f}%) — documentation contains significant errors, re-run discovery"
        )

    sys.exit(0 if accuracy >= 80 else 1)


if __name__ == "__main__":
    main()
