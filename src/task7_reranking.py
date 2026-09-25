"""Task 7 — Reciprocal Rank Fusion and BGE cross-encoder reranking.

RRF gộp nhiều bảng xếp hạng mà không cộng trực tiếp cosine score với BM25
score. Công thức: RRF(d) = sum(1 / (k + rank)), rank bắt đầu từ 1.

Lưu ý: RRF score chỉ phản ánh thứ hạng, không dùng để quyết định fallback.

Vì sao phải copy item trước khi thay score: Task 9 đọc cosine score gốc từ
danh sách dense để quyết định fallback. Nếu RRF ghi đè score trực tiếp lên item
của danh sách đầu vào thì cosine score (~0.6) bị thay bằng RRF score (~0.03),
và mọi truy vấn sẽ rơi xuống dưới threshold.
"""

import os


RERANKER_MODEL = os.getenv("RERANKER_MODEL", "BAAI/bge-reranker-v2-m3")

_reranker = None


def rerank_rrf(
    ranked_lists: list[list[dict]],
    top_k: int = 5,
    k: int = 60,
) -> list[dict]:
    """Fuse nhiều ranked lists và trả hybrid SearchResult."""
    if top_k <= 0:
        return []

    scores: dict[str, float] = {}
    items: dict[str, dict] = {}

    for ranked_list in ranked_lists:
        for rank, item in enumerate(ranked_list, 1):   # rank bắt đầu từ 1
            item_id = item["id"]
            scores[item_id] = scores.get(item_id, 0.0) + 1.0 / (k + rank)
            # Giữ bản gặp đầu tiên: mọi danh sách đều mang cùng content/metadata
            # cho một ID, chỉ khác score và retrieval_method.
            items.setdefault(item_id, item)

    ranked_ids = sorted(scores, key=lambda item_id: scores[item_id], reverse=True)

    results = []
    for item_id in ranked_ids[:top_k]:
        result = items[item_id].copy()   # không sửa item của danh sách đầu vào
        result["score"] = scores[item_id]
        result["retrieval_method"] = "hybrid"
        results.append(result)
    return results


def rerank_bge(query: str, candidates: list[dict], top_k: int = 5) -> list[dict]:
    """Rerank RRF candidates with BGE cross-encoder scores.

    The model is loaded lazily so indexing and tests do not pay its startup cost.
    Callers can disable this stage with ``RERANKER_ENABLED=0``; failures are
    intentionally raised so the retrieval pipeline can fall back to RRF.
    """
    global _reranker
    if not candidates or top_k <= 0:
        return []

    if _reranker is None:
        from sentence_transformers import CrossEncoder

        _reranker = CrossEncoder(RERANKER_MODEL)

    pairs = [(query, item["content"]) for item in candidates]
    scores = _reranker.predict(pairs)

    results = []
    for item, score in zip(candidates, scores):
        result = item.copy()
        result["score"] = float(score)
        result["retrieval_method"] = "hybrid"
        results.append(result)
    return sorted(results, key=lambda item: item["score"], reverse=True)[:top_k]


if __name__ == "__main__":
    dense = [
        {"id": "chunk-0", "content": "a", "score": 0.9, "metadata": {}, "retrieval_method": "dense"},
        {"id": "chunk-1", "content": "b", "score": 0.8, "metadata": {}, "retrieval_method": "dense"},
    ]
    bm25 = [
        {"id": "chunk-1", "content": "b", "score": 7.0, "metadata": {}, "retrieval_method": "bm25"},
        {"id": "chunk-2", "content": "c", "score": 5.0, "metadata": {}, "retrieval_method": "bm25"},
    ]
    print("dense:", [(x["id"], x["score"]) for x in dense])
    print("bm25 :", [(x["id"], x["score"]) for x in bm25])
    print("fused:")
    for item in rerank_rrf([dense, bm25], top_k=3):
        print(f"  {item['score']:.5f}  {item['id']}  {item['retrieval_method']}")
    print("dense sau khi fuse (phải giữ nguyên):",
          [(x["id"], x["score"]) for x in dense])
