# K4 · Computer Vision & Robotics — Lab 21
## Multi-Object Tracking: Tracker Selection, Experiments & Evaluation

> **Hướng dẫn triển khai dành cho người triển khai trong thư mục local mới, CHƯA có Git repository và CHƯA có GitHub repository.** Mục tiêu không chỉ là viết code mà phải thực hiện thực nghiệm thật, tạo đủ năm file kết quả MOTChallenge và viết báo cáo tiếng Việt. Nếu tài nguyên bên ngoài không truy cập được, phải phân biệt rõ phần đã hoàn thành với phần bị chặn, không bịa đặt dữ liệu hoặc số liệu.

## 0. Vai trò, phạm vi và nguyên tắc bắt buộc

Bạn là Senior Computer Vision / MOT Research Engineer. Hãy tự xây dựng và chạy hoàn chỉnh bài lab từ một thư mục local mới chưa được khởi tạo Git và chưa có GitHub repository. Bạn chịu trách nhiệm kiến trúc, dependency management, tải và kiểm tra dữ liệu, YOLO26 inference, năm tracker, visualization, experiment design, TrackEval, kiểm thử, báo cáo và đóng gói bài nộp.

**Tự chủ:** Không hỏi người dùng các quyết định kỹ thuật, cấu hình tracker, ngưỡng confidence/IoU, phiên bản thư viện, lựa chọn thiết bị hay chiến lược thử nghiệm. Chỉ dừng để xin **ủy quyền bảo mật/xác thực** thực sự cần thiết (ví dụ quyền truy cập dataset riêng tư, GitHub authentication). Khi gặp lỗi thông thường: tái hiện → tìm nguyên nhân → sửa → regression test → tiếp tục. Nếu phụ thuộc ngoài không thể truy cập sau khi đã thử những cách hợp lệ, làm tối đa phần không phụ thuộc, ghi rõ blocker và không tuyên bố checkpoint đó đạt.

**Không được:**

- Bịa HOTA/MOTA/IDF1, tạo ground truth giả, hay gán metric cho video 2–5 khi không có nhãn.
- Xem output trên synthetic data là kết quả lab; synthetic data chỉ phục vụ test.
- Thay model cố định `yolo26n.pt`, image size 640, class person (COCO 0), hay Re-ID `osnet_x0_25_msmt17.pt` một cách âm thầm.
- Thay đổi tham số chính ngoài `--tracker`, `--conf`, `--iou` để “thắng” thí nghiệm.
- Nhầm `--iou` (NMS detector) với ngưỡng ghép track.
- Giả định tracker hỗ trợ Re-ID đồng nghĩa Re-ID đã bật; phải kiểm tra trạng thái thực tế.
- Dùng video preview 150 frame làm kết quả final full-sequence.
- Báo cáo những thí nghiệm chưa chạy như thể đã chạy.

**Git/GitHub bắt buộc:** Bắt đầu trong **thư mục local mới** người triển khai đang mở (có thể chỉ chứa file hướng dẫn này). **Không giả định đã tồn tại `.git`, remote `origin` hay repository trên GitHub.** Trước CP0, chủ động khởi tạo Git, tạo **repository GitHub mới ở chế độ PRIVATE**, kết nối `origin`, duy trì duy nhất nhánh làm việc `main`. Ở **mỗi checkpoint**, sau khi tests và acceptance pass phải commit, `git push origin main` và **xác nhận SHA trên remote trùng SHA local**. Không dừng để hỏi người dùng tên repo, owner hay visibility; chỉ được hỏi khi cần authentication/security authorization thực sự. Không force-push, không chiếm dụng repo có sẵn, không tạo lại repo trong mỗi checkpoint. Xem mục **0A** để thực hiện đầy đủ quy trình bắt buộc.

## 0A. BẮT BUỘC TRƯỚC CP0 — Tạo Git repository local và GitHub repository mới

> **Ngữ cảnh thực tế:** người triển khai đang chạy trong một **thư mục local hoàn toàn mới**. Chưa có Git history, `.git/`, GitHub repo, hay `origin`. Việc **tạo repository GitHub là một phần nhiệm vụ**, không phải thao tác tùy chọn và không được chờ người dùng tự làm.

### A. Quyết định mặc định (không hỏi người dùng)

| Thuộc tính | Giá trị |
|---|---|
| Thư mục làm việc | **Thư mục hiện người triển khai đang mở**, không tự tạo thư mục lồng khác |
| GitHub host | `github.com` |
| GitHub owner | Tài khoản người dùng hiện đang đăng nhập `gh` |
| Tên repository ưu tiên | `cv-robotics-lab21` |
| Khi tên đã bị dùng | `cv-robotics-lab21-2`, `cv-robotics-lab21-3`, … chọn tên đầu tiên thực sự khả dụng |
| Visibility | **PRIVATE**; tuyệt đối không tự đổi sang public |
| Local branch | `main` |
| Remote | `origin` |
| Commit cadence | CP0 → CP5, **mỗi CP một commit tối thiểu**, thêm corrective commits khi cần |
| Push cadence | **Ngay sau từng commit**; đối chiếu remote SHA |

Không được ghi token, SSH private key, mật khẩu hoặc credentials vào source, `.env`, logs hay Markdown. Không sửa Git configuration global trừ khi thực sự cần và được cho phép; ưu tiên cấu hình Git cấp repository.

### B. Khởi tạo local Git trong thư mục hiện tại

Chạy từ **thư mục root đang mở**, không thay đổi sang `~/Downloads` hay tự suy đoán một đường dẫn mới. Khảo sát trước:

```bash
pwd
ls -la
command -v git
git rev-parse --is-inside-work-tree 2>/dev/null || true
```

Nếu `.git/` chưa có:

```bash
git init -b main
```

Nếu Git phiên bản cũ không hỗ trợ `-b`, dùng `git init` rồi `git branch -M main` sau khi có commit phù hợp. Nếu `.git/` đã có do lần thực thi trước, **tái sử dụng đúng repository hiện hữu**, không xóa `.git/` và không khởi tạo lại. Kiểm tra nhánh hiện tại; không đổi một branch đang chứa thay đổi của người dùng nếu chưa hiểu trạng thái.

Tạo `.gitignore` **trước khi chạy `git add`**. Phải loại trừ tối thiểu:

```gitignore
# Real dataset, archives and weights
data/
weights/
*.pt
*.pth
*.onnx

# Third-party source and local environment
TrackEval/
.venv/
venv/
.env
.env.*
__pycache__/
.pytest_cache/
.ipynb_checkpoints/
.DS_Store

# Large generated videos / caches
*.mp4
*.avi
*.mov
*.zip
runs/experiments/
runs/thu_nhanh/
```

**Lưu ý:** `.gitignore` cần được thiết kế để **vẫn có thể version-control năm file kết quả `.txt`, báo cáo, cấu hình và bằng chứng phù hợp**, nhưng không stage dataset, model checkpoints hoặc secrets. `submission.zip` là artifact local, **không bắt buộc commit** nếu lớn; phải thực sự tạo ra và giữ để nộp.

### C. Cài đặt/kiểm tra GitHub CLI và tài khoản

```bash
command -v gh || true
gh --version
```

Nếu thiếu `gh`, tự cài từ kênh chính thức phù hợp hệ điều hành. Trên macOS có Homebrew:

```bash
brew install gh
```

Trên hệ điều hành khác, sử dụng package manager/chỉ dẫn phát hành chính thức. **Không** dùng script không rõ nguồn, không yêu cầu người dùng quyết định cách cài nếu tự thực hiện được.

Kiểm tra đăng nhập:

```bash
gh auth status --hostname github.com
```

Nếu chưa đăng nhập hoặc thiếu scope/quyền tạo repository, đây là trường hợp **được phép dừng chỉ để xin xác thực/ủy quyền**. Ưu tiên lệnh browser login chính thức:

```bash
gh auth login --hostname github.com --web --git-protocol https
```

Chỉ yêu cầu người dùng hoàn thành bước cấp quyền OAuth trên trình duyệt nếu cần; **không yêu cầu họ gửi token hay mật khẩu qua chat**. Sau đó:

```bash
gh auth status --hostname github.com
gh auth setup-git --hostname github.com
```

Xác định đúng GitHub login (không tự đoán tên tài khoản):

```bash
GH_OWNER="$(gh api user --jq '.login')"
printf 'GitHub account: %s\n' "$GH_OWNER"
```

Nếu thiếu `user.name` / `user.email` cho Git commits, thiết lập **chỉ tại repo local** bằng GitHub login và GitHub noreply address lấy từ account ID, không ghi email riêng tư một cách không cần thiết:

```bash
GH_USER_ID="$(gh api user --jq '.id')"
git config user.name >/dev/null 2>&1 || git config user.name "$GH_OWNER"
git config user.email >/dev/null 2>&1 || git config user.email "${GH_USER_ID}+${GH_OWNER}@users.noreply.github.com"
```

### D. Chọn tên an toàn và tạo repository GitHub PRIVATE

Tên ưu tiên là `cv-robotics-lab21`. Dùng GitHub API/CLI xác minh repo name có còn trống không. Nếu `$GH_OWNER/cv-robotics-lab21` đã tồn tại, **không push vào đó, không xóa, không ghi đè**, mà chọn hậu tố tăng dần (`-2`, `-3`, ...). Phải phân biệt **HTTP 404 = không tồn tại** với lỗi mạng, authentication, rate limit hoặc permission; không coi mọi lỗi CLI là dấu hiệu tên còn trống. Retry các lỗi tạm thời có giới hạn.

Nếu chưa có `origin`, và repo name đã được xác định là chưa dùng:

```bash
GH_REPO_NAME="cv-robotics-lab21"  # thay bằng tên hậu tố nếu bị trùng
gh repo create "${GH_OWNER}/${GH_REPO_NAME}" \
  --private \
  --source=. \
  --remote=origin \
  --description "Computer Vision Lab 21: Multi-Object Tracking experiments"
```

**Không thêm** `--public`, `--clone` hay `--add-readme`; dự án local đang tồn tại, nên không clone thành một thư mục khác và không tạo remote README gây xung đột lịch sử. **Không dùng `--push` trước khi CP0 tạo commit hợp lệ**.

Nếu lệnh tạo repo lỗi nhưng GitHub repository vừa được tạo thành công (ví dụ kết nối bị ngắt sau bước tạo), xác minh bằng `gh repo view` trước khi retry; liên kết lại `origin` với chính repo đó thay vì tạo repo trùng lặp. Nếu `origin` đã tồn tại từ lần chạy trước, xác minh nó trỏ đúng repository mới do workflow này tạo và repo đó thuộc đúng owner, không sửa remote ngoài phạm vi dự án một cách mù quáng.

Kiểm tra:

```bash
git remote -v
git branch --show-current
gh repo view "${GH_OWNER}/${GH_REPO_NAME}" \
  --json nameWithOwner,visibility,url
```

**Bắt buộc kiểm tra `visibility == PRIVATE`, owner đúng, tên đúng.** Nếu chưa có commit, chưa có `refs/heads/main` trên remote là bình thường; remote branch sẽ được tạo khi push CP0.

### E. Push đầu tiên sau CP0 và push xác minh sau mỗi checkpoint

Sau khi acceptance của CP0 đạt, tạo commit theo mục CP0 rồi chạy:

```bash
git push -u origin main
```

Với CP1–CP5 và mọi corrective commit:

```bash
git push origin main
```

**Không coi commit cục bộ là đã push thành công.** Sau mỗi push, xác minh:

```bash
LOCAL_SHA="$(git rev-parse HEAD)"
REMOTE_SHA="$(git ls-remote origin refs/heads/main | awk '{print $1}')"
test -n "$REMOTE_SHA" && test "$LOCAL_SHA" = "$REMOTE_SHA"
```

Nếu SHA không trùng hoặc push trả lỗi, kiểm tra credentials, URL `origin`, permissions, mạng và remote state; sửa rồi thử lại. Không force-push; nếu non-fast-forward, fetch và xử lý lịch sử một cách an toàn. Không tự ý rewrite/delete công việc trên GitHub.

Ở các checkpoint, trước `git add`, kiểm tra `.gitignore` và những file sắp stage để không vô tình đẩy dữ liệu lớn hoặc secrets. Sau khi stage, kiểm tra `git diff --cached --name-only` và `git diff --cached --check`. Nếu changeset hoàn toàn trống, chỉ tạo commit khi có thay đổi checkpoint thực sự; không tạo empty commit giả.

### F. Chính sách lỗi và tiếp tục làm việc

- **Yêu cầu xác thực/OAuth/authorization**: đây là lý do hợp lệ duy nhất để xin can thiệp người dùng. Sau khi xác thực, tự tiếp tục toàn bộ công việc.
- **Lỗi thông thường như `gh` chưa cài, tên repo đã dùng, PATH lỗi, timeout, network transient, push bị từ chối do trạng thái lịch sử**: tự chẩn đoán, sửa hoặc retry; không đặt câu hỏi kỹ thuật.
- **Mạng/GitHub outage kéo dài không giải quyết được**: không tuyên bố đã tạo/push repo. Tiếp tục các công việc local có thể làm, ghi `REMOTE_PENDING`, tự retry tạo remote/push ở mỗi checkpoint và cuối nhiệm vụ; mọi checkpoint có thể commit local nhưng chỉ được đánh dấu `PUSHED` khi SHA đã xác minh. Không xem đây là hoàn thành GitHub deliverable.
- **Repo vẫn PRIVATE**. Không nới visibility để workaround permissions. Không dùng repo thuộc người khác, không overwrite repository hiện có.

### G. Tiêu chí hoàn thành GitHub setup

- [ ] người triển khai đang làm việc ngay trong thư mục local mới được cung cấp.
- [ ] Đã `git init` với nhánh `main` (hoặc xác minh trạng thái đã khởi tạo từ lần chạy trước).
- [ ] `.gitignore` ngăn datasets, secrets, weights và môi trường local lọt vào Git.
- [ ] GitHub CLI đã cài và tài khoản được xác thực hợp lệ.
- [ ] Có **repository mới** trên GitHub, dưới đúng tài khoản đăng nhập.
- [ ] Repository là **PRIVATE**, không ghi đè repo khác.
- [ ] `origin` trỏ đúng repo vừa tạo.
- [ ] Sau CP0, `main` được push và commit SHA đã đối chiếu với GitHub.
- [ ] CP1–CP5 sẽ tuân thủ cùng quy trình push + verify.

## 1. Mục tiêu lab và tiêu chí lựa chọn

Câu hỏi nghiên cứu: **Tracker nào giữ ID ổn định hơn trong từng điều kiện cảnh quay, và vì sao?**

| Video | Đặc điểm | Đánh giá cho phép |
|---|---|---|
| `video_1` | Quảng trường ban ngày, camera tĩnh, mật độ vừa | Quan sát + HOTA, MOTA, IDF1 với nhãn thực |
| `video_2` | Phố đêm, camera tĩnh trên cao, rất đông | Quan sát trực quan, không ghi HOTA/MOTA/IDF1 |
| `video_3` | Camera di chuyển, ảnh nhỏ, ít FPS | Quan sát trực quan |
| `video_4` | Camera tiến tới trong nhà, phản chiếu kính | Quan sát trực quan |
| `video_5` | Camera trên xe buýt, giao lộ đông, rung lắc | Quan sát trực quan |

Tracker **motion-oriented**: `bytetrack`, `ocsort`. Tracker **appearance/Re-ID capable**: `botsort`, `strongsort`, `deepocsort`. Phải thử tối thiểu một tracker thuộc mỗi nhóm trên **mỗi video**, và với tracker appearance phải xác nhận thực sự dùng Re-ID.

Giữ cố định:

```text
Detector: yolo26n.pt
Image size: 640
Class: person (COCO class 0)
Re-ID: osnet_x0_25_msmt17.pt
```

Tham số khảo sát:

```python
CONF_VALUES = [0.15, 0.30, 0.50]
IOU_VALUES = [0.40, 0.50, 0.70]
BASELINE = dict(conf=0.30, iou=0.50)
```

Chỉ thay đổi **một biến tại một thời điểm**. `--conf` là ngưỡng confidence detector; `--iou` là IoU threshold của NMS detector, **không phải** threshold association của tracker. Nếu YOLO26 dùng inference NMS-free theo mặc định, xác minh và cấu hình inference path phù hợp để `--iou` thực sự điều khiển NMS. Không áp NMS trùng lặp tùy tiện và không tạo khác biệt nhân tạo khi dự đoán không có box chồng lấp.

**Deliverables tối thiểu:**

```text
runs/nop_bai/video_1.txt
runs/nop_bai/video_2.txt
runs/nop_bai/video_3.txt
runs/nop_bai/video_4.txt
runs/nop_bai/video_5.txt
reports/BAO_CAO_LAB21.md
submission.zip
```

## 2. Kiến trúc repository

Tạo cấu trúc gọn gàng (chỉ thêm module thật sự cần dùng):

```text
.
├── README.md
├── IMPLEMENTATION_GUIDE.md
├── environment.yml
├── pyproject.toml
├── requirements-lock.txt
├── .gitignore
├── configs/
│   ├── default.yaml
│   └── experiments.yaml
├── scripts/
│   ├── setup_environment.py
│   ├── download_data.py
│   ├── check_data.py
│   ├── inspect_scenes.py
│   ├── run_tracking.py
│   ├── run_experiments.py
│   ├── evaluate_video1.py
│   ├── validate_submission.py
│   └── prepare_submission.py
├── src/lab21/
│   ├── __init__.py
│   ├── config.py
│   ├── dataset.py
│   ├── detector.py
│   ├── trackers.py
│   ├── pipeline.py
│   ├── mot_writer.py
│   ├── visualization.py
│   ├── metrics.py
│   ├── experiments.py
│   ├── evaluation.py
│   └── reporting.py
├── notebooks/on_tap_metrics.ipynb
├── tests/
│   ├── test_dataset.py
│   ├── test_detector.py
│   ├── test_trackers.py
│   ├── test_pipeline.py
│   ├── test_mot_writer.py
│   ├── test_metrics.py
│   ├── test_evaluation.py
│   └── test_submission.py
├── reports/
│   ├── BAO_CAO_LAB21.md
│   ├── experiment_log.csv
│   └── selected_configs.json
├── artifacts/
│   ├── scene_analysis/
│   ├── comparisons/
│   └── metrics/
├── data/
├── weights/
├── runs/
│   ├── thu_nhanh/
│   ├── experiments/
│   └── nop_bai/
└── TrackEval/
```

Trong `.gitignore` bỏ dataset, weights, video dung lượng lớn, environment, cache, clone TrackEval, temporary results. **Giữ lại** source, configs, tests, notebook, reports, logs, những hình ảnh minh họa cần thiết và năm final `.txt` nếu kích thước phù hợp; nếu file lớn, đảm bảo chúng nằm trong submission artifact, không mất file nộp.

## 3. CP0 — Bootstrap môi trường, dependencies và smoke tests (sau GitHub setup 0A)

### Bước 1: Khảo sát hệ thống

**Trước khi bắt đầu CP0, thực hiện toàn bộ mục 0A:** xác minh `.git/`, branch `main`, `origin` và GitHub repository PRIVATE mới đã được tạo. Nếu repo chưa tạo vì quyền truy cập, chỉ yêu cầu authorization như hướng dẫn ở 0A.

Kiểm tra OS, CPU architecture, RAM, free disk, Python, Git, Conda, CUDA, MPS và GPU. Ví dụ:

```bash
python --version
git status
git remote -v
conda --version
python -c 'import torch; print(torch.__version__, torch.cuda.is_available(), torch.backends.mps.is_available())'
```

Ưu tiên `CUDA → MPS → CPU` nhưng **chỉ dùng backend sau smoke test thành công**. Trên Apple Silicon, MPS có thể không tương thích với một số thao tác Re-ID/tracker; cho phép chạy thành phần đó trên CPU. Ghi lại device thực tế của detector và Re-ID riêng biệt khi cần.

### Bước 2: Tạo môi trường

Tạo `environment.yml` khởi tạo:

```yaml
name: cv_robotics_lab21
channels:
  - conda-forge
  - defaults
dependencies:
  - python=3.11
  - pip
  - git
  - ffmpeg
  - pip:
      - numpy
      - scipy
      - pandas
      - matplotlib
      - pillow
      - opencv-python-headless
      - ultralytics
      - boxmot
      - gdown
      - pyyaml
      - tqdm
      - pytest
      - ipykernel
      - nbformat
      - nbclient
      - nbconvert
      - jupyter
      - imageio-ffmpeg
```

Đây là **starting point**, không phải pinned final versions. Cài PyTorch đúng platform. Nếu có Conda:

```bash
conda env create -f environment.yml
conda activate cv_robotics_lab21
pip install -e .
git clone https://github.com/JonathonLuiten/TrackEval.git TrackEval
pip install -e TrackEval/
```

Nếu không có Conda, dùng Python venv với dependencies tương thích, không bắt người dùng cài Conda. Cần bảo đảm `pyproject.toml` hợp lệ. Ghi TrackEval commit hash. Khi cài xong chạy `pip freeze > requirements-lock.txt`, ghi Python/PyTorch/Ultralytics/BoxMOT/TrackEval versions và model hash vào environment metadata.

### Bước 3: Nghiên cứu API thực tế và kiểm thử

```python
from ultralytics import YOLO
import boxmot
import trackeval
```

Kiểm tra API thực tế của BoxMOT **đã cài**, không sao chép ví dụ cũ và giả định output `tracker.update` có shape cố định. Xây adapter phù hợp. Tải/load `yolo26n.pt`, thử tạo ByteTrack và tracker Re-ID, chạy 1 frame synthetic/ảnh hợp lệ, kiểm tra OpenCV video writer chạy headless, notebook kernel và TrackEval import. Khóa phiên bản sau khi thành công.

**Acceptance CP0:** Repository GitHub PRIVATE mới, remote `origin` đúng, branch `main` đúng;  environment tái tạo được; YOLO26, BoxMOT, TrackEval load; motion tracker và Re-ID tracker smoke test pass; device lựa chọn hợp lệ; codec video test pass; lock file, README và tests có thật.

```bash
pytest -v
git add .
git commit -m "CP0: Bootstrap tracking environment and project structure"
git push -u origin main  # lần push đầu tiên; sau đó verify LOCAL_SHA == REMOTE_SHA theo mục 0A
```

## 4. CP1 — Data validation, scene understanding, metrics notebook

### Bước 1: Tải gói dữ liệu thật

Nguồn chính:

```text
https://drive.google.com/file/d/1UeVPQd6j5pSzxoJDcKJrerT9SL3vJLDt/view?usp=sharing
Google Drive ID: 1UeVPQd6j5pSzxoJDcKJrerT9SL3vJLDt
```

Tạo `scripts/download_data.py`: tìm cache/local zip có sẵn; nếu thiếu, tải bằng `gdown` hoặc cơ chế Drive hợp lệ; hỗ trợ retry/resume thích hợp; xác nhận file thực sự là archive ZIP (không phải HTML lỗi); giải nén an toàn, chống Zip Slip; phát hiện dataset root chứa trực tiếp `video_1`…`video_5`; không ghi đè dữ liệu hợp lệ. Thử:

```bash
gdown --fuzzy "https://drive.google.com/file/d/1UeVPQd6j5pSzxoJDcKJrerT9SL3vJLDt/view" -O data/data_lab21.zip
export LAB_DATA="$(pwd)/data/lab_data"
python scripts/check_data.py --lab-data-root "$LAB_DATA"
```

Nếu lỗi quota/quyền, thử đường dẫn local, cache, download hợp lệ khác; nếu cần quyền truy cập protected resource thì yêu cầu user authorization. **Không lấy dataset khác thay thế**. Việc thử fetch bằng Drive connector trong cuộc trò chuyện trước không thành công; điều đó không chứng minh URL công khai bị hỏng, nên người triển khai phải tự thử runtime download.

### Bước 2: Xác thực dữ liệu

`LAB_DATA` phải trỏ tới thư mục **chứa trực tiếp** `video_1`…`video_5`; từng video có `img1/*.jpg` hợp lệ. `video_1` có ground truth thật; các video còn lại không được suy diễn là có nhãn. Cấu trúc folder `preview`, `gt`, `seqinfo.ini` tùy thuộc archive thực: **không** giả định trước.

Tạo `scripts/check_data.py` nhận `--lab-data-root` hoặc env `LAB_DATA`; kiểm tra:

- Đủ năm video; `img1` không rỗng; file `.jpg` đọc bằng OpenCV.
- Frame naming/order numeric, duplicates, corruption, số frame, dimensions, FPS nếu metadata đáng tin cậy.
- Preview availability; file ảnh gốc; nhãn `video_1`, frame mapping, class IDs, bounding box conventions, GT coverage/ignored regions.
- Nếu nhãn chỉ bao phủ một phần, phải ghi rõ để đánh giá đúng frame phạm vi; không coi missing annotations là negative ground truth.
- Trả về terminal summary + `artifacts/scene_analysis/dataset_metadata.json`; fail rõ khi dữ liệu không hợp lệ.

### Bước 3: Xem và phân tích năm cảnh

Tạo `scripts/inspect_scenes.py`: ưu tiên `preview/video_{1..5}.mp4`; nếu thiếu thì dựng từ frames. Trích các frames đại diện, contact sheets `artifacts/scene_analysis/video_1.jpg`…`video_5.jpg` và viết `scene_analysis.md` mô tả mật độ người, ánh sáng, che khuất, kích thước người, chuyển động camera, reflections, motion blur. Không chỉ chép lại mô tả đề; phân biệt dữ kiện nhìn thấy với nhận định từ guide.

Viết ít nhất **hai giả thuyết có thể kiểm chứng**, ví dụ Re-ID có thể giúp khi đông người nhưng khó phân biệt ngoại hình trong thiếu sáng; low FPS làm association dựa vào chuyển động kém; camera shake gây fragmentations. Ghi rõ là giả thuyết, chưa phải kết quả.

### Bước 4: `notebooks/on_tap_metrics.ipynb`

Tạo notebook có thể chạy end-to-end trên kernel `cv_robotics_lab21` với `LAB_DATA` từ môi trường. Gồm:

1. Detector vs tracker: YOLO sinh box/confidence, tracker mới gắn ID thời gian.
2. IoU và function `box_iou` có unit tests edge cases; giải thích `--iou` là NMS detector.
3. Công thức MOTA: $MOTA=1-(FN+FP+IDSW)/GT$; có thể âm.
4. Công thức IDF1: $IDF1=2IDTP/(2IDTP+IDFP+IDFN)$.
5. HOTA: $HOTA_\alpha=\sqrt{DetA_\alpha AssA_\alpha}$, tổng hợp theo nhiều threshold; không phải trung bình MOTA và IDF1.
6. Ba True/False và giải thích: “YOLO box tự có tracking ID” = False; “`--iou` là ngưỡng ghép tracker” = False; “HOTA xét detection và association” = True. Nếu có notebook chính thức trong dataset thì **ưu tiên giữ và hoàn thành** notebook chính thức thay vì thay thế tùy tiện.
7. YOLO26n inference trên ảnh `video_1`, hiển thị ảnh gốc, box người + confidence, giải thích chưa có ID.

Chạy notebook qua `nbclient`/`nbconvert`. Không xem notebook là pass nếu chỉ có cell code nhưng chưa thực thi.

**Acceptance CP1:** Dữ liệu thật được tải và kiểm tra; `video_1` GT được nhận diện; năm scene analyses/contact sheets; notebook thực thi thành công; 3 True/False; YOLO visualization; ít nhất 2 giả thuyết; `pytest tests/test_dataset.py tests/test_metrics.py -v` pass.

```bash
git add .
git commit -m "CP1: Validate dataset and complete scene and metric analysis"
git push origin main  # bắt buộc; kiểm tra remote SHA theo mục 0A
```

## 5. CP2 — Build detector→tracker→MOT→video pipeline; ByteTrack baseline

### Bước 1: YOLO26 detector adapter (`src/lab21/detector.py`)

Load **đúng** `YOLO("yolo26n.pt")`, `imgsz=640`, `classes=[0]`. API thống nhất `detect(frame, conf, iou) -> [x1,y1,x2,y2,confidence,class_id]`. Kiểm tra box validity, coords, confidence range, finite values và class person. Chú ý YOLO26 có NMS-free inference path: kiểm tra inference mode và chắc chắn `--iou` truyền vào NMS detector có ý nghĩa. Test bằng input crafted có overlapping boxes ở đường xử lý NMS thích hợp; không yêu cầu real video phải có khác biệt khi các boxes không chồng lấp. Không áp hai vòng NMS tùy tiện.

### Bước 2: Tracker factory (`src/lab21/trackers.py`)

Hỗ trợ `bytetrack`, `ocsort`, `botsort`, `strongsort`, `deepocsort`. API thống nhất `create_tracker(name,device,reid_model)` và `update_tracker(tracker,detections,frame)`; normalize kết quả `[x1,y1,x2,y2,track_id,confidence,class_id]` hoặc dataclass có field tương đương. **Dựa vào API BoxMOT đang cài**: tìm hiểu expected detection shapes, dtype, frame, output layout, internal Re-ID switch. Re-ID sử dụng đúng `osnet_x0_25_msmt17.pt`; verify checkpoint/model profile, bật appearance mode thực sự. Lưu `reid_enabled`, model path/hash, device trong metadata. Không bật Re-ID cho motion-only trackers; mỗi sequence khởi tạo tracker mới/reset state, không rò ID/state giữa videos. Xử lý empty detections/tracks và model download/checkpoint failure minh bạch.

### Bước 3: Pipeline (`src/lab21/pipeline.py`)

```text
Read frame in correct order
  -> validate frame
  -> YOLO detections
  -> normalize boxes
  -> update tracker state
  -> normalize tracks
  -> write MOT rows
  -> render preview optionally
  -> next frame
```

Giữ tracker instance qua toàn bộ video. Không bỏ frame lỗi âm thầm; nếu lỗi, phát hiện và ghi log. Không phát sinh ID ở visualization. Không load toàn bộ video vào RAM nếu không cần. Cho phép reuse detector cache **chỉ** khi cùng model/hash, preprocessing, `conf`, `iou`, image size.

### Bước 4: MOTChallenge output (`src/lab21/mot_writer.py`)

Mỗi dòng đúng 10 trường, không header:

```text
frame,id,left,top,width,height,conf,-1,-1,-1
1,1,120.50,80.20,45.00,130.00,0.92,-1,-1,-1
```

Trong file thật không ghi dòng chữ header minh họa trên. Frame IDs 1-based **phải align GT**; positive integer track ID; finite coordinates; width/height positive; frame order; no duplicate `(frame,track_id)`. Không ghi track giả cho frame không có người; một frame không có output là chấp nhận được. Bounding boxes đo pixel và khớp quy ước TrackEval.

### Bước 5: Visualization (`src/lab21/visualization.py`)

Vẽ box, `ID: n`, deterministic stable color theo ID; không random màu theo frame. Giữ aspect ratio, OpenCV writer chạy headless với codec phù hợp; tùy chọn overlay confidences. Preview là bằng chứng, không thay kết quả `.txt`.

### Bước 6: CLI (`scripts/run_tracking.py`)

Phải hỗ trợ `--source`, `--seq-name`, `--tracker`, `--conf`, `--iou`, `--out`, `--save-video`, `--max-frames`, `--device`. Lệnh bắt buộc:

```bash
python scripts/run_tracking.py \
  --source "$LAB_DATA/video_1/img1" \
  --seq-name video_1 \
  --tracker bytetrack --conf 0.3 --iou 0.5 \
  --out runs/thu_nhanh --save-video --max-frames 150
```

Tạo:

```text
runs/thu_nhanh/video_1.txt
runs/thu_nhanh/video_1_preview.mp4
runs/thu_nhanh/video_1_metadata.json
```

Metadata cần `sequence`, tracker, conf, iou, model, img size, frames processed, source/manifest, device, version info, Re-ID state và time. Nếu video <150 frame thì xử lý tất cả và ghi nhận.

### Bước 7: Baseline analysis

Quan sát preview: chọn một đoạn ID giữ ổn định hoặc một lỗi **thực sự nhìn thấy** (identity switch, fragmentation, miss). Trích frame/timestamp minh họa; không bắt buộc bịa lỗi. Chạy unit/integration tests bằng dữ liệu thật.

**Acceptance CP2:** CLI chạy; YOLO26/person class/NMS đúng; ByteTrack outputs; 150 frames nếu có; valid MOT file + playable video; colors stable; no NaN/duplicate IDs per frame; baseline observation; `pytest tests/test_detector.py tests/test_trackers.py tests/test_pipeline.py tests/test_mot_writer.py -v` pass.

```bash
git add .
git commit -m "CP2: Implement tracking pipeline and validate ByteTrack baseline"
git push origin main  # bắt buộc; kiểm tra remote SHA theo mục 0A
```

## 6. CP3 — Compare trackers, tune detector thresholds, select five configurations

### Bước 1: Controlled experiments

Giữ detector `yolo26n.pt`, 640, person-only; mặc định `conf=0.30`, `iou=0.50`. Với **mỗi** video:

1. **A — Tracker comparison:** Motion (`bytetrack` hoặc `ocsort`) vs appearance (`botsort`, `strongsort`, hoặc `deepocsort` với Re-ID confirmed ON). Cùng frame range, `conf`, `iou` và detector output; thêm tracker thứ ba nếu cần.
2. **B — Confidence sweep:** Giữ tracker và `iou=0.50`, thử `conf ∈ {0.15,0.30,0.50}`.
3. **C — NMS IoU sweep:** Giữ tracker và confidence đã chọn, thử `iou ∈ {0.40,0.50,0.70}`.
4. **D — Verification:** Dùng một đoạn khác hoặc toàn sequence để kiểm tra quyết định nếu tài nguyên cho phép.

**Chỉ thay đổi một tham số một lần**. Không phải chạy toàn bộ Cartesian product nếu không cần. Khi phần cứng chậm, thử đoạn đại diện có cùng frame ranges giữa các cấu hình, nhưng không bỏ yêu cầu thử hai nhóm tracker trên bất kỳ video nào và phải tạo full-sequence outputs sau cùng.

### Bước 2: Runner có thể resume (`scripts/run_experiments.py`)

Tạo experiment IDs duy nhất và thư mục riêng:

```text
runs/experiments/video_1/bytetrack_conf030_iou050/
  tracks.txt
  preview.mp4
  metadata.json
runs/experiments/video_1/botsort_conf030_iou050/
...
```

Các chức năng: queue configs, chạy tuần tự để tránh OOM, record status, frame range, timings, FPS, real device, model hashes, Re-ID state, resume safe; không tự ghi đè kết quả cũ; retry những failures có thể khắc phục. Detection cache chỉ được reuse nếu config/model/preprocessing trùng chính xác.

`reports/experiment_log.csv` phải có ít nhất: `video, experiment_id, tracker, conf, iou, frames, frame_range, reid_enabled, device, elapsed_seconds, fps, observations, decision, reason, status`.

### Bước 3: Visual comparison

Render side-by-side **đồng bộ cùng frame** (ví dụ ByteTrack | StrongSORT), có tiêu đề tracker và IDs rõ. Xuất minh chứng trong `artifacts/comparisons/`; không chỉnh sửa kết quả để trông đẹp hơn. Xem track consistency (ID trước/sau che khuất, crossing), misses, FP, fragmentation, reflections, camera motion robustness; nên nêu frame ranges/timestamps cụ thể để kiểm chứng.

Tập trung:

- `video_1`: ID consistency, fragmentation, FP/FN, hỗ trợ bởi TrackEval trong CP4.
- `video_2`: đông, ánh sáng yếu, occlusion, người nhỏ; **không giả định** Re-ID tốt hơn.
- `video_3`: camera movement, ảnh nhỏ, low FPS, between-frame displacement.
- `video_4`: scale change và reflections qua kính, detections giả.
- `video_5`: bus-mounted shake, motion blur, crowded intersection, ID continuity.

### Bước 4: Selection policy

Ưu tiên (1) ID consistency, (2) coverage vs false positives, (3) occlusion recovery, (4) robustness giữa các đoạn, (5) runtime nếu chất lượng tương đương. Từng video phải có danh sách cấu hình bị loại và **lý do quan sát được**. Không chọn chỉ dựa FPS hay lý thuyết. Có thể dùng TrackEval với `video_1` để củng cố/quyết định, và nếu CP4 cần thay config `video_1`, quay lại re-run full-sequence + update selected configs trước final report.

### Bước 5: Full-sequence results

Sau khi chọn, chạy **không có `--max-frames`** từng video vào `runs/nop_bai`:

```bash
python scripts/run_tracking.py \
  --source "$LAB_DATA/video_2/img1" \
  --seq-name video_2 \
  --tracker strongsort --conf 0.30 --iou 0.50 \
  --out runs/nop_bai --save-video
```

Đây chỉ là ví dụ; phải thay bằng cấu hình được chứng minh. Lặp đủ `video_1`…`video_5`. Tránh accidentally overwriting khác video. Lưu `reports/selected_configs.json` với mỗi video gồm `tracker, conf, iou, reason, evidence, full_sequence_metadata`. Không để `null`/placeholder cuối cùng.

**Acceptance CP3:** Với **mọi** video có motion vs real Re-ID comparison, confidence & IoU one-variable comparisons, side-by-side visual evidence, experiment logs, rejected configs/reasons, selected configs, output full-sequence valid files 1–5; tests pass; không có giả số liệu.

```bash
git add .
git commit -m "CP3: Complete tracker comparison and full-sequence tracking"
git push origin main  # bắt buộc; kiểm tra remote SHA theo mục 0A
```

## 7. CP4 — TrackEval: quantitative evaluation of `video_1` only

### Bước 1: Inspect GT

Xác minh đường dẫn nhãn, detection/track columns, coordinate system, 1-based indexing, GT classes, ignore regions, per-frame coverage, sequence length. Nếu cần converter, triển khai đúng nguồn; không tự tạo GT từ predictions. Nếu GT là subset, evaluate đúng annotated range và ghi rõ giới hạn. Đảm bảo predictions và GT align về frame, bbox và class.

### Bước 2: TrackEval directory

Dựng layout chuẩn tương thích phiên bản TrackEval đang dùng, ví dụ:

```text
evaluation/trackeval_data/
├── gt/mot_challenge/
│   ├── LAB21-train/video_1/
│   │   ├── gt/gt.txt
│   │   └── seqinfo.ini
│   └── seqmaps/LAB21-train.txt
└── trackers/mot_challenge/LAB21-train/selected/data/video_1.txt
```

Sequence map:

```text
name
video_1
```

Không coi layout minh họa là tuyệt đối nếu installed TrackEval version khác. Đọc docs/CLI `get_default_dataset_config`, cấu hình chính xác `GT_FOLDER`, `TRACKERS_FOLDER`, `BENCHMARK`, `SPLIT_TO_EVAL`, sequence mappings và preprocess flags phù hợp với annotations.

### Bước 3: `scripts/evaluate_video1.py`

Dùng TrackEval metrics `HOTA`, `CLEAR`, `Identity`; extract **HOTA, MOTA, IDF1** và có thể `DetA, AssA, IDSW, FP, FN`. Nhất quán scale/units (TrackEval thường biểu diễn phần trăm trong báo cáo), MOTA có thể âm. Lưu machine-readable `artifacts/metrics/video_1_metrics.csv` và `artifacts/metrics/video_1_evaluation.md`. Đánh giá selected `runs/nop_bai/video_1.txt`, và khi có các experiment outputs thì so sánh hợp lệ để hỗ trợ lựa chọn.

### Bước 4: Evaluator tests

Synthetic miniature ground truth/test predictions chỉ cho regression test: perfect predictions → scores tối đa; missing detections ảnh hưởng metrics; identity switch được ghi nhận; invalid row rejected; frame mismatch detected. Không đưa synthetic scores vào báo cáo thí nghiệm thực.

### Bước 5: Phân tích

So sánh detection vs association: MOTA nhạy FP/FN/IDSW; IDF1 đo identity; HOTA cân bằng detection/association. Nếu tracker có MOTA cao nhưng IDF1 thấp, thảo luận trade-off, không kết luận tuyệt đối. **Không chạy hoặc ghi HOTA/MOTA/IDF1 cho video 2–5 vì lab không cung cấp GT.**

**Acceptance CP4:** Real GT đúng; TrackEval chạy không báo lỗi; tests/GT alignment pass; actual HOTA/MOTA/IDF1 recorded; có table so sánh nếu thử >1 config; evaluation report; không có metric giả video khác.

```bash
git add .
git commit -m "CP4: Evaluate video 1 using HOTA MOTA and IDF1"
git push origin main  # bắt buộc; kiểm tra remote SHA theo mục 0A
```

## 8. CP5 — Vietnamese report, submission validator and ZIP

### Bước 1: Viết báo cáo `reports/BAO_CAO_LAB21.md`

Sử dụng tiếng Việt, gồm:

1. Giới thiệu và mục tiêu.
2. Detector vs tracker; ByteTrack/OCSORT/BoTSORT/StrongSORT/DeepOCSORT; Re-ID; occlusion/ID switches.
3. IoU, NMS detector, confidence, MOTA/IDF1/HOTA và công thức đúng.
4. Môi trường thật, device, versions, pretrained model, dataset metadata, setup reproducibility.
5. Phân tích năm cảnh và **giả thuyết trước thí nghiệm**.
6. Thiết kế thí nghiệm kiểm soát (one variable at a time, same frames).
7. Baseline ByteTrack `video_1` 150-frame và quan sát thật.
8. Motion vs appearance comparisons, conf and NMS IoU experiments.
9. Mỗi video: cảnh, tracker/conf/iou đã thử, evidence, lỗi/ưu điểm, rejected options, selected config, limitations.
10. Bảng HOTA/MOTA/IDF1 **chỉ video_1**, nguồn là TrackEval thực.
11. Tổng hợp cấu hình cuối cùng cho cả năm video.
12. Thảo luận trade-offs, khi nào Re-ID hữu ích/không, camera motion, crowded scenes, reflections, low light.
13. Hạn chế, kết luận, tài liệu tham khảo.

Bảng selected configs:

| Video | Tracker | Conf | IoU | Bằng chứng lựa chọn |
|---|---|---|---|---|
| video_1 | Giá trị thực nghiệm | Giá trị thực nghiệm | Giá trị thực nghiệm | Quan sát + metric |
| video_2 | Giá trị thực nghiệm | Giá trị thực nghiệm | Giá trị thực nghiệm | Quan sát |
| video_3 | Giá trị thực nghiệm | Giá trị thực nghiệm | Giá trị thực nghiệm | Quan sát |
| video_4 | Giá trị thực nghiệm | Giá trị thực nghiệm | Giá trị thực nghiệm | Quan sát |
| video_5 | Giá trị thực nghiệm | Giá trị thực nghiệm | Giá trị thực nghiệm | Quan sát |

Các giá trị minh họa **không được giữ lại** trong báo cáo cuối. Có thể mô tả frame/timestamp cụ thể và đính kèm ảnh minh họa. Video 2–5 chỉ mô tả quan sát/không được ghi fabricated scores. Các thống kê từ predictions không thể gọi là ground-truth accuracy.

### Bước 2: `scripts/validate_submission.py`

Kiểm tra các file `runs/nop_bai/video_1.txt`…`video_5.txt`:

- Đủ file, là kết quả dataset thật.
- Mỗi dòng đúng 10 trường, không header, frame/ID hợp lệ, bbox width/height positive, finite coords/conf.
- Không duplicate `(frame,track_id)`, frames sorted, frame index mapping khớp GT/dataset conventions.
- Không có `--max-frames` cho final run; metadata xác nhận toàn bộ input frames được xử lý.
- Mỗi file đúng source video, configs khớp `selected_configs.json`, báo cáo và metadata; không lẫn runs.
- Frame không có tracks **không cần** có dòng; nếu output hoàn toàn rỗng, điều tra nguyên nhân và không chấp nhận qua loa.
- Kiểm tra config/model hashes/device/version bất thường; video output không bị ghi đè từ experiment khác.

### Bước 3: `scripts/prepare_submission.py`

Copy đúng file từ `runs/nop_bai` và báo cáo thành:

```text
submission/
├── video_1.txt
├── video_2.txt
├── video_3.txt
├── video_4.txt
├── video_5.txt
└── BAO_CAO_LAB21.md
```

Zip thành `submission.zip`. Không đóng gói dataset/weights. Nếu gói lab có quy định nộp cụ thể khác thì tuân theo tài liệu chính thức. Kiểm tra ZIP có đủ file, có thể giải nén, nội dung giống nguồn và không có file rác.

### Bước 4: End-to-end QA

```bash
pytest -v
python scripts/check_data.py --lab-data-root "$LAB_DATA"
python scripts/validate_submission.py --input runs/nop_bai
python scripts/prepare_submission.py
```

Chạy smoke test cuối; sau mọi chỉnh sửa vào file nộp phải validate lại. Cập nhật README các lệnh tái lập từ clone -> setup -> dataset -> experiments -> TrackEval -> submission. Ghi rõ seed, deterministic limitations và asset checksums.

**Acceptance CP5:** Báo cáo hoàn chỉnh tiếng Việt, không placeholders, mô tả đầy đủ baseline/experiments/metrics/video-specific conclusions; năm final MOT files full-sequence; validator/tests pass; ZIP hợp lệ; repo không chứa secrets/dataset; README tái lập; commit thành công, push và xác minh SHA trên GitHub (trừ sự cố bên ngoài đã ghi nhận rõ là REMOTE_PENDING).

```bash
git add .
git commit -m "CP5: Complete final report submission and validation"
git push origin main  # bắt buộc; kiểm tra remote SHA theo mục 0A
```

## 9. Error handling, retry và tính toàn vẹn khoa học

- **Dependencies:** Kiểm tra đúng environment, version conflicts, install compatible versions, rerun imports/tests, update lock file. Không bỏ tracker vì lỗi import ban đầu.
- **Weights:** Ưu tiên official source/cache, kiểm tra integrity/model identity; không âm thầm thay checkpoint.
- **BoxMOT API mismatch:** Đọc installed API, kiểm tra input/output shapes, sử dụng adapter, smoke test motion & Re-ID trước khi experiment.
- **Memory/OOM:** Xử lý frames tuần tự, không giữ frames trong RAM, giảm concurrency, cache detections hợp lệ, fallback CPU cho thành phần khó; **không giảm 640** của bài nộp chính.
- **Slow inference:** Giảm thử nghiệm không cần thiết, chọn representative windows so sánh công bằng, vẫn full-sequence cho năm outputs; không bịa kết quả nếu inference chưa xong.
- **Evaluation fail:** Check GT/prediction 10-column formats, 1-based indexing, sequence lengths, class mapping, ignore regions, TrackEval paths/config và covered GT frames.
- **Inconsistent runs:** Kiểm tra seeds, device nondeterminism, tracker state reset, ordered frames, model/dependency hash/cache; ghi limitation nếu cần.
- **Dataset inaccessible:** Thử nguồn Drive, local/cache, archive validation; nếu cần protected access, chỉ hỏi quyền. Không tạo `video_*.txt` từ synthetic frames để giả nộp thật.
- **GitHub create/push failure:** Thực hiện đúng mục 0A: tự tạo PRIVATE repo mới, kiểm tra quyền, retry, xác minh remote SHA; chỉ hỏi người dùng để xác thực/ủy quyền. Nếu GitHub outage không thể khắc phục, commit local + REMOTE_PENDING và tự retry ở các CP sau; không giả push thành công.

## 10. Thứ tự checkpoint và định nghĩa hoàn thành

```text
0A   Init local Git + CREATE new PRIVATE GitHub repo   → verify origin/visibility
CP0  Bootstrap + dependency smoke tests                 → validate → commit/push/verify SHA
CP1  Dataset + scenes + metrics notebook               → validate → commit/push/verify SHA
CP2  Detector + five-tracker adapter + MOT + baseline  → validate → commit/push/verify SHA
CP3  Controlled comparisons + final full sequences    → validate → commit/push/verify SHA
CP4  TrackEval metrics for video_1 only                → validate → commit/push/verify SHA
CP5  Vietnamese report + validator + submission.zip   → validate → commit/push/verify SHA
```

Không chuyển checkpoint nếu acceptance chưa pass, trừ khi có phụ thuộc ngoài không thể truy cập bằng quyền hiện có: khi đó làm những phần độc lập, ghi checkpoint **BLOCKED**, không tuyên bố hoàn thành. Nếu sửa lại CP trước, regression test và corrective commit.

### Definition of Done

- [ ] Môi trường reproducible và dependencies pinned.
- [ ] YOLO26n model đúng, 640 px, person-only, detector `conf`/NMS `iou` đúng.
- [ ] Năm BoxMOT trackers chạy, Re-ID thật sự bật ở nhóm appearance khi so sánh.
- [ ] Năm video dataset thật hợp lệ; `video_1` GT đúng.
- [ ] Notebook chạy; metric theory + 3 True/False + YOLO inference.
- [ ] Baseline 150 frames có evidence ID continuity hoặc lỗi quan sát được.
- [ ] Mỗi video đã thử motion và appearance tracker + one-variable conf/IoU sweeps.
- [ ] Có experiment log, visual comparisons, rejected settings với reasons.
- [ ] Có full-sequence outputs `video_1.txt`…`video_5.txt`, MOTChallenge valid.
- [ ] TrackEval đã tính thật HOTA/MOTA/IDF1 của `video_1`.
- [ ] Không có synthetic hoặc invented metrics/results trong báo cáo.
- [ ] Báo cáo tiếng Việt có đủ so sánh/quan sát/kết luận, không placeholders.
- [ ] `submission.zip` hợp lệ và tests/validator pass.
- [ ] Có GitHub repository PRIVATE **mới**, đúng owner, đúng `origin`, branch `main` và URL ghi vào README.
- [ ] Có commits CP0–CP5, từng checkpoint đã push và SHA trên remote trùng local (hoặc ghi rõ REMOTE_PENDING nếu có outage); Git working tree sạch.

## 11. Final response của người triển khai

Trả lời bằng tiếng Việt khi hoàn thành. Báo cáo:

1. **Implementation summary**: môi trường, thiết bị, source, giải pháp.
2. **GitHub repository**: URL repository GitHub PRIVATE mới, owner, branch `main`, remote `origin` và kết quả kiểm tra visibility.
3. **Checkpoint status**: CP0–CP5, PASS/BLOCKED, commit hash, trạng thái PUSHED/REMOTE_PENDING và xác minh remote SHA thực tế.
4. **Final configurations**: năm video, tracker, conf, iou và lý do chọn.
5. **video_1 quantitative results**: HOTA, MOTA, IDF1 thực từ TrackEval.
6. **Deliverables**: paths của năm `.txt`, báo cáo, ZIP; chỉ nói file tồn tại nếu thực có.
7. **Reproducibility and limitations**: lệnh chạy, dependencies, blockers nếu còn.

**Nhiệm vụ của bạn là tạo GitHub repository mới PRIVATE từ thư mục hiện tại, sau đó làm lab thật; không dừng ở việc tạo skeleton code hoặc kế hoạch.** Tự ra quyết định kỹ thuật hợp lý; tự chạy, test, sửa và ghi nhận. Ưu tiên kết quả chính xác, tái lập được và trung thực hơn việc tạo đầu ra trông có vẻ hoàn thành.

## 12. Tham khảo kỹ thuật

- [Ultralytics YOLO26](https://docs.ultralytics.com/models/yolo26/)
- [BoxMOT — GitHub](https://github.com/mikel-brostrom/boxmot)
- [BoxMOT Python API](https://github.com/mikel-brostrom/boxmot/blob/master/docs/python/index.md)
- [GitHub CLI: tạo repository mới](https://cli.github.com/manual/gh_repo_create)
- [GitHub CLI: đăng nhập an toàn](https://cli.github.com/manual/gh_auth_login)
- [GitHub CLI: Git credential helper](https://cli.github.com/manual/gh_auth_setup-git)
- [TrackEval — GitHub](https://github.com/JonathonLuiten/TrackEval)
- [TrackEval MOTChallenge evaluation](https://github.com/JonathonLuiten/TrackEval/blob/master/docs/MOTChallenge-Official/Readme.md)
- [MOTChallenge](https://motchallenge.net/)

**End of IMPLEMENTATION_GUIDE.md**
