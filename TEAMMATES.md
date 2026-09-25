# Thành viên nhóm snoopi

Đồ án RAG pipeline hỏi đáp quy chế UIT — lớp K4-L3B.
Repository: https://github.com/hddung-vinai/K4-L3B-RAG-Pipeline

| Họ và tên | Mã học viên | GitHub | Vai trò | Nhánh |
| --------- | ----------- | ------ | ------- | ----- |
| Hoàng Đức Dũng | 2A202602798 | `hddung-vinai` | Dựng pipeline, đánh giá, giao diện | `dung` |
| Nguyễn Phúc Huy | 2A202602911 | `Yuhnguyn` | Mở rộng viết tắt, conversation memory, hỗ trợ provider | `feat/abbrev-memory-commandcode` |
| Phan Đại Cương | 2A202602510 | `cuongphanhp` | Cross-encoder reranker | `reranker` |

## Phần việc chi tiết

### Hoàng Đức Dũng — 2A202602798

Dựng toàn bộ pipeline từ Task 1 đến Task 10, giao diện Streamlit và phần đánh giá.

| Hạng mục | File |
| -------- | ---- |
| Thu thập corpus, crawl, chuẩn hóa Markdown | `src/task1_collect_legal_docs.py`, `src/task2_crawl_news.py`, `src/task3_convert_markdown.py` |
| Chunking hai tầng, embedding, ChromaDB | `src/task4_chunking_indexing.py` |
| Dense search và BM25 | `src/task5_semantic_search.py`, `src/task6_lexical_search.py` |
| RRF, vectorless fallback, pipeline truy xuất | `src/task7_reranking.py`, `src/task8_pageindex_vectorless.py`, `src/task9_retrieval_pipeline.py` |
| Generation có citation và safe refusal | `src/task10_generation.py` |
| Giao diện Streamlit | `app.py`, `.streamlit/config.toml` |
| Golden dataset, script A/B, báo cáo đánh giá | `src/run_evaluation.py`, `group_project/evaluation/` |
| Slide thuyết trình | `slides/K4-L3B-RAG-Pipeline-Slides.pptx` |

Báo cáo cá nhân: `reports/2A202602798-HoangDucDung.md`

### Nguyễn Phúc Huy — 2A202602911

Bổ sung trên nền pipeline đã có, tập trung vào recommendation #1 của báo cáo đánh giá và hạng mục bonus.

| Hạng mục | File |
| -------- | ---- |
| Mở rộng viết tắt khi index — trích bảng viết tắt từ chính văn bản, chèn dạng đầy đủ vào chunk, có cờ `GLOSSARY_EXPANSION` để đo A/B | `src/glossary.py`, `src/task4_chunking_indexing.py`, `tests/test_glossary.py` |
| Conversation memory — viết lại câu hỏi nối tiếp thành câu hỏi độc lập trước khi retrieve, fallback về câu gốc khi LLM lỗi | `src/conversation_memory.py`, `app.py`, `tests/test_conversation_memory.py` |
| Hỗ trợ `OPENAI_BASE_URL`, tách evaluator embeddings, script so sánh hai lần chạy | `src/task10_generation.py`, `src/run_evaluation.py`, `src/compare_evaluation.py`, `tests/test_llm_provider.py` |
| Đồng bộ tài liệu — số chunk 422 → 396, gộp `reports/RESULT.md` về một nguồn | `group_project/evaluation/RESULT.md`, `README.md` |

Commit: `7c3f61e`, `9eb6be9`, `edff827`, `6accc86`, `58def75` — PR #2
Báo cáo cá nhân: `reports/INDIVIDUAL_REPORT.md`

### Phan Đại Cương — GitHub `cuongphanhp`

| Hạng mục | File |
| -------- | ---- |
| Cross-encoder reranker `BAAI/bge-reranker-v2-m3` chấm lại pool 20 ứng viên sau RRF, có xử lý lỗi rơi về RRF khi model không tải được | `src/task7_reranking.py`, `src/task9_retrieval_pipeline.py` |

Commit: `8451075` — PR #3
Báo cáo cá nhân: `reports/INDIVIDUAL_REPORT.md`

## Ghi chú

Các commit của tài khoản `khvavuong` (`7a43099`, `3c01a06`, `2bbe0e0`, `39fccd0`, `6a2a2d4`)
thuộc **repository mẫu của môn học** `VinUni-AI20k/K4-L3A-RAG-Pipeline`, không phải
thành viên nhóm. Repo này fork từ đó; remote `upstream` vẫn trỏ về bản gốc.
