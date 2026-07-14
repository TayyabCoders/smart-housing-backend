from __future__ import annotations

import os
import re
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional, Tuple

import cv2
import numpy as np
import structlog
from ultralytics import YOLO

from app.utils.ocr_util import get_ocr

_logger = structlog.get_logger(__name__)

_yolo_model: Optional[YOLO] = None


def _get_yolo(weights_path: str) -> YOLO:
    global _yolo_model
    if _yolo_model is None:
        _logger.info("video.yolo.load", weights=weights_path)
        _yolo_model = YOLO(weights_path)
    return _yolo_model


def _extract_plate_text(image_bgr: np.ndarray, debug_dir: Path = None) -> str:
    ocr = get_ocr()
    debug_dir = debug_dir or Path("uploads/output_debug")
    debug_dir.mkdir(parents=True, exist_ok=True)
    ts = int(datetime.now(timezone.utc).timestamp() * 1000)

    cv2.imwrite(str(debug_dir / f"{ts}_0_original.jpg"), image_bgr)

    gray = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2GRAY)
    cv2.imwrite(str(debug_dir / f"{ts}_1_gray.jpg"), gray)

    h, w = gray.shape
    if h < 48 or w < 200:
        scale = max(50 / h, 200 / w)
        new_w, new_h = int(w * scale), int(h * scale)
        gray = cv2.resize(gray, (new_w, new_h), interpolation=cv2.INTER_LANCZOS4)
        cv2.imwrite(str(debug_dir / f"{ts}_2_resized.jpg"), gray)

    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (2, 2))
    gray = cv2.morphologyEx(gray, cv2.MORPH_OPEN, kernel)

    if gray.mean() < 80:
        gamma = 1.6
        table = np.array([(i / 255.0) ** (1 / gamma) * 255 for i in range(256)]).astype("uint8")
        gray = cv2.LUT(gray, table)

    cv2.imwrite(str(debug_dir / f"{ts}_2b_brightness_fixed.jpg"), gray)

    denoised = cv2.bilateralFilter(gray, 5, 30, 30)
    cv2.imwrite(str(debug_dir / f"{ts}_2b_denoised.jpg"), denoised)

    p_low, p_high = np.percentile(denoised, (1, 99))
    gray = np.clip((gray - p_low) * (255 / (p_high - p_low)), 0, 255).astype(np.uint8)
    cv2.imwrite(str(debug_dir / f"{ts}_2c_contrast_stretched.jpg"), gray)

    processed = cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR)
    cv2.imwrite(str(debug_dir / f"{ts}_7_processed.jpg"), processed)

    result = ocr.predict(processed)

    plate_code = ""
    plate_digits = ""

    for r in result:
        rec_texts = r.get("rec_texts", [])
        rec_scores = r.get("rec_scores", [])

        if len(rec_texts) == 1:
            raw = str(rec_texts[0]).upper()
            cleaned = re.sub(r"[^A-Z0-9]", "", raw)
            if re.match(r"^[A-Z]{2,3}[0-9]{3,4}$", cleaned):
                return cleaned

        for text, score in zip(rec_texts, rec_scores):
            if score is None or np.isnan(score) or float(score) < 0.40:
                continue
            raw = str(text).upper()
            cleaned = re.sub(r"[^A-Z0-9]", "", raw)

            if re.match(r"^[A-Z]{2,3}$", cleaned):
                plate_code = cleaned
                continue
            if re.match(r"^[0-9]{3,4}$", cleaned):
                plate_digits = cleaned
                continue
            m = re.match(r"^([A-Z]{2,3})([0-9]{1,4})$", cleaned)
            if m:
                letters, digits = m.groups()
                if len(letters) >= 2:
                    plate_code = letters
                if len(digits) >= 3:
                    plate_digits = digits

    return plate_code + plate_digits


class VideoProcessingService:
    def __init__(self):
        from app.configs.app_config import settings
        self.weights_path = settings.PARKING_WEIGHTS_PATH

    def detect_first_plate_and_snapshot(
        self,
        video_path: str,
        snapshots_dir: Path,
        conf: float = 0.45,
    ) -> Optional[Tuple[str, datetime, str]]:
        """Returns (plate_number, timestamp_utc, snapshot_path) for the first detected plate."""
        logger = _logger.bind(video=video_path)
        yolo = _get_yolo(self.weights_path)

        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            logger.error("video.open.failed")
            return None

        fps = cap.get(cv2.CAP_PROP_FPS) or 25.0
        frame_idx = 0
        snapshots_dir.mkdir(parents=True, exist_ok=True)

        try:
            while True:
                ok, frame = cap.read()
                if not ok:
                    break
                frame_idx += 1

                results = yolo.predict(source=frame, conf=conf, verbose=False)
                if not results:
                    continue
                boxes = results[0].boxes
                if boxes is None:
                    continue

                for box in boxes:
                    x1, y1, x2, y2 = box.xyxy[0]
                    x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)
                    h, w = frame.shape[:2]
                    x1 = max(0, min(x1, w - 1))
                    x2 = max(1, min(x2, w))
                    y1 = max(0, min(y1, h - 1))
                    y2 = max(1, min(y2, h))
                    if x2 <= x1 or y2 <= y1:
                        continue

                    crop = frame[y1:y2, x1:x2]
                    plate_text = _extract_plate_text(crop)

                    cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                    if plate_text:
                        cv2.putText(
                            frame, plate_text, (x1, max(0, y1 - 10)),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2,
                        )

                    if not plate_text:
                        continue

                    ts_sec = frame_idx / fps
                    ts_utc = datetime.now(timezone.utc)
                    snap_name = f"{plate_text}_{int(ts_sec * 1000)}.jpg"
                    snap_path = snapshots_dir / snap_name
                    cv2.imwrite(str(snap_path), frame)

                    logger.info("video.plate.detected", plate=plate_text, snapshot=str(snap_path))
                    return plate_text, ts_utc, str(snap_path)
        finally:
            cap.release()

        logger.info("video.plate.not_found")
        return None

    def detect_plate_from_image(
        self,
        image_path: str,
        snapshots_dir: Path,
        conf: float = 0.45,
    ) -> Optional[Tuple[str, str]]:
        """Returns (plate_number, snapshot_path) from a single image."""
        logger = _logger.bind(image=image_path)
        yolo = _get_yolo(self.weights_path)

        img = cv2.imread(image_path)
        if img is None:
            logger.error("image.open.failed")
            return None

        snapshots_dir.mkdir(parents=True, exist_ok=True)
        results = yolo.predict(source=img, conf=conf, verbose=False)
        if not results:
            return None

        boxes = results[0].boxes
        if boxes is None:
            return None

        for box in boxes:
            x1, y1, x2, y2 = map(int, box.xyxy[0])
            h, w = img.shape[:2]
            x1 = max(0, min(x1, w - 1))
            x2 = max(1, min(x2, w))
            y1 = max(0, min(y1, h - 1))
            y2 = max(1, min(y2, h))
            if x2 <= x1 or y2 <= y1:
                continue

            crop = img[y1:y2, x1:x2]
            plate_text = _extract_plate_text(crop)

            cv2.rectangle(img, (x1, y1), (x2, y2), (0, 255, 0), 2)
            if plate_text:
                cv2.putText(
                    img, plate_text, (x1, max(0, y1 - 10)),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2,
                )

            if not plate_text:
                continue

            snap_name = f"{plate_text}_{int(datetime.now().timestamp() * 1000)}.jpg"
            snap_path = snapshots_dir / snap_name
            cv2.imwrite(str(snap_path), img)

            logger.info("image.plate.detected", plate=plate_text, snapshot=str(snap_path))
            return plate_text, str(snap_path)

        return None

    @staticmethod
    def save_uploaded_temp(file_bytes: bytes, suffix: str = ".mp4") -> str:
        fd, tmp_path = tempfile.mkstemp(suffix=suffix)
        with os.fdopen(fd, "wb") as f:
            f.write(file_bytes)
        return tmp_path
