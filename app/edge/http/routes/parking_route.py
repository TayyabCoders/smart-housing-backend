from pathlib import Path
from typing import Optional

from fastapi import APIRouter, Depends, File, Form, Query, Request, UploadFile, status
from dependency_injector.wiring import inject, Provide

from app.di.container import container
from app.configs.app_config import settings
from app.edge.http.controller.parking_controller import ParkingController
from app.schemas.parking_schema import (
    AllRecordsResponse,
    DetectResponse,
    EntryResponse,
    ExitResponse,
    StatusResponse,
)

router = APIRouter()


def _upload_dir() -> Path:
    p = Path(settings.PARKING_UPLOAD_DIR)
    p.mkdir(parents=True, exist_ok=True)
    return p


def _to_public_url(path: Optional[str], request: Request) -> Optional[str]:
    if not path:
        return None
    rel = str(path).replace("\\", "/").lstrip("/")
    return f"{str(request.base_url).rstrip('/')}/{rel}"


@router.post("/detect", response_model=DetectResponse)
@inject
async def detect_plate(
    request: Request,
    image_file: UploadFile = File(...),
    controller: ParkingController = Depends(Provide["parking_controller"]),
):
    image_bytes = await image_file.read()
    suffix = Path(image_file.filename or "image.jpg").suffix or ".jpg"
    result = await controller.detect_plate(
        image_file_bytes=image_bytes,
        image_file_suffix=suffix,
        upload_dir=_upload_dir(),
    )
    return DetectResponse(
        detected=result["detected"],
        plate_number=result.get("plate_number"),
        confidence=result.get("confidence"),
        snapshot_url=_to_public_url(result.get("snapshot_path"), request),
        message=result["message"],
        resident_status=result.get("resident_status"),
        owner_name=result.get("owner_name"),
        flat_number=result.get("flat_number"),
        vehicle_type=result.get("vehicle_type"),
    )


@router.post("/entry", response_model=EntryResponse, status_code=status.HTTP_201_CREATED)
@inject
async def register_entry(
    request: Request,
    plate_number: Optional[str] = Form(None),
    video_file: Optional[UploadFile] = File(None),
    video_url: Optional[str] = Form(None),
    cnic_number: Optional[str] = Form(None),
    cnic_image: Optional[UploadFile] = File(None),
    controller: ParkingController = Depends(Provide["parking_controller"]),
):
    video_bytes = await video_file.read() if video_file else None
    video_suffix = Path(video_file.filename or "video.mp4").suffix if video_file else ".mp4"
    cnic_bytes = await cnic_image.read() if cnic_image else None

    result = await controller.register_entry(
        upload_dir=_upload_dir(),
        plate_number=plate_number,
        video_file_bytes=video_bytes,
        video_file_suffix=video_suffix,
        video_url=video_url,
        cnic_number=cnic_number,
        cnic_image_bytes=cnic_bytes,
    )

    return EntryResponse(
        plate_number=result["plate_number"],
        cnic_number=result["cnic_number"],
        entry_image_url=_to_public_url(result.get("entry_image_path"), request),
        entry_time=result["entry_time"],
        status="IN",
        message=result["message"],
    )


@router.post("/exit", response_model=ExitResponse)
@inject
async def register_exit(
    request: Request,
    plate_number: Optional[str] = Form(None),
    video_file: Optional[UploadFile] = File(None),
    video_url: Optional[str] = Form(None),
    cnic_number: Optional[str] = Form(None),
    cnic_image: Optional[UploadFile] = File(None),
    controller: ParkingController = Depends(Provide["parking_controller"]),
):
    video_bytes = await video_file.read() if video_file else None
    video_suffix = Path(video_file.filename or "video.mp4").suffix if video_file else ".mp4"
    cnic_bytes = await cnic_image.read() if cnic_image else None

    result = await controller.register_exit(
        upload_dir=_upload_dir(),
        plate_number=plate_number,
        video_file_bytes=video_bytes,
        video_file_suffix=video_suffix,
        video_url=video_url,
        cnic_number=cnic_number,
        cnic_image_bytes=cnic_bytes,
    )

    return ExitResponse(
        plate_number=result["plate_number"],
        entry_time=result["entry_time"],
        cnic_number=result["cnic_number"],
        exit_image_url=_to_public_url(result.get("exit_image_path"), request),
        exit_time=result["exit_time"],
        duration_minutes=result["duration_minutes"],
        fee=result["fee"],
        message=result["message"],
    )


@router.get("/status/{plate_number}", response_model=StatusResponse)
@inject
async def get_status(
    plate_number: str,
    controller: ParkingController = Depends(Provide["parking_controller"]),
):
    result = await controller.get_status(plate_number)
    return StatusResponse(**result)


@router.get("/all", response_model=AllRecordsResponse)
@inject
async def get_all(
    page: int = Query(1, ge=1),
    limit: int = Query(50, ge=1, le=200),
    status_filter: Optional[str] = Query(None, pattern="^(IN|OUT)$"),
    date_filter: Optional[str] = Query(None, description="YYYY-MM-DD"),
    controller: ParkingController = Depends(Provide["parking_controller"]),
):
    result = await controller.get_all_records(
        page=page,
        limit=limit,
        status_filter=status_filter,
        date_filter=date_filter,
    )
    return AllRecordsResponse(**result)
