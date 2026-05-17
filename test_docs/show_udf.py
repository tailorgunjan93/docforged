import zipfile, json, os, sys

path = sys.argv[1] if len(sys.argv) > 1 else "test_docs/resume.udf"
source_kb = float(sys.argv[2]) if len(sys.argv) > 2 else 0

print("=" * 60)
print(f"  UDF REPORT: {os.path.basename(path)}")
print("=" * 60)

if source_kb:
    print(f"  Source PDF:  {source_kb:.1f} KB")
udf_kb = os.path.getsize(path) / 1024
print(f"  Output .udf: {udf_kb:.1f} KB")
if source_kb:
    print(f"  Size ratio:  {100*udf_kb/source_kb:.0f}% of original PDF")

print()
print("Archive contents:")
with zipfile.ZipFile(path) as zf:
    for i in zf.infolist():
        pct = 100 * (1 - i.compress_size / i.file_size) if i.file_size else 0
        print(f"  {i.filename:22s}  raw={i.file_size:>7,}  zip={i.compress_size:>6,}  -{pct:.0f}%")

    print()
    m = json.loads(zf.read("manifest.json"))
    print("manifest.json:")
    for k, v in m.items():
        print(f"  {k:22s} = {v}")

    print()
    cat = json.loads(zf.read("catalogue.json"))
    si = cat.get("section_index", [])
    print(f"Section tree  ({len(si)} sections):")
    for s in si:
        indent = "  " * (s["level"] - 1)
        kw = "  →  " + ", ".join(s["keywords"][:5]) if s.get("keywords") else ""
        print(f"  {indent}{s['id']:8s}  {s['title']}{kw}")

    print()
    content = json.loads(zf.read("content.json"))
    sections = content.get("sections", {})
    print("Section text preview:")
    for sid, sec in list(sections.items())[:5]:
        text = (sec.get("text") or "").strip()[:120].replace("\n", " ")
        if text:
            print(f"  {sid}: {text}…")
