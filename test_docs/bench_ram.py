import tracemalloc, sys
sys.path.insert(0, "D:/Learning/docnest")
from docnest.reader import UDFIndex

def measure(path):
    tracemalloc.start()
    idx = UDFIndex.load(path)
    cur, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    return cur, peak, idx

print("=== RAM at index load (before any search) ===")
c1, p1, _ = measure("D:/Learning/docnest/test_docs/sample_report.udf")
print(f"v1 (old) : current={c1/1024:.1f} KB  peak={p1/1024:.1f} KB")

c3, p3, idx3 = measure("D:/Learning/docnest/test_docs/sample_report_v3.udf")
print(f"v3 (new) : current={c3/1024:.1f} KB  peak={p3/1024:.1f} KB")
print(f"Savings  : {(p1-p3)/1024:.1f} KB  ({100*(p1-p3)/p1:.0f}% less peak RAM on load)")

print()
print("=== Embedding matrix state before search ===")
print(f"  _embed_matrix_loaded   = {idx3._embed_matrix_loaded}")
print(f"  _embed_matrix          = {idx3._embed_matrix}")
print(f"  _has_binary_embeddings = {idx3._has_binary_embeddings}")

print()
print("=== RAM after first search (lazy load triggered) ===")
tracemalloc.start()
result = idx3._hybrid_search("azure migration")
c_s, p_s = tracemalloc.get_traced_memory()
tracemalloc.stop()
print(f"Post-search: current={c_s/1024:.1f} KB  peak={p_s/1024:.1f} KB")
print(f"  _embed_matrix_loaded = {idx3._embed_matrix_loaded}")
print(f"  embed_matrix shape   = {idx3._embed_matrix.shape if idx3._embed_matrix is not None else 'None'}")
top = result[0] if result else ("none", 0)
print(f"  Top result: {top[0]}  score={top[1]:.3f}")
