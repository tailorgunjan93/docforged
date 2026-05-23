"""
judge_answers.py — Score existing DocNest eval results without re-running.

Reads  : eval/results/answers_for_claude.json  (written by rag_accuracy_eval.py)
Outputs: eval/results/scored_results.md        (per-question score table)

Uses the same _local_judge logic as rag_accuracy_eval.py (keyword+number overlap).
Run from repo root:
    python eval/judge_answers.py
"""

from __future__ import annotations
import json, re
from pathlib import Path

EVAL_DIR    = Path(__file__).parent
RESULTS_DIR = EVAL_DIR / "results"

# ── Stop-words (same set as rag_accuracy_eval.py) ────────────────────────────
_STOP_WORDS = frozenset(
    "what which how the a an is are was were does did do in on at to for of and "
    "or by with from this that these those it its be been being have has had will "
    "would could should may might must shall can cannot dont doesnt report describe "
    "say says said describes according year annual global".split()
)


def _local_judge(question: str, candidate: str, reference: str) -> tuple[int, str]:
    """Keyword+number overlap judge — instant, no API required."""
    cand = candidate.lower().strip()
    ref  = reference.lower().strip()

    # Hard zero: retrieval failure sentinel
    if cand.startswith("not found in context") or cand.startswith("not found in the context"):
        return 0, "retrieval-miss: 'not found in context'"

    def _nums(text: str) -> list[str]:
        return re.findall(r'\b\d[\d\.]*', text.replace(',', ''))

    def _close(a: str, b: str) -> bool:
        try:
            va, vb = float(a), float(b)
            return abs(va - vb) / max(abs(va), 0.001) < 0.06
        except Exception:
            return a == b

    ref_nums   = _nums(ref)
    cand_nums  = _nums(cand)
    num_hits   = sum(1 for rn in ref_nums if any(_close(rn, cn) for cn in cand_nums))
    num_ratio  = num_hits / max(len(ref_nums), 1)

    ref_kws    = {w for w in re.sub(r'[^a-z0-9]', ' ', ref).split()
                  if w not in _STOP_WORDS and len(w) > 2}
    cand_words = set(re.sub(r'[^a-z0-9]', ' ', cand).split())
    kw_ratio   = len(ref_kws & cand_words) / max(len(ref_kws), 1)

    raw_phrases  = re.split(r'[;|:\-–]', ref)
    ref_phrases  = [p.strip() for p in raw_phrases if 4 < len(p.strip()) < 60]
    phrase_hits  = sum(1 for p in ref_phrases if p in cand)
    phrase_ratio = phrase_hits / max(len(ref_phrases), 1)

    if num_ratio >= 0.75 and kw_ratio >= 0.45:
        return 10, f"fast✓ num={num_ratio:.2f} kw={kw_ratio:.2f}"
    if not ref_nums and kw_ratio >= 0.60:
        return 10, f"text✓ kw={kw_ratio:.2f}"
    if not ref_nums and kw_ratio >= 0.40:
        return 9,  f"text~ kw={kw_ratio:.2f}"

    combined = 0.50 * num_ratio + 0.30 * kw_ratio + 0.20 * phrase_ratio
    if   combined >= 0.70: score = 10
    elif combined >= 0.55: score = 9
    elif combined >= 0.40: score = 8
    elif combined >= 0.28: score = 7
    elif combined >= 0.18: score = 6
    elif combined >= 0.10: score = 5
    elif combined >= 0.04: score = 3
    else:                  score = 0

    return score, f"num={num_ratio:.2f} kw={kw_ratio:.2f} phrase={phrase_ratio:.2f}"


def main() -> None:
    # Try v6_p2 first, then fall back to root results dir
    candidates = [
        RESULTS_DIR / "v6_p2" / "answers_for_claude.json",
        RESULTS_DIR / "answers_for_claude.json",
    ]
    answers_path = next((p for p in candidates if p.exists()), None)
    if answers_path is None:
        print("❌  answers_for_claude.json not found. Run rag_accuracy_eval.py first.")
        return

    pairs = json.loads(answers_path.read_text(encoding="utf-8"))
    print(f"📂  Loaded {len(pairs)} Q&A pairs from {answers_path}")
    print(f"🔍  Scoring with local keyword+number judge…\n")

    rows: list[dict] = []
    by_doc: dict[str, list[int]] = {}

    for p in pairs:
        doc      = p["doc"]
        q_num    = p["q_num"]
        question = p["question"]
        cand     = p.get("docnest_answer", "")
        ref      = p.get("expected_answer", "")

        score, reason = _local_judge(question, cand, ref)
        icon = "✅" if score >= 7 else ("⚠️" if score >= 5 else "❌")
        rows.append({**p, "score": score, "reason": reason, "icon": icon})
        by_doc.setdefault(doc, []).append(score)
        print(f"  {icon} [{doc[:40]}] Q{q_num}: {score}/10  ({reason})")

    # ── Summary ───────────────────────────────────────────────────────────────
    all_scores = [r["score"] for r in rows]
    avg  = sum(all_scores) / len(all_scores) if all_scores else 0
    pasn = sum(1 for s in all_scores if s >= 7)
    pct  = pasn / len(all_scores) * 100 if all_scores else 0

    print(f"\n{'='*60}")
    print(f"📊  RESULTS SUMMARY")
    print(f"    Total questions : {len(all_scores)}")
    print(f"    Average score   : {avg:.1f} / 10")
    print(f"    Pass rate (≥7)  : {pasn}/{len(all_scores)} ({pct:.0f}%)")
    print(f"\n    Per-document breakdown:")
    for doc, scores in by_doc.items():
        doc_avg  = sum(scores) / len(scores)
        doc_pass = sum(1 for s in scores if s >= 7)
        print(f"      {doc[:50]:<50}  avg={doc_avg:.1f}  pass={doc_pass}/{len(scores)}")
    print(f"{'='*60}\n")

    # ── Write markdown report ─────────────────────────────────────────────────
    out = answers_path.parent / "scored_results.md"
    lines = [
        "# DocNest Scored Results",
        "",
        f"**Total questions:** {len(all_scores)}  |  "
        f"**Avg score:** {avg:.1f}/10  |  "
        f"**Pass rate:** {pasn}/{len(all_scores)} ({pct:.0f}%)",
        "",
        "| # | Document | Q | Score | Reasoning | DocNest Answer (120c) | Expected Answer (100c) |",
        "|---|----------|---|-------|-----------|----------------------|------------------------|",
    ]
    for i, r in enumerate(rows, 1):
        dn   = r.get("docnest_answer", "")[:120].replace("|", "｜").replace("\n", " ")
        ref  = r.get("expected_answer", "")[:100].replace("|", "｜").replace("\n", " ")
        lines.append(
            f"| {i} | {r['doc'][:40]} | Q{r['q_num']} "
            f"| {r['icon']} {r['score']}/10 | {r['reason']} "
            f"| {dn} | {ref} |"
        )

    out.write_text("\n".join(lines), encoding="utf-8")
    print(f"💾  Scored results written → {out}")


if __name__ == "__main__":
    main()
