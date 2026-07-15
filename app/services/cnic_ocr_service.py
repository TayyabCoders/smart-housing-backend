from __future__ import annotations

import re
from datetime import datetime
from typing import Dict, Optional

import cv2
import numpy as np
import structlog

_logger = structlog.get_logger(__name__)

_CNIC_DASHED_RE = re.compile(r"^(\d{5})-(\d{7})-(\d)$")
_CNIC_DIGITS_RE = re.compile(r"^(\d{13})$")
_DATE_RE = re.compile(r"\b(\d{1,2})[./-](\d{1,2})[./-](\d{4})\b")
_GENDER_RE = re.compile(r"\b([MF])\b", re.I)


def _normalize_cnic(raw: str) -> Optional[str]:
    if not raw:
        return None
    s = re.sub(r"[^0-9-]", "", raw)
    m = _CNIC_DASHED_RE.match(s)
    if m:
        return f"{m.group(1)}-{m.group(2)}-{m.group(3)}"
    s_digits = re.sub(r"[^0-9]", "", s)
    m2 = _CNIC_DIGITS_RE.match(s_digits)
    if m2:
        d = m2.group(1)
        return f"{d[0:5]}-{d[5:12]}-{d[12]}"
    return None


def _preprocess_variants(img: np.ndarray) -> list[np.ndarray]:
    variants: list[np.ndarray] = []
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    den = cv2.bilateralFilter(gray, 9, 75, 75)
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    enh = clahe.apply(den)
    variants.append(cv2.cvtColor(enh, cv2.COLOR_GRAY2BGR))

    _, otsu = cv2.threshold(enh, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    variants.append(cv2.cvtColor(otsu, cv2.COLOR_GRAY2BGR))

    adap = cv2.adaptiveThreshold(enh, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 31, 10)
    variants.append(cv2.cvtColor(adap, cv2.COLOR_GRAY2BGR))

    kernel = np.ones((3, 3), np.uint8)
    closed = cv2.morphologyEx(enh, cv2.MORPH_CLOSE, kernel, iterations=1)
    variants.append(cv2.cvtColor(closed, cv2.COLOR_GRAY2BGR))
    return variants


def _rotate_variants(img: np.ndarray) -> list[np.ndarray]:
    return [
        img,
        cv2.rotate(img, cv2.ROTATE_90_CLOCKWISE),
        cv2.rotate(img, cv2.ROTATE_180),
        cv2.rotate(img, cv2.ROTATE_90_COUNTERCLOCKWISE),
    ]


def _parse_match(m) -> Optional[datetime]:
    try:
        d, mon, y = map(int, m.groups())
        if y < 100:
            y += 1900 if y >= 50 else 2000
        return datetime(y, mon, d)
    except Exception:
        return None


def _extract_fields(ocr_blob: str) -> Dict[str, Optional[object]]:
    lines = [l.strip() for l in ocr_blob.splitlines() if l.strip()]
    lower = ocr_blob.lower()

    result: Dict[str, Optional[object]] = {
        "cnic_number": None,
        "name": None,
        "father_name": None,
        "gender": None,
        "country_of_stay": None,
        "date_of_birth": None,
        "date_of_issue": None,
        "date_of_expiry": None,
    }

    m = re.search(r"(\d{5}-\d{7}-\d)", ocr_blob)
    if m:
        result["cnic_number"] = _normalize_cnic(m.group(1))
    else:
        m = re.search(r"(\d{13})", ocr_blob)
        if m:
            result["cnic_number"] = _normalize_cnic(m.group(1))

    def value_after(labels: list[str], max_skip: int = 2) -> Optional[str]:
        lbls = [lbl.lower() for lbl in labels]
        for i, line in enumerate(lines):
            if any(l in line.lower() for l in lbls):
                for j in range(i + 1, min(i + 1 + max_skip, len(lines))):
                    cand = lines[j].strip()
                    if cand:
                        return cand
        return None

    result["name"] = value_after(["Name", "Name:", "Holder"])
    result["father_name"] = value_after(["Father Name", "Father's Name", "Father"])

    gm = _GENDER_RE.search(ocr_blob)
    if gm:
        result["gender"] = gm.group(1).upper()

    if "pakistan" in lower:
        result["country_of_stay"] = "PAKISTAN"

    date_matches = list(_DATE_RE.finditer(ocr_blob))

    def assign_by_label(label_keys: list[str]) -> Optional[datetime]:
        for key in label_keys:
            pos = lower.find(key)
            if pos == -1:
                continue
            for dm in date_matches:
                if abs(dm.start() - pos) < 250:
                    return _parse_match(dm)
        return None

    result["date_of_birth"] = assign_by_label(["date of birth", "dob", "birth"])
    result["date_of_issue"] = assign_by_label(["date of issue", "issue", "doi"])
    result["date_of_expiry"] = assign_by_label(["date of expiry", "expiry", "doe"])

    if date_matches and not all([result["date_of_birth"], result["date_of_issue"], result["date_of_expiry"]]):
        parsed = [_parse_match(dm) for dm in date_matches]
        parsed = sorted([d for d in parsed if d])
        if not result["date_of_birth"] and parsed:
            result["date_of_birth"] = parsed[0]
        if not result["date_of_issue"] and len(parsed) > 1:
            result["date_of_issue"] = parsed[1]
        if not result["date_of_expiry"] and len(parsed) > 2:
            result["date_of_expiry"] = parsed[2]

    return result


class CnicOcrService:
    def __init__(self):
        pass

    def normalize_cnic(self, raw: str) -> Optional[str]:
        return _normalize_cnic(raw)

    def extract_cnic_number_from_image_bytes(
        self, image_bytes: bytes, min_conf: float = 0.35
    ) -> Optional[str]:
        arr = np.frombuffer(image_bytes, dtype=np.uint8)
        img = cv2.imdecode(arr, cv2.IMREAD_COLOR)
        if img is None:
            _logger.warning("cnic_ocr.decode_failed")
            return None

        h0, w0 = img.shape[:2]
        if min(h0, w0) < 600:
            scale = max(1, int(600 / max(1, min(h0, w0))))
            if scale > 1:
                img = cv2.resize(img, (w0 * scale, h0 * scale), interpolation=cv2.INTER_LANCZOS4)

        from app.utils.ocr_util import run_ocr  # lazy import — avoids heavy load at startup

        for rotated in _rotate_variants(img):
            for proc in _preprocess_variants(rotated):
                kept: list[str] = []
                for detected_text, score_f in run_ocr(proc):
                    if np.isnan(score_f) or score_f < min_conf:
                        continue
                    kept.append(detected_text)

                if not kept:
                    continue

                blob = " ".join(kept)
                m = re.search(r"(\d{5}-\d{7}-\d)", blob)
                if m:
                    norm = _normalize_cnic(m.group(1))
                    if norm:
                        _logger.info("cnic_ocr.detected", cnic=norm)
                        return norm

                m2 = re.search(r"(\d{13})", blob)
                if m2:
                    norm2 = _normalize_cnic(m2.group(1))
                    if norm2:
                        _logger.info("cnic_ocr.detected", cnic=norm2)
                        return norm2

        _logger.info("cnic_ocr.not_found")
        return None

    def extract_cnic_fields_from_image_bytes(
        self, image_bytes: bytes, min_conf: float = 0.35
    ) -> Dict[str, Optional[object]]:
        empty = {k: None for k in [
            "cnic_number", "name", "father_name", "gender",
            "country_of_stay", "date_of_birth", "date_of_issue", "date_of_expiry",
        ]}
        arr = np.frombuffer(image_bytes, dtype=np.uint8)
        img = cv2.imdecode(arr, cv2.IMREAD_COLOR)
        if img is None:
            return empty

        h0, w0 = img.shape[:2]
        if min(h0, w0) < 600:
            scale = max(1, int(600 / max(1, min(h0, w0))))
            if scale > 1:
                img = cv2.resize(img, (w0 * scale, h0 * scale), interpolation=cv2.INTER_LANCZOS4)

        from app.utils.ocr_util import run_ocr  # lazy import — avoids heavy load at startup
        best_fields: Optional[Dict[str, Optional[object]]] = None

        for rotated in _rotate_variants(img):
            for proc in _preprocess_variants(rotated):
                kept: list[str] = []
                for detected_text, score_f in run_ocr(proc):
                    if np.isnan(score_f) or score_f < min_conf:
                        continue
                    kept.append(detected_text)

                if not kept:
                    continue

                blob = "\n".join(kept)
                fields = _extract_fields(blob)
                if fields.get("cnic_number"):
                    return fields
                if best_fields is None:
                    best_fields = fields

        return best_fields if best_fields is not None else empty
