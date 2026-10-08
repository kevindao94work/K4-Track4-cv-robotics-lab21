# Lab 21 — Lựa chọn tracker cho năm video

## Trạng thái thực hiện

Báo cáo đang được xây dựng từ thực nghiệm thật. Chưa công bố cấu hình cuối cùng hoặc điểm số trước khi hoàn thành kiểm tra tương ứng. Dữ liệu synthetic chỉ được dùng trong regression tests.

## Mục tiêu và cơ sở lý thuyết

Câu hỏi nghiên cứu là tracker nào duy trì ID ổn định hơn trong từng cảnh và vì sao. Detector YOLO26n tìm người trong từng ảnh; tracker duy trì lịch sử và ghép các detections qua thời gian. Một detection độc lập chưa có danh tính thời gian.

ByteTrack ghép detections confidence cao rồi tận dụng detections confidence thấp để khôi phục track. OCSORT bổ sung cập nhật theo quan sát để giảm sai lệch mô hình chuyển động. BoTSORT kết hợp motion, bù chuyển động camera và appearance; StrongSORT dùng appearance cùng motion; DeepOCSORT bổ sung appearance vào họ OCSORT. Khả năng hỗ trợ Re-ID không chứng minh encoder đã chạy: triển khai phải cấu hình checkpoint và kiểm tra encoder sống sau update với detections thực.

Re-ID biểu diễn ngoại hình thành vector để đối chiếu người trước và sau che khuất. Che khuất có thể làm mất detection, ngắt track hoặc đổi ID. ID switch là lỗi gán danh tính được xác định với GT; với video không nhãn chỉ có thể ghi nhận thay đổi ID quan sát được, không gọi thống kê dự đoán là accuracy.

## Confidence, IoU, NMS và metrics

IoU(A,B) = |A ∩ B| / |A ∪ B|. Bbox không có diện tích hoặc không giao cho IoU bằng 0 trong hàm kiểm thử. Confidence lọc dự đoán detector. NMS giữ box điểm cao và loại box cùng lớp chồng lấp vượt ngưỡng IoU. Tham số `--iou` chỉ điều khiển NMS detector; ngưỡng association của các tracker giữ mặc định, không điều chỉnh để tạo lợi thế.

YOLO26 có nhánh NMS-free và nhánh one-to-many. Phiên bản cài đặt dùng `nms=None` để chọn one-to-many và áp NMS; kiểm thử xác nhận backend `end2end=False`. Kiểm thử overlap có hai box IoU 0,6: threshold 0,4 giữ một box, 0,7 giữ hai. Video thật không bắt buộc thay đổi nếu box không có mức overlap phù hợp.

- MOTA = 1 − (FN + FP + IDSW)/GT, có thể âm; chịu ảnh hưởng lớn bởi bỏ sót và false positives.
- IDF1 = 2IDTP/(2IDTP + IDFP + IDFN), nhấn mạnh sự nhất quán danh tính toàn chuỗi.
- HOTA_α = √(DetA_α × AssA_α), sau đó trung bình qua các ngưỡng α; cân bằng detection và association, không phải trung bình MOTA và IDF1.

Chỉ video_1 có đánh giá định lượng từ GT thật. TrackEval dùng GT MOT17 gốc với preprocessing để xử lý zero-marked objects và distractor classes. Không tạo GT từ predictions, không tính HOTA/MOTA/IDF1 cho video_2–5.

## Thiết kế thực nghiệm

Giữ cố định `yolo26n.pt`, imgsz=640, COCO class 0, Re-ID `osnet_x0_25_msmt17.pt`. So sánh motion và appearance trên cùng frame, confidence=0,30 và NMS IoU=0,50. Sau đó khảo sát confidence 0,15/0,30/0,50 với tracker và IoU cố định; khảo sát IoU 0,40/0,50/0,70 với tracker và confidence đã chọn. Không chạy Cartesian product. Mỗi sequence khởi tạo tracker mới.

Cache detections chỉ tái sử dụng khi model SHA256, source frame SHA256, preprocessing, imgsz, class, confidence và NMS IoU khớp. Kết quả cuối phải xử lý toàn bộ frames; metadata và validator từ chối preview có giới hạn frames.

## Giới hạn và khả năng tái lập

Seed=42. MPS không bảo đảm bitwise determinism. Encoder Re-ID chạy CPU để tránh thao tác không tương thích. Runtime đo gồm xử lý tracker, vẽ preview, cache I/O; cache warm/cold có thể ảnh hưởng FPS nên không dùng FPS làm tiêu chí chính. Những video không có FPS metadata đáng tin cậy chỉ báo frame index; preview dựng ở 25 FPS phục vụ xem và không được suy diễn là thời gian gốc.

## Tài liệu tham khảo

- [Ultralytics YOLO26](https://docs.ultralytics.com/models/yolo26/)
- [BoxMOT](https://github.com/mikel-brostrom/boxmot)
- [TrackEval](https://github.com/JonathonLuiten/TrackEval)
- [MOTChallenge](https://motchallenge.net/)
