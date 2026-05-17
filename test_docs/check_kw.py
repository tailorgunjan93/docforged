import zipfile, json, sys

path = sys.argv[1] if len(sys.argv) > 1 else "test_docs/resume.udf"
with zipfile.ZipFile(path) as zf:
    cat = json.loads(zf.read("catalogue.json"))
    print(f"Keywords per section (fast mode = no LLM = no keywords):")
    for s in cat["section_index"]:
        kw = s.get("keywords") or []
        print(f"  {s['id']:6s}  {s['title']:45s}  kw={kw}")
