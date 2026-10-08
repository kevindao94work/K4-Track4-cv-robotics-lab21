# Quan sát cảnh trước thí nghiệm

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
