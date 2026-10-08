# Ghi nhận lựa chọn — sau so sánh tracker và confidence

Mỗi thử nghiệm đầu dùng frames 1–150. Hai nhóm tracker dùng chung detections cache ở conf=0,30/iou=0,50. Appearance encoder OSNet đã chạy thật. ID giữa hai tracker không cần bằng nhau; cần theo cùng người qua các frame trong từng run.

| Video | Quan sát hai tracker (frame 1,75,150) | Confidence (frame 50,100,150) | Quyết định tạm thời cho sweep IoU |
|---|---|---|---|
| video_1 | ByteTrack giữ áo tím ID3 và áo đỏ ID2; BoTSORT cũng giữ hai người nhưng không cải thiện coverage người nhỏ. | 0,15 giữ thêm một box ở nhóm trái tại frame100; 0,50 dễ ngắt/tái sinh ID hơn quanh crossing. | ByteTrack, conf0,15; kiểm chứng bằng TrackEval trước kết luận cuối. |
| video_2 | Hai tracker đều giữ người đứng phải gần xe; nhiều người phía trên vẫn không có track. Không thấy lợi thế rõ ràng của Re-ID. | 0,15 giữ người áo trắng ID8 tại frame50/100/150, trong khi 0,50 mất track đó; frame100 có thêm người áo trắng bên phải cột đèn. | ByteTrack, conf0,15; ưu tiên continuity/coverage quan sát được. |
| video_3 | Người áo sọc ID1 và người áo xám ID2 giữ liên tục ở cả hai; người giữa có ID khác giữa tracker nhưng không chứng minh switch. | 0,15 và 0,50 đều giữ ba người tiền cảnh frame50/100/150; không có lợi ích coverage rõ rệt. | ByteTrack, conf0,30; giữ mức trung gian vì không thấy lợi ích của thay đổi. |
| video_4 | Người áo đỏ được ID2 lúc đầu nhưng đổi ở frame150 trong cả hai tracker; Re-ID chưa giải quyết dứt điểm che khuất. | 0,15 và 0,50 rất giống ở ba frame; người áo trắng ID5 ổn định. Không khẳng định reflection gây FP khi ảnh chưa cho thấy rõ. | ByteTrack, conf0,30; giữ mức trung gian, không chọn theo giả định Re-ID. |
| video_5 | Người áo hồng phải đường giữ ID2 ở frame1/75; cả hai vẫn bỏ nhiều người xa; frame150 tracks tương đương. | 0,15 và 0,50 tương tự trên các frame; confidence thấp không chứng minh cải thiện người rất xa. | ByteTrack, conf0,30; kiểm tra thêm đoạn sau khi xe rẽ. |

Các quyết định là thực nghiệm trên đoạn giới hạn, không khẳng định tracker tốt nhất toàn cục. Runtime chỉ được dùng khi chất lượng trực quan tương đương. Evidence: `artifacts/comparisons/video_*_trackers.jpg`, `video_*_confidence.jpg`; baseline và scene contact sheets bổ sung ngữ cảnh.

## Kiểm chứng frames 301–450 và quyết định cập nhật

- video_1: áo tím và áo xanh giữ ID trong cả hai, nhưng đánh giá đủ 600 frame với GT thật cho BoTSORT conf0,15 HOTA/IDF1 cao hơn ByteTrack conf0,15, dù MOTA thấp hơn. Vì ưu tiên identity, chuyển sang BoTSORT và chạy sweep riêng của tracker này trước khi chốt.
- video_2: ByteTrack giữ ID8 cho người nhỏ ở phía trên qua 375–450 mà BoTSORT không giữ trong các ảnh tương ứng. Chưa thấy lợi thế Re-ID; giữ ByteTrack0,15.
- video_3: người áo xám/túi đeo ở 301 và 375 giữ BoTSORT ID3; ByteTrack gán ID12 tại375. Đây là lợi ích identity quan sát được, nên chuyển sang BoTSORT và bổ sung sweeps. Cả hai vẫn có fragmentation ở những người khác.
- video_4: người áo trắng giữ ByteTrack ID5 tại301/375/450, BoTSORT chuyển từID5 sangID8 tại375. Giữ ByteTrack0,30 vì evidence cụ thể nghiêng về continuity.
- video_5: cả hai không có track tại301, dù ảnh có người xa; frame375 và450 có detections lại. Re-ID không giải quyết thiếu detections. Giữ ByteTrack0,30, hạn chế rõ ở người nhỏ và chuyển động camera.

NMS IoU: các ảnh50/100/150 không cho cải thiện ổn định khi đổi0,40 hoặc0,70. video_4 có cả MOT output giống hệt ở ba ngưỡng. Các video khác có chênh lệch nhẹ về số dòng/tọa độ nhưng số dòng không phải accuracy; giữ0,50 trừ khi TrackEval video_1 cung cấp bằng chứng khác.

## Chốt cấu hình sau sweeps bổ sung

video_1 chọn BoTSORT0,15/0,50: HOTA27,6804 và IDF124,4190 cao nhất trong bảy run đủ600frames sau chuẩn hóa MOT. IoU0,40 đạt HOTA27,6410/IDF124,3839;0,70 giảmIDF1 xuống23,9729. Conf0,30 đạtIDF124,2839;0,50 đạt21,0571. Chênh lệch0,15–0,30 nhỏ, không khẳng định tổng quát vượt trội.

video_3: sweeps BoTSORT conf0,15/0,30/0,50 và IoU0,40/0,50/0,70 giữ ba người tiền cảnh tương tự ở50/100/150; giữ mức trung gian0,30/0,50. Chọn tracker dựa trên continuity quan sát ở301–375, không suy diễn accuracy toàn video.

Bác bỏ những cấu hình khác theo quan sát/metric nêu trên; OCSORT/StrongSORT/DeepOCSORT chỉ chạy smoke tests và regression trên synthetic input, không có comparative experiment trên video thật và không được tuyên bố tốt/xấu hơn.
