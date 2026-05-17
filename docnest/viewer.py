"""
DocNest HTML Viewer — generates a self-contained human-readable HTML page
from a .udf archive.

The output is a single .html file with:
  - Left sidebar: collapsible section tree (same §id index the AI uses)
  - Right panel: full document content, section by section
  - Tables rendered as proper HTML tables
  - Active-section tracking as you scroll
  - Zero external dependencies — works offline

Usage::

    from docnest.viewer import generate_html
    html_path = generate_html("report.udf")          # → report.html
    html_path = generate_html("report.udf", "out.html")

    # Or from CLI:
    docnest view report.udf
"""

from __future__ import annotations

import html as _html
import json
import zipfile
from pathlib import Path


# ------------------------------------------------------------------ #
#  Public API                                                          #
# ------------------------------------------------------------------ #

def generate_html(udf_path: str, output_path: str | None = None) -> str:
    """Generate a self-contained HTML viewer for a .udf file.

    Args:
        udf_path: Path to the .udf archive.
        output_path: Where to write the HTML. Defaults to same name as .udf.

    Returns:
        Absolute path to the generated HTML file.
    """
    path = Path(udf_path)
    if not path.exists():
        raise FileNotFoundError(f"File not found: {udf_path}")

    with zipfile.ZipFile(str(path), "r") as zf:
        manifest  = json.loads(zf.read("manifest.json"))
        catalogue = json.loads(zf.read("catalogue.json"))
        content   = json.loads(zf.read("content.json"))

    out = Path(output_path) if output_path else path.with_suffix(".html")
    html_str = _render(manifest, catalogue, content, path.name)
    out.write_text(html_str, encoding="utf-8")
    return str(out.resolve())


# ------------------------------------------------------------------ #
#  Renderer                                                            #
# ------------------------------------------------------------------ #

def _e(text: str) -> str:
    """HTML-escape a string."""
    return _html.escape(str(text), quote=True)


def _render_table(table: dict) -> str:
    """Render a table dict as an HTML <table>."""
    rows_html = ""
    headers = table.get("headers") or []
    rows = table.get("rows") or []
    caption = table.get("caption") or table.get("table_id") or ""

    thead = ""
    if headers:
        ths = "".join(f"<th>{_e(h)}</th>" for h in headers)
        thead = f"<thead><tr>{ths}</tr></thead>"

    tbody_rows = ""
    for row in rows:
        tds = "".join(f"<td>{_e(str(c))}</td>" for c in row)
        tbody_rows += f"<tr>{tds}</tr>"
    tbody = f"<tbody>{tbody_rows}</tbody>"

    cap_html = f"<caption>{_e(caption)}</caption>" if caption else ""
    return f'<div class="table-wrap"><table>{cap_html}{thead}{tbody}</table></div>'


def _render_section_content(sec: dict) -> str:
    """Render the body of a section: text + tables."""
    parts = []
    text = (sec.get("text") or "").strip()
    if text:
        # Preserve line breaks
        escaped = _e(text).replace("\n", "<br>")
        parts.append(f'<p class="sec-text">{escaped}</p>')

    for table in sec.get("tables") or []:
        parts.append(_render_table(table))

    return "\n".join(parts)


def _build_sidebar(section_index: list[dict]) -> str:
    """Build the collapsible sidebar TOC."""
    items = []
    for entry in section_index:
        sid   = entry.get("id", "")
        title = entry.get("title", "")
        level = entry.get("level", 1)
        indent = (level - 1) * 14
        items.append(
            f'<a class="toc-item toc-l{level}" '
            f'href="#{_e(sid)}" '
            f'style="padding-left:{indent + 12}px" '
            f'onclick="setActive(this)" '
            f'data-id="{_e(sid)}">'
            f'<span class="toc-id">{_e(sid)}</span>'
            f'<span class="toc-title">{_e(title)}</span>'
            f'</a>'
        )
    return "\n".join(items)


def _build_doc_body(section_index: list[dict], sections: dict) -> str:
    """Build the main document body — one <section> per §id."""
    parts = []
    for entry in section_index:
        sid   = entry.get("id", "")
        title = entry.get("title", "")
        level = entry.get("level", 1)
        sec_data = sections.get(sid, {})
        h_tag = f"h{min(level + 1, 6)}"   # §1 → h2, §1.1 → h3, etc.

        body_html = _render_section_content(sec_data)

        # Summary badge (if available)
        summary = entry.get("summary") or ""
        summary_html = ""
        if summary:
            summary_html = f'<p class="sec-summary">{_e(summary)}</p>'

        # Keywords
        kws = entry.get("keywords") or []
        kw_html = ""
        if kws:
            badges = "".join(f'<span class="kw-badge">{_e(k)}</span>' for k in kws)
            kw_html = f'<div class="kw-row">{badges}</div>'

        parts.append(
            f'<section id="{_e(sid)}" class="doc-section level-{level}" data-id="{_e(sid)}">'
            f'<{h_tag} class="sec-heading">'
            f'<span class="sec-id">{_e(sid)}</span> {_e(title)}'
            f'</{h_tag}>'
            f'{summary_html}'
            f'{body_html}'
            f'{kw_html}'
            f'</section>'
        )
    return "\n".join(parts)


def _render(manifest: dict, catalogue: dict, content: dict, filename: str) -> str:
    """Render the full HTML page."""
    title      = _e(catalogue.get("title") or manifest.get("title") or "Document")
    doc_summary = _e(catalogue.get("summary") or "")
    owner       = _e(catalogue.get("owner") or "")
    dept        = _e(catalogue.get("department") or "")
    version     = _e(catalogue.get("version") or manifest.get("version") or "")
    tags        = catalogue.get("tags") or []
    emb_model   = _e(manifest.get("embedding_model") or "")
    quant       = _e(manifest.get("quantization") or "")
    created     = _e(manifest.get("created_at", "")[:10])
    section_index = catalogue.get("section_index") or []
    sections      = content.get("sections") or {}

    sidebar_html  = _build_sidebar(section_index)
    body_html     = _build_doc_body(section_index, sections)

    # Insights
    insights = catalogue.get("insights") or []
    insights_html = ""
    if insights:
        items = "".join(f"<li>{_e(i)}</li>" for i in insights)
        insights_html = f'<div class="insights-box"><strong>Key Insights</strong><ul>{items}</ul></div>'

    # Key numbers
    key_numbers = catalogue.get("key_numbers") or []
    kn_html = ""
    if key_numbers:
        rows = "".join(
            f'<tr><td>{_e(k.get("label",""))}</td>'
            f'<td><strong>{_e(k.get("value",""))}</strong> {_e(k.get("unit",""))}</td>'
            f'<td class="dim">{_e(k.get("section",""))}</td></tr>'
            for k in key_numbers
        )
        kn_html = (
            f'<div class="kn-box"><strong>Key Numbers</strong>'
            f'<table><tbody>{rows}</tbody></table></div>'
        )

    # Tags
    tags_html = "".join(f'<span class="tag">{_e(t)}</span>' for t in tags) if tags else ""

    # Meta bar
    meta_parts = []
    if owner:   meta_parts.append(f'<span>👤 {owner}</span>')
    if dept:    meta_parts.append(f'<span>🏢 {dept}</span>')
    if version: meta_parts.append(f'<span>v{version}</span>')
    if created: meta_parts.append(f'<span>📅 {created}</span>')
    if emb_model: meta_parts.append(f'<span title="Embedding model">🧠 {emb_model}</span>')
    if quant:   meta_parts.append(f'<span>⚙ {quant}</span>')
    meta_html = " · ".join(meta_parts)

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title} — DocNest</title>
<style>
  :root {{
    --sidebar-w: 280px;
    --header-h: 56px;
    --bg:       #f8f9fa;
    --sidebar-bg: #ffffff;
    --border:   #e2e8f0;
    --text:     #1a202c;
    --muted:    #718096;
    --accent:   #3b82f6;
    --active-bg:#eff6ff;
    --active-border: #3b82f6;
    --heading-color: #1e40af;
    --kw-bg:    #e0f2fe;
    --kw-color: #0369a1;
    --tag-bg:   #dcfce7;
    --tag-color:#166534;
    --insight-bg:#fefce8;
    --insight-border:#fde047;
    --kn-bg:    #f0fdf4;
    --kn-border:#86efac;
    --table-head:#f1f5f9;
    --table-border:#cbd5e1;
  }}
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
         background: var(--bg); color: var(--text); display: flex; flex-direction: column;
         height: 100vh; overflow: hidden; }}

  /* ── Header ── */
  .header {{ height: var(--header-h); background: var(--sidebar-bg);
            border-bottom: 1px solid var(--border); display: flex;
            align-items: center; padding: 0 20px; gap: 12px;
            flex-shrink: 0; }}
  .header-title {{ font-size: 16px; font-weight: 600; color: var(--text); flex: 1;
                   white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }}
  .header-badge {{ font-size: 11px; padding: 3px 8px; border-radius: 12px;
                  background: #dbeafe; color: #1d4ed8; font-weight: 500; flex-shrink: 0; }}
  .meta-bar {{ font-size: 11px; color: var(--muted); display: flex;
              flex-wrap: wrap; gap: 10px; padding: 6px 20px;
              background: #f1f5f9; border-bottom: 1px solid var(--border);
              flex-shrink: 0; }}

  /* ── Layout ── */
  .layout {{ display: flex; flex: 1; overflow: hidden; }}

  /* ── Sidebar ── */
  .sidebar {{ width: var(--sidebar-w); background: var(--sidebar-bg);
             border-right: 1px solid var(--border); overflow-y: auto;
             flex-shrink: 0; padding: 12px 0; }}
  .sidebar-label {{ font-size: 10px; font-weight: 600; text-transform: uppercase;
                   letter-spacing: .08em; color: var(--muted);
                   padding: 8px 16px 4px; }}
  .toc-item {{ display: flex; gap: 8px; align-items: baseline; text-decoration: none;
              color: var(--muted); font-size: 12px; padding: 5px 12px;
              border-left: 2px solid transparent; transition: all .12s; }}
  .toc-item:hover {{ color: var(--text); background: #f8fafc; }}
  .toc-item.active {{ color: var(--accent); background: var(--active-bg);
                     border-left-color: var(--active-border); font-weight: 500; }}
  .toc-id {{ font-family: monospace; font-size: 10px; color: var(--muted);
            flex-shrink: 0; min-width: 36px; }}
  .toc-title {{ flex: 1; line-height: 1.4; }}
  .toc-l1 .toc-title {{ font-weight: 500; color: var(--text); }}

  /* ── Main content ── */
  .main {{ flex: 1; overflow-y: auto; padding: 32px 48px; max-width: 900px; }}

  .doc-meta-block {{ margin-bottom: 24px; }}
  .doc-title {{ font-size: 26px; font-weight: 700; color: var(--text); margin-bottom: 8px; }}
  .doc-summary {{ font-size: 14px; color: var(--muted); line-height: 1.7; margin-bottom: 12px; }}
  .tags-row {{ display: flex; flex-wrap: wrap; gap: 6px; margin-top: 8px; }}
  .tag {{ font-size: 11px; padding: 2px 8px; border-radius: 12px;
          background: var(--tag-bg); color: var(--tag-color); font-weight: 500; }}

  .insights-box {{ background: var(--insight-bg); border: 1px solid var(--insight-border);
                  border-radius: 8px; padding: 14px 18px; margin-bottom: 20px; }}
  .insights-box strong {{ font-size: 12px; text-transform: uppercase; letter-spacing: .05em;
                          color: #854d0e; display: block; margin-bottom: 8px; }}
  .insights-box ul {{ list-style: none; }}
  .insights-box li {{ font-size: 13px; color: #78350f; padding: 3px 0;
                      padding-left: 16px; position: relative; line-height: 1.5; }}
  .insights-box li::before {{ content: "•"; position: absolute; left: 0; color: #ca8a04; }}

  .kn-box {{ background: var(--kn-bg); border: 1px solid var(--kn-border);
            border-radius: 8px; padding: 14px 18px; margin-bottom: 28px; }}
  .kn-box strong {{ font-size: 12px; text-transform: uppercase; letter-spacing: .05em;
                   color: #166534; display: block; margin-bottom: 10px; }}
  .kn-box table {{ width: 100%; border-collapse: collapse; font-size: 13px; }}
  .kn-box td {{ padding: 4px 8px; color: #14532d; }}
  .kn-box td:first-child {{ color: var(--muted); width: 160px; }}
  .kn-box .dim {{ color: var(--muted); font-size: 11px; font-family: monospace; }}

  /* ── Document sections ── */
  .doc-section {{ margin-bottom: 36px; scroll-margin-top: 20px; }}
  .sec-heading {{ color: var(--heading-color); font-weight: 600; line-height: 1.3;
                 margin-bottom: 8px; display: flex; align-items: baseline; gap: 10px; }}
  .level-1 .sec-heading {{ font-size: 20px; border-bottom: 1px solid var(--border);
                           padding-bottom: 6px; margin-bottom: 12px; }}
  .level-2 .sec-heading {{ font-size: 16px; }}
  .level-3 .sec-heading {{ font-size: 14px; color: #374151; }}
  .level-4 .sec-heading, .level-5 .sec-heading, .level-6 .sec-heading {{
    font-size: 13px; color: #4b5563; }}
  .sec-id {{ font-family: monospace; font-size: 11px; color: var(--muted);
            background: #f1f5f9; border-radius: 4px; padding: 1px 5px;
            flex-shrink: 0; }}
  .sec-summary {{ font-size: 12px; color: var(--muted); font-style: italic;
                 margin-bottom: 10px; line-height: 1.6; border-left: 3px solid var(--border);
                 padding-left: 10px; }}
  .sec-text {{ font-size: 13px; color: #374151; line-height: 1.8; white-space: pre-wrap; }}

  /* ── Tables ── */
  .table-wrap {{ overflow-x: auto; margin: 14px 0; border-radius: 8px;
                border: 1px solid var(--table-border); }}
  table {{ border-collapse: collapse; font-size: 12px; width: 100%; }}
  caption {{ font-size: 11px; color: var(--muted); text-align: left;
            padding: 6px 10px; font-style: italic; }}
  th {{ background: var(--table-head); padding: 8px 12px; text-align: left;
       font-weight: 600; font-size: 11px; text-transform: uppercase;
       letter-spacing: .04em; color: var(--muted);
       border-bottom: 1px solid var(--table-border); }}
  td {{ padding: 7px 12px; border-bottom: 1px solid #f1f5f9; color: #374151; }}
  tr:last-child td {{ border-bottom: none; }}
  tr:hover td {{ background: #f8fafc; }}

  /* ── Keywords ── */
  .kw-row {{ display: flex; flex-wrap: wrap; gap: 4px; margin-top: 10px; }}
  .kw-badge {{ font-size: 10px; padding: 2px 7px; border-radius: 10px;
              background: var(--kw-bg); color: var(--kw-color); }}

  /* ── Scroll sync ── */
  .main::-webkit-scrollbar {{ width: 6px; }}
  .main::-webkit-scrollbar-track {{ background: transparent; }}
  .main::-webkit-scrollbar-thumb {{ background: #cbd5e1; border-radius: 3px; }}

  @media(max-width: 700px) {{
    .sidebar {{ display: none; }}
    .main {{ padding: 20px 16px; max-width: 100%; }}
  }}
</style>
</head>
<body>

<div class="header">
  <span class="header-title">{title}</span>
  <span class="header-badge">UDF 1.0</span>
  <span class="header-badge" style="background:#dcfce7;color:#166534">{len(section_index)} sections</span>
</div>
<div class="meta-bar">{meta_html}</div>

<div class="layout">
  <nav class="sidebar">
    <p class="sidebar-label">Contents</p>
    {sidebar_html}
  </nav>

  <main class="main" id="main-scroll">
    <div class="doc-meta-block">
      <h1 class="doc-title">{title}</h1>
      {f'<p class="doc-summary">{doc_summary}</p>' if doc_summary else ''}
      {f'<div class="tags-row">{tags_html}</div>' if tags_html else ''}
    </div>

    {insights_html}
    {kn_html}

    {body_html}
  </main>
</div>

<script>
// ── Active section tracking ──────────────────────────────────────────
function setActive(el) {{
  document.querySelectorAll('.toc-item').forEach(a => a.classList.remove('active'));
  el.classList.add('active');
}}

// Intersection Observer — highlight sidebar item as sections scroll into view
const observer = new IntersectionObserver(entries => {{
  entries.forEach(entry => {{
    if (entry.isIntersecting) {{
      const id = entry.target.getAttribute('data-id');
      document.querySelectorAll('.toc-item').forEach(a => {{
        a.classList.toggle('active', a.getAttribute('data-id') === id);
      }});
    }}
  }});
}}, {{ rootMargin: '-20% 0px -70% 0px' }});

document.querySelectorAll('.doc-section').forEach(s => observer.observe(s));

// ── Smooth scroll to first section on load ───────────────────────────
window.addEventListener('load', () => {{
  const first = document.querySelector('.toc-item');
  if (first) first.classList.add('active');
}});
</script>
</body>
</html>"""
