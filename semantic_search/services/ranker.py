import numpy as np


def cosine_top_k(query_vec: list[float], items: list[tuple[object, list[float]]], k: int = 20):
    """
    items: [(event_obj, embedding_list), ...]
    Retorna [(event_obj, score), ...] ordenat desc.
    """
    if not query_vec:
        return []

    q = np.array(query_vec, dtype=np.float32)
    if np.linalg.norm(q) == 0:
        return []

    scored = []
    for obj, emb in items:
        if not emb:
            continue
        v = np.array(emb, dtype=np.float32)
        if v.shape != q.shape or np.linalg.norm(v) == 0:
            continue
        score = float(np.dot(q, v))  # ja normalitzats => cosine
        scored.append((obj, score))

    scored.sort(key=lambda x: x[1], reverse=True)
    return scored[:k]
