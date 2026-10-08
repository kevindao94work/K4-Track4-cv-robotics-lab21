# Lab 21 — Lựa chọn tracker cho năm video

## Trạng thái thực hiện

Đã chạy thực nghiệm trên dữ liệu thật, xuất đủ năm sequence và tính TrackEval cho video_1. Dữ liệu synthetic chỉ được dùng trong regression tests, không đưa vào kết quả lab.

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


<!-- RESULTS -->

## Môi trường và dữ liệu thật

Python 3.11.15; macOS-27.2-arm64-arm-64bit; RAM 16 GiB. Detector dùng mps; encoder Re-ID dùng CPU FP32. PyTorch 2.14.1.

| Thành phần | Phiên bản |
|---|---|
| ultralytics | 8.4.174 |
| boxmot | 25.0.0 |
| numpy | 2.4.6 |
| opencv-python | 4.14.0.94 |
| trackeval | 1.0.dev1 |


TrackEval commit: `12c8791b303e0a0b50f753af204249e622d0281a`. Script `patch_trackeval.py` chỉ thay alias np.float/np.int/np.bool đã bị loại bỏ bằng built-in tương ứng, không đổi logic metric. BoxMOT 25.0.0 cài từ PyPI dùng TrackerSpec và configure_reid(ReIDEncoderSpec); không giả định API nhánh master giống wheel đã cài. Cả năm tracker qua smoke test; ba tracker appearance xác nhận encoder đã chạy và OSNet nạp đủ 565/565 tensors.


| Checkpoint | SHA256 |
|---|---|
| osnet_x0_25_msmt17.pt | `6f57607fed9f502b9efed546108132ee715df5a5b6e6932c6269bacb47f59f99` |
| yolo26n.pt | `9b09cc8bf347f0fc8a5f7657480587f25db09b34bf33b0652110fb03a8ad4fef` |


Nguồn dữ liệu là archive Drive được chỉ định (647 MB), tải công khai thành công; SHA256 và URL trong `artifacts/dataset_source.json`. Tất cả JPG được đọc kiểm tra; frame đặt tên số liên tục bắt đầu từ 1.


| Video | Frames | Kích thước H×W | FPS gốc |
|---|---|---|---|
| video_1 | 600 | [[1080, 1920]] | 30.0 |
| video_2 | 1050 | [[1080, 1920]] | Không có metadata đáng tin cậy |
| video_3 | 837 | [[480, 640]] | Không có metadata đáng tin cậy |
| video_4 | 900 | [[1080, 1920]] | Không có metadata đáng tin cậy |
| video_5 | 750 | [[1080, 1920]] | Không có metadata đáng tin cậy |


video_1 là MOT17-02-FRCNN, GT gốc có 9 cột, phủ frames 1–600. Có 18581 hàng pedestrian hợp lệ trước preprocessing. Không thay missing labels bằng negative GT. Các class/zero-marked objects được giữ nguyên để TrackEval xử lý.

## Phân tích cảnh và giả thuyết trước thí nghiệm



Nguồn: sáu frame rải đều trên mỗi video, contact sheets `video_1.jpg` đến `video_5.jpg`. Nhận định dưới đây đến từ ảnh thật; chưa phải kết luận tracker.

| Video | Dữ kiện quan sát | Rủi ro cần kiểm chứng |
|---|---|---|
| video_1 | Frame 1–600: quảng trường ngoài trời; nền nhà/cây giữ vị trí; người gần tiền cảnh lớn hơn người xa; nhóm đi ngang giao nhau, có xe đạp ở 360–480. | Người nhỏ ở nền dễ bỏ sót; crossing có thể làm đổi ID. |
| video_2 | Frame 1–1050: phố đêm nhìn từ cao; cột đèn cháy sáng; xe trắng gần cố định; nhiều người nhỏ quanh cửa hàng phía trái; cảnh sampled không phải lúc nào cũng cực đông. | Confidence cao có thể mất người xa; ngoại hình thiếu chi tiết làm Re-ID không chắc tốt hơn motion. |
| video_3 | Frame 1–837: camera đi qua đường rồi theo người lên vỉa hè; người rất gần che phần lớn ảnh ở 168–502; nền đổi mạnh. Không có FPS metadata nên low-FPS là mô tả từ guide, chưa được đo. | Motion và appearance đều khó khi người ra/vào mép ảnh; scale thay đổi mạnh. |
| video_4 | Frame 1–900: hành lang trung tâm thương mại; camera tiến tới; lan can kính, cửa kính và sàn phản chiếu; người đi hai chiều, người tiền cảnh bị cắt ở mép ảnh. | Reflection có thể tạo detections phụ; camera motion gây fragmentation. |
| video_5 | Frame 1–750: camera cao trên xe, qua giao lộ rồi rẽ; góc nhìn đổi mạnh ở 300–600; người trên vỉa hè nhỏ, xe chiếm nhiều diện tích. Không đủ bằng chứng gọi mọi frame đông người hoặc rung mạnh. | Người nhỏ và chuyển động camera có thể quan trọng hơn ngoại hình; đánh giá khác giữa trước và sau rẽ. |

## Giả thuyết có thể kiểm chứng

1. Giảm confidence từ 0,30 xuống 0,15 có thể tăng coverage người nhỏ ở video_1/2/5, đồng thời tăng false detections; so sánh cùng frames và kiểm tra trực quan.
2. BoTSORT với OSNet có thể duy trì ID qua giao nhau tốt hơn ByteTrack ở video_1/4, nhưng người nhỏ/thiếu sáng ở video_2/5 có thể làm embeddings không đủ phân biệt.
3. Chuyển động camera ở video_3/5 có thể làm motion-only kém ổn định; bù camera trong BoTSORT có thể giúp nhưng cần nhìn ID trước/sau cùng người.

Các timestamp chỉ đáng tin khi có FPS gốc; video_1 có frameRate=30. Các preview dựng ở 25 FPS không chứng minh FPS dataset.


## Baseline ByteTrack



YOLO26n, 640, person, confidence 0,30, NMS IoU 0,50; detector MPS, tracker CPU. Preview có 150 frame và decode thành công. MOT có 498 dòng và 6 IDs; đây là thống kê predictions, không phải accuracy.

Contact sheet `baseline.jpg` thể hiện người áo tím đi cùng người áo đỏ phía trái giữ cùng màu/ID qua frame 1, 75, 150. Người nhỏ quanh cây và cuối quảng trường thường chưa có box/track trong những frame này; detector 640 và ngưỡng confidence có thể hạn chế coverage. Không kết luận IDSW định lượng từ contact sheet. Frame 75 = 2,47 giây từ frame đầu, frame 150 = 4,97 giây theo FPS nguồn 30.



Ở baseline, áo tím ID3 và áo đỏ ID2 giữ danh tính tại 1/75/150. Màu phụ thuộc ID, visualization không phát sinh ID mới. Notebook đã chạy end-to-end với kernel cv_robotics_lab21, ba câu đúng/sai và YOLO inference ảnh thật.

## Kết quả thí nghiệm và lựa chọn

Đã hoàn thành 51 run được ghi trong `reports/experiment_log.csv`. Manifest metadata, model hashes, Re-ID state và output hashes được lưu trong `artifacts/experiment_manifest.json`. Tất cả so sánh đầu dùng frames 1–150; verification dùng 301–450, khởi tạo tracker mới tại đầu mỗi đoạn. Video_1 bổ sung bảy run đủ 600 frames. Không so sánh ID numeric giữa hai tracker như thể đó là cùng danh tính.



Mỗi thử nghiệm đầu dùng frames 1–150. Hai nhóm tracker dùng chung detections cache ở conf=0,30/iou=0,50. Appearance encoder OSNet đã chạy thật. ID giữa hai tracker không cần bằng nhau; cần theo cùng người qua các frame trong từng run.

| Video | Quan sát hai tracker (frame 1,75,150) | Confidence (frame 50,100,150) | Quyết định tạm thời cho sweep IoU |
|---|---|---|---|
| video_1 | ByteTrack giữ áo tím ID3 và áo đỏ ID2; BoTSORT cũng giữ hai người nhưng không cải thiện coverage người nhỏ. | 0,15 giữ thêm một box ở nhóm trái tại frame 100; 0,50 dễ ngắt/tái sinh ID hơn quanh crossing. | ByteTrack, conf0,15; kiểm chứng bằng TrackEval trước kết luận cuối. |
| video_2 | Hai tracker đều giữ người đứng phải gần xe; nhiều người phía trên vẫn không có track. Không thấy lợi thế rõ ràng của Re-ID. | 0,15 giữ người áo trắng ID8 tại frame 50/100/150, trong khi 0,50 mất track đó; frame 100 có thêm người áo trắng bên phải cột đèn. | ByteTrack, conf0,15; ưu tiên continuity/coverage quan sát được. |
| video_3 | Người áo sọc ID1 và người áo xám ID2 giữ liên tục ở cả hai; người giữa có ID khác giữa tracker nhưng không chứng minh switch. | 0,15 và 0,50 đều giữ ba người tiền cảnh frame 50/100/150; không có lợi ích coverage rõ rệt. | ByteTrack, conf0,30; giữ mức trung gian vì không thấy lợi ích của thay đổi. |
| video_4 | Người áo đỏ được ID2 lúc đầu nhưng đổi ở frame 150 trong cả hai tracker; Re-ID chưa giải quyết dứt điểm che khuất. | 0,15 và 0,50 rất giống ở ba frame; người áo trắng ID5 ổn định. Không khẳng định reflection gây FP khi ảnh chưa cho thấy rõ. | ByteTrack, conf0,30; giữ mức trung gian, không chọn theo giả định Re-ID. |
| video_5 | Người áo hồng phải đường giữ ID2 ở frame1/75; cả hai vẫn bỏ nhiều người xa; frame 150 tracks tương đương. | 0,15 và 0,50 tương tự trên các frame; confidence thấp không chứng minh cải thiện người rất xa. | ByteTrack, conf0,30; kiểm tra thêm đoạn sau khi xe rẽ. |

Các quyết định là thực nghiệm trên đoạn giới hạn, không khẳng định tracker tốt nhất toàn cục. Runtime chỉ được dùng khi chất lượng trực quan tương đương. Evidence: `artifacts/comparisons/video_*_trackers.jpg`, `video_*_confidence.jpg`; baseline và scene contact sheets bổ sung ngữ cảnh.

## Kiểm chứng frames 301–450 và quyết định cập nhật

- video_1: áo tím và áo xanh giữ ID trong cả hai, nhưng đánh giá đủ 600 frame với GT thật cho BoTSORT conf0,15 HOTA/IDF1 cao hơn ByteTrack conf0,15, dù MOTA thấp hơn. Vì ưu tiên identity, chuyển sang BoTSORT và chạy sweep riêng của tracker này trước khi chốt.
- video_2: ByteTrack giữ ID8 cho người nhỏ ở phía trên qua 375–450 mà BoTSORT không giữ trong các ảnh tương ứng. Chưa thấy lợi thế Re-ID; giữ ByteTrack 0,15.
- video_3: người áo xám/túi đeo ở 301 và 375 giữ BoTSORT ID3; ByteTrack gán ID12 tại 375. Đây là lợi ích identity quan sát được, nên chuyển sang BoTSORT và bổ sung sweeps. Cả hai vẫn có fragmentation ở những người khác.
- video_4: người áo trắng giữ ByteTrack ID5 tại 301/375/450, BoTSORT chuyển từ ID5 sang ID8 tại 375. Giữ ByteTrack 0,30 vì evidence cụ thể nghiêng về continuity.
- video_5: cả hai không có track tại 301, dù ảnh có người xa; frame375 và450 có detections lại. Re-ID không giải quyết thiếu detections. Giữ ByteTrack 0,30, hạn chế rõ ở người nhỏ và chuyển động camera.

NMS IoU: các ảnh50/100/150 không cho cải thiện ổn định khi đổi0,40 hoặc0,70. video_4 có cả MOT output giống hệt ở ba ngưỡng. Các video khác có chênh lệch nhẹ về số dòng/tọa độ nhưng số dòng không phải accuracy; giữ0,50 trừ khi TrackEval video_1 cung cấp bằng chứng khác.

## Chốt cấu hình sau sweeps bổ sung

video_1 chọn BoTSORT 0,15/0,50: HOTA 27,6804 và IDF1 24,4190 cao nhất trong bảy run đủ 600 frames sau chuẩn hóa MOT. IoU0,40 đạt HOTA 27,6410/IDF1 24,3839;0,70 giảmIDF1 xuống23,9729. Conf0,30 đạtIDF1 24,2839;0,50 đạt21,0571. Chênh lệch0,15–0,30 nhỏ, không khẳng định tổng quát vượt trội.

video_3: sweeps BoTSORT conf0,15/0,30/0,50 và IoU0,40/0,50/0,70 giữ ba người tiền cảnh tương tự ở50/100/150; giữ mức trung gian0,30/0,50. Chọn tracker dựa trên continuity quan sát ở301–375, không suy diễn accuracy toàn video.

Bác bỏ những cấu hình khác theo quan sát/metric nêu trên; OCSORT/StrongSORT/DeepOCSORT chỉ chạy smoke tests và regression trên synthetic input, không có comparative experiment trên video thật và không được tuyên bố tốt/xấu hơn.


## Bảng định lượng video_1

Tất cả giá trị HOTA/MOTA/IDF1 sau đây là phần trăm, từ TrackEval chạy với GT thật trên đủ 600 frames. Các run có cùng detector/640/class, preprocessing và phạm vi; chỉ thaytracker/conf/IoU theo từng phép so sánh.

| Tracker | Conf | NMS IoU | HOTA | MOTA | IDF1 | IDSW | FP | FN |
|---|---|---|---|---|---|---|---|---|
| botsort | 0.15 | 0.40 | 27.6410 | 15.0745 | 24.3839 | 8 | 58 | 15714 |
| botsort | 0.15 | 0.50 | 27.6804 | 15.1284 | 24.4190 | 8 | 58 | 15704 |
| botsort | 0.15 | 0.70 | 27.5367 | 15.2252 | 23.9729 | 9 | 61 | 15682 |
| botsort | 0.30 | 0.50 | 27.6103 | 14.9400 | 24.2839 | 8 | 53 | 15744 |
| botsort | 0.50 | 0.50 | 24.3730 | 13.9174 | 21.0571 | 11 | 44 | 15940 |
| bytetrack | 0.15 | 0.50 | 25.6152 | 15.8280 | 23.1729 | 10 | 57 | 15573 |
| bytetrack | 0.30 | 0.50 | 25.5053 | 15.5643 | 22.9975 | 10 | 51 | 15628 |


Run final được đánh giá riêng: **HOTA 27.6804, MOTA 15.1284, IDF1 24.4190**. Nguồn: `artifacts/metrics/video_1_metrics.csv`, provenance GT/prediction SHA256 trong `video_1_evaluation.md`. DetA = 13.3834, AssA = 57.2541.


BoTSORT 0,15/0,50 cải thiện association/identity so với ByteTrack 0,15/0,50 nhưng có nhiều FN hơn nên MOTA thấp hơn. Chọn theo mục tiêu ưu tiên giữ ID; không kết luận tốt hơn trên mọi metric. Điểm tuyệt đối thấp và FN rất lớn: pipeline cố định YOLO26n 640 cùng ngưỡng khởi tạo tracker mặc định chưa bao phủ người nhỏ/che khuất. Re-ID không sinh detections bị thiếu. Đây là hạn chế thật, không sửa metric hoặc đổi model để che giấu.

## Cấu hình cuối và kết quả full sequence

| Video | Tracker | Conf | IoU | Frames | Dòng MOT | Lý do |
|---|---|---|---|---|---|---|
| video_1 | botsort | 0.15 | 0.50 | 600 | 2951 | BoTSORT conf0,15/iou0,50 có HOTA và IDF1 cao nhất trong 7 cấu hình full video_1; ưu tiên identity dù MOTA thấp hơn ByteTrack. |
| video_2 | bytetrack | 0.15 | 0.50 | 1050 | 9244 | ByteTrack giữ người áo trắng qua frame 50–150 ở conf0,15 và người xa ID8 qua375–450; Re-ID chưa có lợi thế rõ. |
| video_3 | botsort | 0.30 | 0.50 | 837 | 3865 | BoTSORT giữ ID3 của người áo xám từ301 đến375 trong khi ByteTrack đổi sang ID12; sweeps0,15/0,30/0,50 và IoU0,40/0,50/0,70 không cải thiện rõ ba người tiền cảnh; giữ0,30/0,50. |
| video_4 | bytetrack | 0.30 | 0.50 | 900 | 5493 | ByteTrack giữ người áo trắng ID5 qua301/375/450; BoTSORT đổi ID tại 375. Confidence sweep không cho lợi ích rõ và IoU outputs bằng nhau; giữ0,30/0,50. |
| video_5 | bytetrack | 0.30 | 0.50 | 750 | 1449 | Hai nhóm tương đương ở người áo hồng và đều mất người xa tại 301; confidence/IoU không cho cải thiện quan sát ổn định; chọn ByteTrack 0,30/0,50. |


Số dòng và số IDs là thống kê predictions, không phải accuracy. Video_2–5 chỉ đánh giá bằng quan sát, không có HOTA/MOTA/IDF1. Năm final run không dùng max-frames. Frame không có tracks không có dòng MOT.


MOT dùng frame/ID dương và gốc bbox (1,1). Development runs ban đầu được hiệu chỉnh left/top +1 theo tài liệu chính thức TrackEval trước đánh giá; width/height/confidence/ID không đổi. Run final xuất trực tiếp đúng convention, không áp dịch lần hai.

## Kiểm thử, đóng gói và tái lập

20 regression tests đã pass: thứ tự frames, Zip Slip, IoU edge cases, NMS overlap, năm tracker, state/ID, MOT invalid rows, TrackEval perfect/missing/ID-switch/misalignment và missing submission provenance. Tests synthetic không được dùng làm kết quả thật.


Validator kiểm tra 10 cột, finite values, bbox positive, IDs, duplicate(frame,ID), thứ tựframes, source/model/hash, selected configs, Re-ID state và toàn bộ input frames. ZIP chỉ chứa video_1.txt–video_5.txt và BAO_CAO_LAB21.md; testzip và so sánh bytes với nguồn.


Tái lập: làm theo README từ venv và requirements-lock.txt; tải/check dữ liệu, chạy notebook, tracker/conf/IoU sweeps, render comparisons, chọn cấu hình bằng evidence; chạy `LAB_DATA=... .venv/bin/python scripts/run_selected.py`, evaluate_video1.py, validate_submission.py, prepare_submission.py. Các kết quả có sẵn được kiểm tra hash trước resume, không ghi đè âm thầm.


Repository PRIVATE: https://github.com/kevindao94work/cv-robotics-lab21; owner kevindao94work; branch main; remote origin. CP0–CP5 có commit/push và đối chiếu SHA; bảng checkpoint và receipts trong reports.

## Thảo luận và kết luận

Re-ID hữu ích cho một số đoạn di chuyển/che khuất ở video_3 và cải thiện identity tổng thể ở video_1. Ởvideo_4, appearance vẫn đổi ID người áo trắng mà ByteTrack giữ; ở video_2/5, detections người nhỏ là giới hạn lớn hơn matching. Reflection và ánh sáng yếu là rủi ro cảnh quan sát được; không khẳng định chúng gây FP cụ thể nếu evidence không chứng minh.


Hai đoạn 150 frames/video không bao quát mọi tình huống. Việc chọn video_1 dựa trên cùng GT dùng đánh giá tạo nguy cơ overfit; không có tập test độc lập. Các tracker giữ cấu hình association mặc định, chỉ khảo sát detector conf/NMS IoU và tracker theo guide. Không tuyên bố tracker tốt nhất toàn cục; kết luận giới hạn ở dữ liệu và cấu hình đã chạy.
