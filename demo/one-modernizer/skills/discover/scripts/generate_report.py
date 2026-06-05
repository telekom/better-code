#!/usr/bin/env python3
"""Generate an interactive HTML report from .migration/ docs.

Usage: python3 generate_report.py [project-root]

Produces .migration/report.html — a single-file interactive dashboard showing:
- System overview with stats
- Module dependency graph (interactive, clickable)
- Module cards with expandable details
- Unknowns/risks highlighted
- Search across all documentation

Also produces .migration/index.json — machine-readable summary for LLM consumption.
"""

import json
import re
import sys
from pathlib import Path
from html import escape


def parse_module_doc(path: Path) -> dict:
    content = path.read_text(encoding="utf-8", errors="ignore")
    lines = content.split("\n")

    module = {
        "name": path.stem,
        "file": path.name,
        "purpose": "",
        "complexity": "unknown",
        "dependencies": [],
        "source_files": [],
        "interfaces": [],
        "business_rules": [],
        "unknowns": [],
    }

    current_section = ""
    for line in lines:
        if line.startswith("# "):
            module["name"] = line[2:].strip()
        elif line.startswith("## "):
            current_section = line[2:].strip().lower()
        elif current_section == "purpose" and line.strip():
            module["purpose"] += line.strip() + " "
        elif current_section == "complexity assessment" and "rating" in line.lower():
            for level in ("simple", "moderate", "complex"):
                if level in line.lower():
                    module["complexity"] = level
                    break
        elif current_section.startswith("calls") or current_section.startswith(
            "dependencies"
        ):
            match = re.match(r"[-*]\s+`?(\w+)`?", line)
            if match:
                module["dependencies"].append(match.group(1))
        elif (
            current_section == "source files"
            and "|" in line
            and not line.startswith("|--")
        ):
            parts = [p.strip() for p in line.split("|") if p.strip()]
            if parts and not parts[0].startswith("File") and "---" not in parts[0]:
                module["source_files"].append(parts[0])
        elif current_section == "unknowns" and line.strip().startswith("-"):
            module["unknowns"].append(line.strip("- ").strip())

    module["purpose"] = module["purpose"].strip()
    return module


def parse_overview(path: Path) -> dict:
    if not path.exists():
        return {}
    content = path.read_text(encoding="utf-8", errors="ignore")
    return {
        "raw": content,
        "has_content": len(content) > 100,
    }


def build_index(migration_dir: Path) -> dict:
    """Build machine-readable index.json for LLM consumption."""
    modules_dir = migration_dir / "modules"
    modules = []
    if modules_dir.exists():
        for f in sorted(modules_dir.glob("*.md")):
            modules.append(parse_module_doc(f))

    overview = parse_overview(migration_dir / "overview.md")
    unknowns_path = migration_dir / "unknowns.md"
    unknowns_content = (
        unknowns_path.read_text(encoding="utf-8", errors="ignore")
        if unknowns_path.exists()
        else ""
    )

    graph_stats = {}
    graph_path = migration_dir / "graphify-out" / "graph.json"
    if graph_path.exists():
        try:
            data = json.loads(graph_path.read_text(encoding="utf-8"))
            graph_stats = {
                "nodes": len(data.get("nodes", [])),
                "edges": len(data.get("links", data.get("edges", []))),
            }
        except (json.JSONDecodeError, KeyError):
            pass

    return {
        "modules": modules,
        "graph": graph_stats,
        "has_overview": overview.get("has_content", False),
        "has_unknowns": len(unknowns_content) > 50,
        "module_count": len(modules),
        "total_dependencies": sum(len(m["dependencies"]) for m in modules),
        "total_unknowns": sum(len(m["unknowns"]) for m in modules),
        "complexity_breakdown": {
            "simple": sum(1 for m in modules if m["complexity"] == "simple"),
            "moderate": sum(1 for m in modules if m["complexity"] == "moderate"),
            "complex": sum(1 for m in modules if m["complexity"] == "complex"),
            "unknown": sum(1 for m in modules if m["complexity"] == "unknown"),
        },
    }


def generate_html(migration_dir: Path, index: dict) -> str:
    modules = index["modules"]
    graph_stats = index.get("graph", {})
    overview_path = migration_dir / "overview.md"
    overview_content = (
        overview_path.read_text(encoding="utf-8", errors="ignore")
        if overview_path.exists()
        else "No overview generated yet."
    )

    module_cards = ""
    for m in modules:
        deps_html = "".join(
            f'<span class="tag dep">{escape(d)}</span>' for d in m["dependencies"]
        )
        unknowns_html = "".join(f"<li>{escape(u)}</li>" for u in m["unknowns"])
        complexity_class = m["complexity"]
        files_html = "".join(
            f"<li><code>{escape(f)}</code></li>" for f in m["source_files"][:10]
        )

        module_cards += f'''
        <div class="module-card" data-name="{escape(m["name"].lower())}">
          <div class="module-header">
            <h3>{escape(m["name"])}</h3>
            <span class="complexity {complexity_class}">{m["complexity"]}</span>
          </div>
          <p class="purpose">{escape(m["purpose"][:200])}</p>
          <details>
            <summary>Source Files ({len(m["source_files"])})</summary>
            <ul class="file-list">{files_html}</ul>
          </details>
          {'<details><summary>Dependencies</summary><div class="tags">' + deps_html + "</div></details>" if deps_html else ""}
          {"<details><summary>Unknowns (" + str(len(m["unknowns"])) + ')</summary><ul class="unknowns">' + unknowns_html + "</ul></details>" if unknowns_html else ""}
        </div>'''

    # Dependency graph data for vis
    nodes_js = json.dumps(
        [{"id": m["name"], "complexity": m["complexity"]} for m in modules]
    )
    edges_js = []
    for m in modules:
        for dep in m["dependencies"]:
            if any(m2["name"] == dep for m2 in modules):
                edges_js.append({"from": m["name"], "to": dep})
    edges_json = json.dumps(edges_js)

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Migration Discovery Report</title>
<style>
:root {{ --bg: #0f1117; --surface: #1a1d27; --border: #2d3040; --text: #e4e4e7; --muted: #8b8d97; --accent: #6366f1; --success: #22c55e; --warning: #eab308; --danger: #ef4444; }}
* {{ box-sizing: border-box; margin: 0; padding: 0; }}
body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; background: var(--bg); color: var(--text); line-height: 1.6; }}
.container {{ max-width: 1200px; margin: 0 auto; padding: 24px; }}
header {{ padding: 32px 0; border-bottom: 1px solid var(--border); margin-bottom: 32px; }}
h1 {{ font-size: 28px; font-weight: 700; margin-bottom: 8px; }}
.subtitle {{ color: var(--muted); font-size: 14px; }}
.stats {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 16px; margin: 24px 0; }}
.stat {{ background: var(--surface); border: 1px solid var(--border); border-radius: 12px; padding: 20px; text-align: center; }}
.stat-value {{ font-size: 32px; font-weight: 700; color: var(--accent); }}
.stat-label {{ font-size: 12px; color: var(--muted); text-transform: uppercase; letter-spacing: 0.5px; margin-top: 4px; }}
.search {{ width: 100%; padding: 12px 16px; background: var(--surface); border: 1px solid var(--border); border-radius: 8px; color: var(--text); font-size: 14px; margin-bottom: 24px; }}
.search:focus {{ outline: none; border-color: var(--accent); }}
.tabs {{ display: flex; gap: 4px; margin-bottom: 24px; border-bottom: 1px solid var(--border); padding-bottom: 0; }}
.tab {{ padding: 10px 20px; cursor: pointer; color: var(--muted); border-bottom: 2px solid transparent; transition: all 0.2s; }}
.tab:hover {{ color: var(--text); }}
.tab.active {{ color: var(--accent); border-bottom-color: var(--accent); }}
.tab-content {{ display: none; }}
.tab-content.active {{ display: block; }}
.modules-grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(350px, 1fr)); gap: 16px; }}
.module-card {{ background: var(--surface); border: 1px solid var(--border); border-radius: 12px; padding: 20px; transition: border-color 0.2s; }}
.module-card:hover {{ border-color: var(--accent); }}
.module-header {{ display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px; }}
.module-header h3 {{ font-size: 16px; }}
.complexity {{ font-size: 11px; padding: 3px 8px; border-radius: 12px; text-transform: uppercase; font-weight: 600; }}
.complexity.simple {{ background: #052e16; color: var(--success); }}
.complexity.moderate {{ background: #422006; color: var(--warning); }}
.complexity.complex {{ background: #450a0a; color: var(--danger); }}
.complexity.unknown {{ background: #1e1e2e; color: var(--muted); }}
.purpose {{ color: var(--muted); font-size: 13px; margin-bottom: 12px; }}
details {{ margin-top: 8px; }}
summary {{ cursor: pointer; font-size: 13px; color: var(--muted); padding: 4px 0; }}
summary:hover {{ color: var(--text); }}
.tags {{ display: flex; flex-wrap: wrap; gap: 6px; margin-top: 8px; }}
.tag {{ font-size: 11px; padding: 2px 8px; border-radius: 4px; background: #1e1b4b; color: #a5b4fc; }}
.file-list, .unknowns {{ margin-top: 8px; padding-left: 16px; font-size: 13px; }}
.file-list li, .unknowns li {{ margin: 4px 0; color: var(--muted); }}
.unknowns li {{ color: var(--warning); }}
.graph-container {{ background: var(--surface); border: 1px solid var(--border); border-radius: 12px; padding: 24px; min-height: 400px; position: relative; }}
.graph-placeholder {{ color: var(--muted); text-align: center; padding: 80px 20px; }}
canvas {{ width: 100%; height: 400px; }}
.overview-content {{ background: var(--surface); border: 1px solid var(--border); border-radius: 12px; padding: 24px; white-space: pre-wrap; font-size: 14px; color: var(--muted); }}
</style>
</head>
<body>
<div class="container">
  <header>
    <h1>Migration Discovery Report</h1>
    <p class="subtitle">Generated by one-modernizer</p>
  </header>

  <div class="stats">
    <div class="stat"><div class="stat-value">{index["module_count"]}</div><div class="stat-label">Modules</div></div>
    <div class="stat"><div class="stat-value">{graph_stats.get("nodes", 0)}</div><div class="stat-label">Graph Nodes</div></div>
    <div class="stat"><div class="stat-value">{graph_stats.get("edges", 0)}</div><div class="stat-label">Relationships</div></div>
    <div class="stat"><div class="stat-value">{index["total_unknowns"]}</div><div class="stat-label">Unknowns</div></div>
    <div class="stat"><div class="stat-value">{index["complexity_breakdown"].get("complex", 0)}</div><div class="stat-label">Complex Modules</div></div>
  </div>

  <input type="text" class="search" placeholder="Search modules..." oninput="filterModules(this.value)">

  <div class="tabs">
    <div class="tab active" onclick="switchTab('modules')">Modules</div>
    <div class="tab" onclick="switchTab('graph')">Dependency Graph</div>
    <div class="tab" onclick="switchTab('overview')">Overview</div>
  </div>

  <div id="tab-modules" class="tab-content active">
    <div class="modules-grid">{module_cards}</div>
  </div>

  <div id="tab-graph" class="tab-content">
    <div class="graph-container">
      <canvas id="graph-canvas"></canvas>
    </div>
  </div>

  <div id="tab-overview" class="tab-content">
    <div class="overview-content">{escape(overview_content)}</div>
  </div>
</div>

<script>
const nodes = {nodes_js};
const edges = {edges_json};

function switchTab(name) {{
  document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
  document.querySelectorAll('.tab-content').forEach(t => t.classList.remove('active'));
  document.querySelector(`#tab-${{name}}`).classList.add('active');
  event.target.classList.add('active');
  if (name === 'graph') drawGraph();
}}

function filterModules(query) {{
  const q = query.toLowerCase();
  document.querySelectorAll('.module-card').forEach(card => {{
    card.style.display = card.dataset.name.includes(q) ? '' : 'none';
  }});
}}

function drawGraph() {{
  const canvas = document.getElementById('graph-canvas');
  const ctx = canvas.getContext('2d');
  canvas.width = canvas.offsetWidth * 2;
  canvas.height = 800;
  ctx.scale(2, 2);
  const w = canvas.offsetWidth, h = 400;

  const positions = {{}};
  const colors = {{ simple: '#22c55e', moderate: '#eab308', complex: '#ef4444', unknown: '#6b7280' }};
  nodes.forEach((n, i) => {{
    const angle = (2 * Math.PI * i) / nodes.length;
    const r = Math.min(w, h) * 0.35;
    positions[n.id] = {{ x: w/2 + r * Math.cos(angle), y: h/2 + r * Math.sin(angle) }};
  }});

  // Draw edges
  ctx.strokeStyle = '#2d3040';
  ctx.lineWidth = 1;
  edges.forEach(e => {{
    const from = positions[e.from], to = positions[e.to];
    if (from && to) {{
      ctx.beginPath();
      ctx.moveTo(from.x, from.y);
      ctx.lineTo(to.x, to.y);
      ctx.stroke();
      const angle = Math.atan2(to.y - from.y, to.x - from.x);
      const ax = to.x - 20 * Math.cos(angle), ay = to.y - 20 * Math.sin(angle);
      ctx.beginPath();
      ctx.moveTo(ax, ay);
      ctx.lineTo(ax - 8*Math.cos(angle-0.4), ay - 8*Math.sin(angle-0.4));
      ctx.lineTo(ax - 8*Math.cos(angle+0.4), ay - 8*Math.sin(angle+0.4));
      ctx.fillStyle = '#2d3040';
      ctx.fill();
    }}
  }});

  // Draw nodes
  nodes.forEach(n => {{
    const p = positions[n.id];
    ctx.beginPath();
    ctx.arc(p.x, p.y, 12, 0, 2 * Math.PI);
    ctx.fillStyle = colors[n.complexity] || colors.unknown;
    ctx.fill();
    ctx.font = '11px -apple-system, sans-serif';
    ctx.fillStyle = '#e4e4e7';
    ctx.textAlign = 'center';
    ctx.fillText(n.id, p.x, p.y + 24);
  }});
}}
</script>
</body>
</html>"""


def main():
    root = Path(sys.argv[1] if len(sys.argv) > 1 else ".").resolve()
    migration_dir = root / ".migration" / "discovery"

    if not migration_dir.exists():
        print("ERROR: .migration/ directory not found.", file=sys.stderr)
        sys.exit(1)

    index = build_index(migration_dir)

    # Write machine-readable index for LLM
    index_path = migration_dir / "index.json"
    index_path.write_text(json.dumps(index, indent=2), encoding="utf-8")
    print(f"  index.json  ->  {index_path}")

    # Write HTML report for humans
    html = generate_html(migration_dir, index)
    report_path = migration_dir / "report.html"
    report_path.write_text(html, encoding="utf-8")
    print(f"  report.html ->  {report_path}")

    # Try to open in browser
    import webbrowser

    try:
        webbrowser.open(f"file://{report_path}")
        print("  Opened in browser")
    except Exception:
        print(f"  Open {report_path} in a browser to view")


if __name__ == "__main__":
    main()
