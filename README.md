# Lab 21 — Multi-object tracking

Repository: https://github.com/kevindao94work/cv-robotics-lab21 (PRIVATE), branch `main`, remote `origin`.

Completed CODEX_IMPLEMENTATION_GUIDE.md against the assigned real dataset: 51 experiment runs, five full-sequence MOT outputs, executed notebook, real TrackEval metrics, and Vietnamese report. Checkpoint acceptance and evidence are recorded in `reports/checkpoints.json`. A checkpoint is not complete merely because its source exists.

## Reproduce

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
# Review synchronized comparisons before selecting tracker and confidence.
.venv/bin/python scripts/run_experiments.py --phase conf --tracker bytetrack
.venv/bin/python scripts/run_experiments.py --phase iou --tracker bytetrack --conf .30
# Run each evidence-selected config with --out runs/nop_bai, without --max-frames.
.venv/bin/python scripts/evaluate_video1.py
.venv/bin/python scripts/validate_submission.py
.venv/bin/python scripts/prepare_submission.py
```

Weights are `weights/yolo26n.pt` and `weights/osnet_x0_25_msmt17.pt`; their official source URLs and SHA256 are recorded with environment metadata. Detection uses the one-to-many NMS path (`nms=None`), image size 640 and person class 0. Re-ID runs on CPU, explicitly configured and checked for a live encoder. Seeds are 42; MPS operations are not guaranteed bitwise deterministic. Cache keys include model hash, frame bytes, confidence, NMS IoU, image size and inference mode. Each sequence creates a fresh tracker. Partial runs are rejected by submission validation.

Data, weights, third-party source and environments are excluded from Git. Original GT is used only for video_1, with MOT17 distractor preprocessing. No metrics for video_2–5.

## Final results

All CP0–CP5 acceptance checks pass. Detector: MPS on Apple Silicon; Re-ID: CPU FP32. All five tracker adapters pass smoke/regression tests; comparative real-video runs use ByteTrack and BoTSORT with live OSNet embeddings.

| Video | Tracker | Confidence | NMS IoU | Frames |
|---|---|---|---|---|
| video_1 | botsort | 0.15 | 0.50 | 600 |
| video_2 | bytetrack | 0.15 | 0.50 | 1050 |
| video_3 | botsort | 0.30 | 0.50 | 837 |
| video_4 | bytetrack | 0.30 | 0.50 | 900 |
| video_5 | bytetrack | 0.30 | 0.50 | 750 |

Video_1 TrackEval: HOTA 27.6804%, MOTA 15.1284%, IDF1 24.4190%. Absolute scores are low due to substantial misses; no quantitative accuracy is claimed for videos 2–5. Comparisons and limitations are in reports/BAO_CAO_LAB21.md.

Replay all 51 recorded configurations and final selected runs:

```sh
.venv/bin/python scripts/reproduce_experiments.py --lab-data-root "$LAB_DATA"
.venv/bin/python scripts/evaluate_candidates.py
.venv/bin/python scripts/render_comparisons.py
.venv/bin/python scripts/run_selected.py --lab-data-root "$LAB_DATA"
.venv/bin/python scripts/evaluate_video1.py --lab-data-root "$LAB_DATA"
.venv/bin/python scripts/validate_submission.py
.venv/bin/python scripts/prepare_submission.py
```

MOT outputs use positive frame/track IDs and one-based bbox origin. The migration script is only for legacy development results; new runs already use the correct origin and must not be translated again. The local submission.zip contains exactly the five TXT files and Vietnamese report; it is intentionally excluded from Git. Receipts for CP0–CP4 are committed in reports/checkpoint_receipts.json; the final CP5 push receipt is stored locally in reports/push_verification.jsonl and its SHA can be verified with git ls-remote origin refs/heads/main.
