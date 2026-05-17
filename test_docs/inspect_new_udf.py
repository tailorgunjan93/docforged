import zipfile, json, sys

path = "test_docs/GunjanTailor_new.udf"
with zipfile.ZipFile(path) as zf:
    mf = json.loads(zf.read("manifest.json"))
    cat = json.loads(zf.read("catalogue.json"))
    content = json.loads(zf.read("content.json"))

print("=== MANIFEST ===")
print(json.dumps(mf, indent=2))

print("\n=== SECTION INDEX (catalogue) ===")
for s in cat["section_index"]:
    print(f"  {s['id']:6s}  lv={s['level']}  parent={str(s.get('parent_id','?')):6s}  children={s.get('children',[])}  title={s['title']}")
    kw = s.get("keywords") or []
    if kw: print(f"          kw={kw}")

print("\n=== CONTENT SECTIONS ===")
for sid, sec in content["sections"].items():
    text = (sec.get("text") or "").strip()[:200].replace("\n", " | ")
    print(f"  {sid:6s}  lv={sec['level']}  '{sec['title']}'")
    if text: print(f"          text: {text}...")
