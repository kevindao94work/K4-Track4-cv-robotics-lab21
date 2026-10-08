# Lab 21 — Theo dõi nhiều đối tượng

Kho mã: https://github.com/kevindao94work/K4-Track4-cv-robotics-lab21, ở chế độ riêng tư (PRIVATE), nhánh `main`, remote `origin`.

Đã hoàn thành các yêu cầu trong `IMPLEMENTATION_GUIDE.md` trên dữ liệu thật được chỉ định: 51 lượt thí nghiệm, năm kết quả MOT cho toàn bộ chuỗi, notebook đã thực thi, chỉ số tính bằng TrackEval và báo cáo tiếng Việt. Trạng thái nghiệm thu và bằng chứng của từng mốc được ghi trong `reports/checkpoints.json`. Mỗi mốc chỉ được công nhận hoàn thành sau khi đạt các kiểm tra nghiệm thu.

## Thiết lập và tái lập

```sh
python3.11 -m venv .venv
.venv/bin/python -m pip install -r requirements-lock.txt
.venv/bin/python -m pip install -e . --no-deps
git clone https://github.com/JonathonLuiten/TrackEval.git TrackEval
git -C TrackEval checkout 12c8791b303e0a0b50f753af204249e622d0281a
.venv/bin/python -m pip install -e TrackEval --no-deps
.venv/bin/python scripts/patch_trackeval.py
.venv/bin/python scripts/setup_environment.py
.venv/bin/python scripts/download_data.py
export LAB_DATA="$PWD/data/extracted/data_lab21"
.venv/bin/python scripts/check_data.py --lab-data-root "$LAB_DATA"
.venv/bin/python scripts/inspect_scenes.py --lab-data-root "$LAB_DATA"
.venv/bin/python -m pytest -v
.venv/bin/python scripts/run_tracking.py --source "$LAB_DATA/video_1/img1" --seq-name video_1 --tracker bytetrack --conf .30 --iou .50 --max-frames 150 --save-video
.venv/bin/python scripts/run_experiments.py --phase tracker
# Xem các ảnh so sánh đồng bộ trước khi chọn tracker và ngưỡng confidence.
.venv/bin/python scripts/run_experiments.py --phase conf --tracker bytetrack
.venv/bin/python scripts/run_experiments.py --phase iou --tracker bytetrack --conf .30
# Chạy từng cấu hình đã chọn với --out runs/nop_bai và không dùng --max-frames.
.venv/bin/python scripts/evaluate_video1.py
.venv/bin/python scripts/validate_submission.py
.venv/bin/python scripts/prepare_submission.py
```

Hai bộ trọng số là `weights/yolo26n.pt` và `weights/osnet_x0_25_msmt17.pt`; URL nguồn chính thức và SHA256 được lưu cùng thông tin môi trường. Detector dùng nhánh one-to-many có NMS (`nms=None`), kích thước ảnh 640 và lớp người (COCO class 0). Re-ID chạy trên CPU, được cấu hình rõ ràng và kiểm tra encoder thực sự hoạt động. Seed được đặt là 42; các phép toán MPS không bảo đảm kết quả giống nhau từng bit giữa các lần chạy. Khóa bộ nhớ đệm gồm mã băm mô hình, nội dung frame, confidence, NMS IoU, kích thước ảnh và chế độ suy luận. Mỗi chuỗi khởi tạo tracker mới. Bộ kiểm tra bài nộp từ chối kết quả chỉ xử lý một phần chuỗi.

Dữ liệu, trọng số, mã nguồn bên thứ ba và môi trường cục bộ không được đưa vào Git. Nhãn gốc (GT) chỉ được dùng để đánh giá `video_1`, với bước tiền xử lý các đối tượng gây nhiễu theo MOT17. Không tính HOTA/MOTA/IDF1 cho video 2–5.

## Kết quả cuối cùng

Tất cả các mốc CP0–CP5 đã đạt kiểm tra nghiệm thu. Detector chạy MPS trên Apple Silicon; Re-ID chạy CPU FP32. Bộ chuyển đổi của cả năm tracker đều đạt kiểm tra khởi chạy và kiểm thử hồi quy; các thí nghiệm so sánh trên video thật dùng ByteTrack và BoTSORT với encoder OSNet thực sự tạo embeddings.

| Video | Tracker | Ngưỡng confidence | NMS IoU | Số frame |
|---|---|---|---|---|
| video_1 | botsort | 0.15 | 0.50 | 600 |
| video_2 | bytetrack | 0.15 | 0.50 | 1050 |
| video_3 | botsort | 0.30 | 0.50 | 837 |
| video_4 | bytetrack | 0.30 | 0.50 | 900 |
| video_5 | bytetrack | 0.30 | 0.50 | 750 |

Kết quả TrackEval của `video_1`: **HOTA 27,6804%, MOTA 15,1284%, IDF1 24,4190%**. Điểm tuyệt đối còn thấp do bỏ sót nhiều người; video 2–5 chỉ được đánh giá bằng quan sát trực quan. Chi tiết so sánh và các hạn chế nằm trong [báo cáo](reports/BAO_CAO_LAB21.md).

Chạy lại toàn bộ 51 cấu hình thí nghiệm đã ghi nhận và các cấu hình được chọn cho bài nộp:

```sh
.venv/bin/python scripts/reproduce_experiments.py --lab-data-root "$LAB_DATA"
.venv/bin/python scripts/evaluate_candidates.py
.venv/bin/python scripts/render_comparisons.py
.venv/bin/python scripts/run_selected.py --lab-data-root "$LAB_DATA"
.venv/bin/python scripts/evaluate_video1.py --lab-data-root "$LAB_DATA"
.venv/bin/python scripts/validate_submission.py
.venv/bin/python scripts/prepare_submission.py
```

Kết quả MOT dùng chỉ số frame và ID track dương, với gốc tọa độ bounding box là `(1,1)`. Script chuyển đổi tọa độ chỉ dành cho các kết quả phát triển cũ; các lượt chạy mới đã dùng đúng gốc tọa độ và không được dịch thêm lần nữa. File cục bộ `submission.zip` chứa đúng năm file TXT và báo cáo tiếng Việt, được loại khỏi Git. Bằng chứng push của CP0–CP4 được lưu trong `reports/checkpoint_receipts.json`; bằng chứng push CP5 được lưu cục bộ trong `reports/push_verification.jsonl`. Có thể kiểm tra SHA trên remote bằng lệnh `git ls-remote origin refs/heads/main`.
