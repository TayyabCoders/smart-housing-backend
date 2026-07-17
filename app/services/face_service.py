from datetime import datetime
from typing import Any, Dict, Optional
from uuid import UUID

import structlog
from dependency_injector.wiring import Provide, inject
from fastapi import HTTPException, UploadFile, status

from app.models.enums import ActionType, DetectionStatus, PersonRole

logger = structlog.get_logger(__name__)

_ROLE_TO_STATUS = {
    PersonRole.RESIDENT: DetectionStatus.RESIDENT,
    PersonRole.STAFF: DetectionStatus.STAFF,
    PersonRole.VISITOR: DetectionStatus.VISITOR,
}

_BLACKLISTING_ACTIONS = {ActionType.DENY, ActionType.FLAG_UNKNOWN}


class FaceService:
    @inject
    def __init__(
        self,
        face_repository=Provide["face_repository"],
        face_recognition_service=Provide["face_recognition_service"],
        upload_service=Provide["upload_service"],
    ):
        self.face_repository = face_repository
        self.face_recognition_service = face_recognition_service
        self.upload_service = upload_service

    async def detect_and_match(self, file: UploadFile, camera_id: UUID) -> Dict[str, Any]:
        try:
            image_bytes = await file.read()
            await file.seek(0)

            faces = self.face_recognition_service.detect_faces(image_bytes)
            if not faces:
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail="No face detected in the image",
                )

            face = max(faces, key=lambda f: f["confidence"])
            match = await self.face_repository.find_closest_person(face["embedding"])

            upload_result = await self.upload_service.upload_image(file)
            image_url = upload_result["url"]

            if match:
                person, similarity = match
                detection_status = _ROLE_TO_STATUS.get(person.role, DetectionStatus.UNKNOWN)
                confidence = similarity
                matched_person_id = person.id
                matched_person_info = person
            else:
                detection_status = DetectionStatus.UNKNOWN
                confidence = face["confidence"]
                matched_person_id = None
                matched_person_info = None

            detection = await self.face_repository.create({
                "matched_person_id": matched_person_id,
                "confidence": confidence,
                "bbox": face["bbox"],
                "camera_id": camera_id,
                "status": detection_status,
                "image_url": image_url,
            })

            return {
                "id": detection.id,
                "matched_person_id": matched_person_id,
                "confidence": confidence,
                "bbox": face["bbox"],
                "status": detection_status.value,
                "image_url": image_url,
                "full_frame_url": image_url,
                "matched_person": (
                    {
                        "name": matched_person_info.name,
                        "flat_no": matched_person_info.flat_no,
                        "role": matched_person_info.role.value,
                    }
                    if matched_person_info
                    else None
                ),
                "camera_name": None,
                "detected_at": detection.detected_at,
            }
        except HTTPException:
            raise
        except Exception as e:
            logger.error("FaceService: detect_and_match failed", exc_info=True)
            raise e

    async def enroll(
        self,
        file: UploadFile,
        person_id: Optional[UUID],
        name: Optional[str],
        role: Optional[str],
        flat_no: Optional[str],
        phone: Optional[str],
    ) -> Dict[str, Any]:
        try:
            image_bytes = await file.read()
            await file.seek(0)

            faces = self.face_recognition_service.detect_faces(image_bytes)
            if not faces:
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail="No face detected in the uploaded image",
                )
            face = max(faces, key=lambda f: f["confidence"])

            upload_result = await self.upload_service.upload_image(file)
            image_url = upload_result["url"]

            if person_id:
                person = await self.face_repository.get_person(person_id)
                if not person:
                    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Person not found")
            else:
                if not name or not role:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="name and role are required to enroll a new person",
                    )
                try:
                    role_enum = PersonRole(role)
                except ValueError:
                    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid role")

                person = await self.face_repository.create_person({
                    "name": name,
                    "role": role_enum,
                    "flat_no": flat_no,
                    "phone": phone,
                    "photo_url": image_url,
                })

            await self.face_repository.create_embedding(person.id, face["embedding"], image_url)

            return {
                "id": person.id,
                "name": person.name,
                "role": person.role.value,
                "flat_no": person.flat_no,
                "photo_url": person.photo_url or image_url,
            }
        except HTTPException:
            raise
        except Exception as e:
            logger.error("FaceService: enroll failed", exc_info=True)
            raise e

    async def list_detections(
        self,
        camera_id: Optional[UUID],
        status_filter: Optional[str],
        date_from: Optional[datetime],
        date_to: Optional[datetime],
        search: Optional[str],
        offset: int,
        limit: int,
    ) -> Dict[str, Any]:
        try:
            status_enum = None
            if status_filter:
                try:
                    status_enum = DetectionStatus(status_filter)
                except ValueError:
                    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid status filter")

            result = await self.face_repository.list_detections(
                camera_id=camera_id,
                status=status_enum,
                date_from=date_from,
                date_to=date_to,
                search=search,
                offset=offset,
                limit=limit,
            )
            stats = await self.face_repository.get_stats()

            items = []
            for d in result["items"]:
                items.append({
                    "id": d.id,
                    "matched_person_id": d.matched_person_id,
                    "confidence": float(d.confidence) if d.confidence is not None else None,
                    "bbox": d.bbox,
                    "status": d.status.value,
                    "image_url": d.image_url,
                    "full_frame_url": d.full_frame_url,
                    "matched_person": (
                        {
                            "name": d.matched_person.name,
                            "flat_no": d.matched_person.flat_no,
                            "role": d.matched_person.role.value,
                        }
                        if d.matched_person
                        else None
                    ),
                    "camera_name": d.camera.name if d.camera else None,
                    "detected_at": d.detected_at,
                })

            return {
                "items": items,
                "total": result["total"],
                "limit": limit,
                "offset": offset,
                "stats": stats,
            }
        except HTTPException:
            raise
        except Exception as e:
            logger.error("FaceService: list_detections failed", exc_info=True)
            raise e

    async def apply_action(self, detection_id: UUID, action: str, acted_by: UUID) -> Dict[str, Any]:
        try:
            try:
                action_enum = ActionType(action)
            except ValueError:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid action")

            detection = await self.face_repository.update_action(detection_id, action_enum, acted_by)
            if not detection:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Detection not found")

            if action_enum in _BLACKLISTING_ACTIONS:
                await self.face_repository.update(detection_id, {"status": DetectionStatus.BLACKLIST})

            return {
                "message": f"Action '{action}' applied to detection {detection_id}",
                "status": "success",
            }
        except HTTPException:
            raise
        except Exception as e:
            logger.error("FaceService: apply_action failed", exc_info=True)
            raise e
