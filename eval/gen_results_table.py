"""Generate the live_results.md table from Run 4 details.json."""
import json
from pathlib import Path

RESULTS_DIR = Path(__file__).parent / "results"
details = json.loads((RESULTS_DIR / "details.json").read_text(encoding="utf-8"))

rows = []
for doc in details:
    fmt  = doc["fmt"].upper()
    name = doc["name"]
    for q in doc["questions"]:
        score    = q.get("judge_score", "?")
        dn_ms    = round(q.get("docnest_total_ms", 0))
        tr_ms    = round(q.get("trad_total_ms", 0))
        dn_tok   = q.get("docnest_tokens", "?")
        tr_tok   = q.get("trad_tokens", "?")
        question = q["question"][:60].replace("|", "/")
        dn_ans   = (q.get("docnest_answer") or "").replace("\n", " ")[:80].replace("|", "/")
        expected = (q.get("reference") or q.get("truth") or "").replace("\n", " ")[:80].replace("|", "/")
        rows.append(
            f"| {name[:28]} | {fmt} | {question} | {score}/10 "
            f"| {dn_ms} ms | {tr_ms} ms | {dn_tok} | {tr_tok} "
            f"| {dn_ans} | {expected} |"
        )

header = (
    "# DOCNEST Live Results — Run 4\n\n"
    "| File | Fmt | Question | Score | DocNest Time | Trad Time "
    "| DocNest Tokens | Trad Tokens | DocNest Answer | Expected / Baseline |\n"
    "|------|-----|----------|-------|-------------|----------|"
    "----------------|------------|----------------|---------------------|\n"
)

out = header + "\n".join(rows)
(RESULTS_DIR / "live_results.md").write_text(out, encoding="utf-8")

# Also print summary stats per format
from collections import defaultdict
by_fmt = defaultdict(lambda: {"pass": 0, "total": 0, "dn_tok": 0, "tr_tok": 0, "dn_ms": 0})
for doc in details:
    fmt = doc["fmt"].upper()
    for q in doc["questions"]:
        by_fmt[fmt]["total"] += 1
        if q.get("judge_score", 0) >= 7:
            by_fmt[fmt]["pass"] += 1
        by_fmt[fmt]["dn_tok"] += q.get("docnest_tokens", 0)
        by_fmt[fmt]["tr_tok"] += q.get("trad_tokens", 0)
        by_fmt[fmt]["dn_ms"]  += q.get("docnest_total_ms", 0)

print(f"\n{'Format':<8} {'Pass':>6} {'Total':>6} {'Score':>7} {'DN Tok':>8} {'Tr Tok':>8} {'Tok Save%':>10} {'DN ms':>8}")
print("-" * 70)
total_pass = total_q = total_dn_tok = total_tr_tok = 0
for fmt, d in sorted(by_fmt.items()):
    n = d["total"]
    p = d["pass"]
    avg_dn = d["dn_tok"] // n
    avg_tr = d["tr_tok"] // n
    save   = round((1 - avg_dn / avg_tr) * 100) if avg_tr else 0
    avg_ms = round(d["dn_ms"] / n)
    print(f"{fmt:<8} {p:>6} {n:>6} {p/n*10:>7.2f} {avg_dn:>8} {avg_tr:>8} {save:>9}% {avg_ms:>7}ms")
    total_pass += p; total_q += n; total_dn_tok += d["dn_tok"]; total_tr_tok += d["tr_tok"]

print("-" * 70)
avg_dn = total_dn_tok // total_q; avg_tr = total_tr_tok // total_q
save = round((1 - avg_dn / avg_tr) * 100)
print(f"{'ALL':<8} {total_pass:>6} {total_q:>6} {total_pass/total_q*10:>7.2f} {avg_dn:>8} {avg_tr:>8} {save:>9}%")
print(f"\nlive_results.md written → {RESULTS_DIR / 'live_results.md'}")
