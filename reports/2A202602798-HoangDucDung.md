## Thông tin

- Họ và tên: Hoàng Đức Dũng
- Mã học viên: 2A202602798
- Nhóm: snoopi
- Repository/branch: https://github.com/hddung-vinai/K4-L3B-RAG-Pipeline/dung

## Phần việc đã thực hiện

| Module/deliverable | Việc tôi trực tiếp làm | File/commit/PR | Trạng thái |
|---|---|---|---|
| Thu thập corpus | Chốt chủ đề quy chế UIT, kiểm tra `robots.txt`, viết script sàng 69 PDF theo tỉ lệ ký tự tiếng Việt để loại bản scan và bản OCR font không Unicode, giữ lại 6 file | `src/task1_collect_legal_docs.py`, `data/landing/legal/` | Done |
| Crawl bài viết | Viết `crawl_article()` với cấu hình tách theo domain (React SPA dùng mặc định, Drupal dùng `target_elements="#main-content"`), lọc boilerplate và link SEO rác | `src/task2_crawl_news.py`, `data/landing/news/` | Done |
| Chuẩn hóa Markdown | Nối lại câu bị PDF ngắt giữa chừng, khôi phục heading Chương/Điều, nhúng YAML frontmatter, sửa 151 ký tự `ƣ` của văn bản 196 | `src/task3_convert_markdown.py`, `data/standardized/` | Done |
| Chunking + indexing | Chunk hai tầng 800/120, gắn lại tên Điều vào chunk con, embedding `bge-m3`, dọn chunk mồ côi sau `upsert` | `src/task4_chunking_indexing.py` | Done |
| Dense + BM25 | `semantic_search()` dùng chung `embed_texts()` với Task 4; `lexical_search()` với tokenizer giữ nguyên mã văn bản dạng `790/QĐ-ĐHCNTT` | `src/task5_semantic_search.py`, `src/task6_lexical_search.py` | Done |
| RRF + fallback | `rerank_rrf()` có copy item trước khi ghi score; vectorless retriever cục bộ hai tầng; `retrieve()` đọc dense score gốc để quyết định fallback, bọc `try/except` quanh provider | `src/task7_reranking.py`, `src/task8_pageindex_vectorless.py`, `src/task9_retrieval_pipeline.py` | Done |
| Generation + UI | `generate_with_citation()` có safe refusal ba đường; giao diện Streamlit hiển thị nguồn thật kèm liên kết văn bản gốc | `src/task10_generation.py`, `app.py` | Done |
| Evaluation | 15 golden case trích `expected_context` nguyên văn từ corpus, script A/B, phân tích 3 case kém nhất | `src/run_evaluation.py`, `group_project/evaluation/` | Done |

Chỉ kê khai công việc có thể đối chiếu bằng file, commit, pull request, test hoặc kết quả evaluation.

## Quyết định kỹ thuật quan trọng

Mô tả tối đa hai quyết định mà bạn trực tiếp tham gia:

1. **Quyết định:** Nâng `CHUNK_SIZE` từ 500 lên 800 và chunk hai tầng — tách theo heading Chương/Điều trước, cắt theo ký tự sau.
   **Lý do/evidence:** Đo phân phối độ dài của 156 Điều trong corpus: trung vị 799 ký tự, chỉ 52/156 Điều vừa trong 500 ký tự còn 78/156 vừa trong 800. Với cấu hình starter, hai phần ba số Điều bị chẻ nhỏ; ví dụ Điều 4 của 790/QĐ-ĐHCNTT định nghĩa tín chỉ dài khoảng 1.700 ký tự bị cắt thành 4 mảnh, nên câu hỏi "một tín chỉ bằng bao nhiêu tiết" có thể trúng mảnh không chứa con số.
   **Trade-off:** Chunk lớn hơn làm tăng recall nhưng giảm precision vì mỗi chunk mang thêm nội dung không liên quan. Số chunk giảm từ khoảng 463 xuống 396. Chỉ dùng tầng một là không đủ vì Điều dài nhất tới 13.077 ký tự, nên phải giữ cả tầng cắt theo ký tự.

2. **Quyết định:** Dùng `BM25Plus` thay cho `BM25Okapi`.
   **Lý do/evidence:** Công thức Okapi tính `idf = log(N − n + 0.5) − log(n + 0.5)`, cho đúng 0 khi term xuất hiện ở một nửa số tài liệu. Trên corpus 2 tài liệu của `test_lexical_search_returns_bm25_contract`, toàn bộ score về 0 nên không có kết quả nào vượt bộ lọc — kể cả đoạn code gợi ý sẵn trong scaffold cũng không thể pass test này. `BM25Plus` (Lv & Zhai, 2011) thêm cận dưới nên xếp hạng vẫn đúng trên corpus nhỏ.
   **Trade-off:** Mất ngưỡng 0 tự nhiên để phát hiện "không khớp gì", vì mọi tài liệu đều nhận điểm dương. Không ảnh hưởng tới pipeline vì Task 9 dùng cosine score của dense làm ngưỡng fallback, không dùng điểm BM25.

## Kiểm thử và kết quả

- **Test hoặc query tôi đã dùng:**
  - `pytest tests/ -q` → 20 passed (15 contract test + 5 acceptance test).
  - Hiệu chỉnh ngưỡng fallback bằng 11 truy vấn thủ công: 6 câu trong chủ đề và 5 câu ngoài chủ đề, đo `best_dense_score` của từng câu.
  - Đánh giá A/B bằng RAGAS trên 15 golden case, hai cấu hình chỉ khác `use_reranking`.
  - Kiểm chứng end-to-end qua giao diện bằng `streamlit.testing.v1.AppTest`: một truy vấn trong chủ đề và một ngoài chủ đề.

- **Kết quả trước/sau nếu có:**
  - Ngưỡng fallback: trong chủ đề 0.6282–0.7391, ngoài chủ đề 0.3432–0.4361 → chọn 0.55. Giá trị mặc định 0.3 của starter thấp hơn cả truy vấn ngoài chủ đề tệ nhất nên fallback sẽ không bao giờ kích hoạt.
  - A/B: Config A (dense-only) average 0.8178, Config B (hybrid + RRF) 0.7961, delta −0.0217. Config A thắng cả bốn metric.
  - Thí nghiệm sửa `SYSTEM_PROMPT` nhằm nâng answer relevance: faithfulness tụt 1.0000 → 0.8889 và answer relevance cũng tụt 0.4426 → 0.4072, nên đã quay lại bản gốc.

- **Lỗi đã phát hiện và cách xử lý:**
  - Đa số PDF trên cổng UIT, ĐHQG-HCM và Bộ GD&ĐT là bản scan hoặc OCR bằng font VNI/TCVN3, trích ra ký tự rác nhưng vẫn dài hơn ngưỡng của acceptance test. Viết script sàng 69 PDF theo tỉ lệ ký tự tiếng Việt có dấu, giữ lại 24 file dùng được.
  - Văn bản 196/QĐ-ĐHCNTT chứa 151 ký tự `ƣ` thay cho `ư` do font trong PDF gốc, khiến `đƣợc` không khớp `được` ở cả BM25 lẫn embedding. Thêm bảng ánh xạ ký tự trong `normalize_text()`, chỉ map hai ký tự chắc chắn sai.
  - Mục lục của văn bản bị biến thành heading, tạo chunk chỉ chứa dòng tiêu đề nhưng vẫn cạnh tranh thứ hạng với chunk có nội dung. Lọc theo dấu hiệu dot leader và gộp section ngắn hơn 50 ký tự vào section kế tiếp; số chunk rác giảm từ 37 xuống 10.
  - `upsert()` không xóa ID cũ: khi đổi `CHUNK_SIZE`, 26 chunk của cấu hình trước vẫn nằm lại trong ChromaDB và vẫn được search trả về. Thêm bước dọn chunk mồ côi trong `index_to_vectorstore()`.
  - Nhãn `[Document N]` trong câu trả lời đánh theo thứ tự context sau `reorder_for_llm()`, không phải thứ tự `sources` sắp theo score. Lấy thẳng chỉ số thì 3/5 citation trỏ sai nguồn. Sửa bằng `citation_numbers()` trong `app.py`.
  - Mở ChromaDB `PersistentClient` từ hai tiến trình cùng lúc làm hỏng file HNSW index, phải embed lại toàn bộ corpus. Ghi lưu ý vận hành vào báo cáo: không chạy `app.py` song song với `task4`.

## Điều còn hạn chế

- **Một hạn chế cụ thể của phần tôi làm:** Retrieval không bắc được cầu giữa dạng viết tắt và dạng đầy đủ. Văn bản 159/QĐ-ĐHCNTT dùng `KLTN` 113 lần so với 11 lần viết "khóa luận tốt nghiệp", `CBPB` 25 lần so với 2 lần viết "cán bộ phản biện". Câu hỏi của người dùng viết đầy đủ nên cả 5 chunk lấy về đều từ văn bản khác, `context_recall = 0.000`. Có case khác trả lời đúng chỉ vì văn bản sai tình cờ chứa cùng thông tin — nếu hai văn bản mâu thuẫn nhau thì hệ thống đã trả lời sai mà không ai phát hiện.

- **Nếu có thêm thời gian, thay đổi đầu tiên tôi sẽ thực hiện:** Đọc bảng thuật ngữ ở Điều 2 của mỗi văn bản rồi chèn dạng đầy đủ vào chunk, ví dụ `KLTN (khóa luận tốt nghiệp)`, cài đặt trong `chunk_documents()`. Xác minh bằng cách chạy lại `python -m src.task4_chunking_indexing` và `python -m src.run_evaluation`, kiểm tra cột `chunk_ids` của case này trong `raw_results.json` có xuất hiện `legal/159-...` hay không, và `context_recall` của nhóm câu hỏi `confusable` có tăng từ mức 0.800 hiện tại hay không.

## Xác nhận đóng góp

Tôi xác nhận nội dung trên phản ánh đúng phần việc của mình và có thể giải thích hoặc chạy lại trong buổi demo.

- Ngày: 25-9-2026
- Tên thành viên: Hoàng Đức Dũng
