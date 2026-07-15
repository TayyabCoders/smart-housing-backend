from __future__ import annotations

from typing import TYPE_CHECKING, List, Optional, Tuple

import structlog

if TYPE_CHECKING:
    import easyocr as _easyocr

_logger = structlog.get_logger(__name__)

_ocr_singleton: Optional["_easyocr.Reader"] = None


def get_ocr() -> "_easyocr.Reader":
    global _ocr_singleton
    if _ocr_singleton is None:
        import easyocr  # lazy import — avoids heavy load at startup
        _logger.info("ocr.singleton.init", backend="easyocr")
        _ocr_singleton = easyocr.Reader(["en"], gpu=False)
    return _ocr_singleton


def run_ocr(image) -> List[Tuple[str, float]]:
    """Run OCR on an image. Returns [(text, confidence), ...]."""
    ocr = get_ocr()
    raw = ocr.readtext(image)
    results: List[Tuple[str, float]] = []
    for item in raw:
        text = str(item[1])
        try:
            score = float(item[2])
        except Exception:
            score = 0.0
        results.append((text, score))
    return results
