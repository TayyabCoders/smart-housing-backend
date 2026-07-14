from __future__ import annotations

from datetime import datetime, timezone
from math import ceil
from pathlib import Path
from typing import Any, Dict, Optional

import httpx
import structlog
from fastapi import HTTPException, status
from dependency_injector.wiring import inject, Provide

logger = structlog.get_logger(__name__)


def _now() -> datetime:
    return datetime.now(timezone.utc)


def compute_fee_minutes(elapsed_minutes: int) -> int:
    """
    Pricing: first 10 min free, then PKR 100 per 30-min block, capped at PKR 800.
    """
    if elapsed_minutes <= 10:
        return 0
    blocks = ceil((elapsed_minutes - 10) / 30)
    return min(blocks * 100, 800)


class ParkingService:
    @inject
    def __init__(
        self,
        parking_repository=Provide["parking_repository"],
        cnic_repository=Provide["cnic_repository"],
        video_processing_service=Provide["video_processing_service"],
        cnic_ocr_service=Provide["cnic_ocr_service"],
        prometheus=Provide["prometheus"],
    ):
        self.parking_repository = parking_repository
        self.cnic_repository = cnic_repository
        self.video_processing_service = video_processing_service
        self.cnic_ocr_service = cnic_ocr_service
        self.prometheus = prometheus

    # ------------------------------------------------------------------
    # ENTRY
    # ------------------------------------------------------------------
    async def register_entry(
        self,
        upload_dir: Path,
        plate_number: Optional[str] = None,
        video_file_bytes: Optional[bytes] = None,
        video_file_suffix: str = ".mp4",
        video_url: Optional[str] = None,
        cnic_number: Optional[str] = None,
        cnic_image_bytes: Optional[bytes] = None,
    ) -> Dict[str, Any]:
        logger.info(
            "parking.entry.request",
            plate=plate_number,
            video_url=video_url,
            cnic_provided=bool(cnic_number),
            cnic_image=bool(cnic_image_bytes),
        )

        detected_cnic, extracted_fields = self._resolve_cnic(cnic_number, cnic_image_bytes)
        detected_plate, entry_image_path = await self._resolve_plate(
            plate_number, video_file_bytes, video_file_suffix, video_url,
            snapshots_dir=upload_dir / "snapshots",
        )

        existing = await self.parking_repository.find_active_by_plate(detected_plate)
        if existing:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Vehicle already inside")

        await self.cnic_repository.upsert(detected_cnic, extracted_fields or {})

        record = await self.parking_repository.create_record({
            "plate_number": detected_plate,
            "cnic_number": detected_cnic,
            "status": "IN",
            "entry_time": _now(),
            "entry_image_path": entry_image_path,
        })

        logger.info("parking.entry.recorded", plate=detected_plate, id=record.id)
        return {
            "plate_number": detected_plate,
            "cnic_number": detected_cnic,
            "entry_image_path": entry_image_path,
            "entry_time": record.entry_time,
            "status": "IN",
            "message": "Entry recorded successfully",
        }

    # ------------------------------------------------------------------
    # EXIT
    # ------------------------------------------------------------------
    async def register_exit(
        self,
        upload_dir: Path,
        plate_number: Optional[str] = None,
        video_file_bytes: Optional[bytes] = None,
        video_file_suffix: str = ".mp4",
        video_url: Optional[str] = None,
        cnic_number: Optional[str] = None,
        cnic_image_bytes: Optional[bytes] = None,
    ) -> Dict[str, Any]:
        logger.info("parking.exit.request", plate=plate_number)

        detected_cnic, _ = self._resolve_cnic(cnic_number, cnic_image_bytes)
        detected_plate, exit_image_path = await self._resolve_plate(
            plate_number, video_file_bytes, video_file_suffix, video_url,
            snapshots_dir=upload_dir / "snapshots",
        )

        record = await self.parking_repository.find_active_by_plate(detected_plate)
        if not record:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Plate not found or already exited",
            )

        if (record.cnic_number or "") != (detected_cnic or ""):
            logger.warning(
                "parking.exit.cnic_mismatch",
                plate=detected_plate,
                expected=record.cnic_number,
                provided=detected_cnic,
            )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="CNIC does not match the entry record",
            )

        exit_time = _now()
        elapsed = int((exit_time - record.entry_time).total_seconds() // 60)
        fee = compute_fee_minutes(elapsed)

        updated = await self.parking_repository.update_record(record.id, {
            "status": "OUT",
            "exit_time": exit_time,
            "fee": fee,
            "exit_image_path": exit_image_path,
        })

        logger.info("parking.exit.recorded", plate=detected_plate, id=record.id, fee=fee)
        return {
            "plate_number": detected_plate,
            "entry_time": record.entry_time,
            "cnic_number": record.cnic_number,
            "exit_image_path": exit_image_path,
            "exit_time": exit_time,
            "duration_minutes": elapsed,
            "fee": fee,
            "message": f"Exit recorded successfully. Please pay PKR {fee}.",
        }

    # ------------------------------------------------------------------
    # STATUS
    # ------------------------------------------------------------------
    async def get_status(self, plate_number: str) -> Dict[str, Any]:
        record = await self.parking_repository.find_latest_by_plate(plate_number)
        if not record:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Plate not found")

        if record.status == "IN":
            now = _now()
            elapsed = int((now - record.entry_time).total_seconds() // 60)
            return {
                "plate_number": plate_number,
                "status": "IN",
                "entry_time": record.entry_time,
                "elapsed_minutes": elapsed,
                "current_fee": compute_fee_minutes(elapsed),
                "grace_period_remaining_minutes": max(0, 10 - elapsed),
            }

        return {
            "plate_number": plate_number,
            "status": "OUT",
            "exit_time": record.exit_time,
            "total_fee_paid": int(record.fee or 0),
        }

    # ------------------------------------------------------------------
    # ALL RECORDS
    # ------------------------------------------------------------------
    async def get_all_records(
        self,
        page: int = 1,
        limit: int = 50,
        status_filter: Optional[str] = None,
        date_filter: Optional[str] = None,
    ) -> Dict[str, Any]:
        result = await self.parking_repository.find_paginated(page, limit, status_filter, date_filter)
        data = []
        for r in result["items"]:
            elapsed = None
            current_fee = None
            if r.status == "IN":
                elapsed = int((_now() - r.entry_time).total_seconds() // 60)
                current_fee = compute_fee_minutes(elapsed)
            data.append({
                "plate_number": r.plate_number,
                "status": r.status,
                "entry_time": r.entry_time,
                "exit_time": r.exit_time,
                "duration_minutes": (
                    int((r.exit_time - r.entry_time).total_seconds() // 60)
                    if r.exit_time else None
                ),
                "fee": int(r.fee) if r.fee is not None else None,
                "entry_image_url": None,
                "exit_image_url": None,
                "elapsed_minutes": elapsed,
                "current_fee": current_fee,
            })
        return {"total": result["total"], "page": page, "limit": limit, "data": data}

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------
    def _resolve_cnic(
        self,
        cnic_number: Optional[str],
        cnic_image_bytes: Optional[bytes],
    ):
        """Validate/detect CNIC and return (normalized_cnic, extracted_fields)."""
        if cnic_number:
            normalized = self.cnic_ocr_service.normalize_cnic(cnic_number)
            if not normalized:
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail="Invalid CNIC format",
                )
            return normalized, None

        if cnic_image_bytes:
            fields = self.cnic_ocr_service.extract_cnic_fields_from_image_bytes(cnic_image_bytes)
            detected = (fields or {}).get("cnic_number")
            if not detected:
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail="No valid CNIC detected in image",
                )
            return detected, fields

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Provide cnic_number or cnic_image",
        )

    async def _resolve_plate(
        self,
        plate_number: Optional[str],
        video_file_bytes: Optional[bytes],
        video_file_suffix: str,
        video_url: Optional[str],
        snapshots_dir: Path,
    ):
        """Return (detected_plate, image_path). Uses provided plate or runs YOLO on video."""
        if plate_number:
            return plate_number, None

        tmp_path = None
        try:
            if video_file_bytes:
                tmp_path = self.video_processing_service.save_uploaded_temp(
                    video_file_bytes, suffix=video_file_suffix
                )
            elif video_url:
                with httpx.Client(timeout=60) as client:
                    resp = client.get(video_url)
                    resp.raise_for_status()
                    tmp_path = self.video_processing_service.save_uploaded_temp(resp.content, suffix=".mp4")
            else:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Provide plate_number, video_file, or video_url",
                )

            res = self.video_processing_service.detect_first_plate_and_snapshot(tmp_path, snapshots_dir)
            if not res:
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail="No plate detected in video",
                )
            detected_plate, _ts, image_path = res
            return detected_plate, image_path
        finally:
            if tmp_path:
                try:
                    Path(tmp_path).unlink(missing_ok=True)
                except Exception:
                    pass
