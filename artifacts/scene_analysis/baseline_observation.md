# Baseline ByteTrack — video_1 frames 1–150

YOLO26n, 640, person, confidence 0,30, NMS IoU 0,50; detector MPS, tracker CPU. Preview có 150 frame và decode thành công. MOT có 498 dòng và 6 IDs; đây là thống kê predictions, không phải accuracy.

Contact sheet `baseline.jpg` thể hiện người áo tím đi cùng người áo đỏ phía trái giữ cùng màu/ID qua frame 1, 75, 150. Người nhỏ quanh cây và cuối quảng trường thường chưa có box/track trong những frame này; detector 640 và ngưỡng confidence có thể hạn chế coverage. Không kết luận IDSW định lượng từ contact sheet. Frame 75 = 2,47 giây từ frame đầu, frame 150 = 4,97 giây theo FPS nguồn 30.
