"""
ArcFace-based face detection + embedding extraction (insightface).
"""
from typing import Any, Dict, List

import cv2
import numpy as np
import structlog

logger = structlog.get_logger(__name__)


class FaceRecognitionService:
    """
    Loads the ArcFace model (buffalo_l) lazily on first use and caches it at the
    class level so repeated (transient) DI instantiations don't reload the model.
    """

    _app = None

    @property
    def app(self):
        cls = type(self)
        if cls._app is None:
            from insightface.app import FaceAnalysis

            logger.info("FaceRecognitionService: loading ArcFace model (buffalo_l)...")
            cls._app = FaceAnalysis(name="buffalo_l", providers=["CPUExecutionProvider"])
            cls._app.prepare(ctx_id=-1, det_size=(640, 640))
            logger.info("FaceRecognitionService: model loaded")
        return cls._app

    def detect_faces(self, image_bytes: bytes) -> List[Dict[str, Any]]:
        """Detect faces in an image, returning normalized bbox + 512-d embedding per face."""
        try:
            nparr = np.frombuffer(image_bytes, np.uint8)
            image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            if image is None:
                return []

            height, width = image.shape[:2]
            faces = self.app.get(image)

            results = []
            for face in faces:
                x1, y1, x2, y2 = face.bbox.tolist()
                results.append({
                    "bbox": {
                        "x": max(0.0, x1 / width),
                        "y": max(0.0, y1 / height),
                        "width": (x2 - x1) / width,
                        "height": (y2 - y1) / height,
                    },
                    "embedding": face.normed_embedding.tolist(),
                    "confidence": float(face.det_score),
                })
            return results
        except Exception as e:
            logger.error("FaceRecognitionService: detect_faces failed", exc_info=True)
            raise e
