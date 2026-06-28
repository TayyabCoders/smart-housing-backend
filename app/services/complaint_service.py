from typing import Optional, Dict, Any, List
from uuid import UUID

from fastapi import HTTPException, status

from app.schemas.complaint_schema import ComplaintCreate, ComplaintUpdate, Complaint as ComplaintSchema
from app.di.container import container
from app.models.complaint_model import Complaint as ComplaintModel
from app.models.user_model import User, Role
import structlog
from dependency_injector.wiring import inject, Provide

logger = structlog.get_logger(__name__)


class ComplaintService:
    @inject
    def __init__(
        self,
        complaint_repository = Provide["complaint_repository"],
        prometheus = Provide["prometheus"],
    ):
        self.complaint_repository = complaint_repository
        self.prometheus = prometheus
    
    async def list_complaints(self, filters: dict = None, offset: int = 0, limit: int = 10, current_user: User = None) -> Dict[str, Any]:
        try:
            logger.info("ComplaintService: Listing complaints...")
            
            # Apply role-based filtering
            if current_user and current_user.role != Role.admin:
                # Non-admin users can only see their own complaints
                filters = filters or {}
                filters["user_id"] = str(current_user.id)
            
            result = await self.complaint_repository.findAndCountAll(filters, offset, limit)
            
            # Convert SQLAlchemy Complaint objects to Pydantic Complaint schemas
            complaint_schemas = [ComplaintSchema.model_validate(complaint) for complaint in result['rows']]
            result['rows'] = complaint_schemas
            
            # Count complaints by status
            status_filters = filters.copy() if filters else {}
            all_complaints = await self.complaint_repository.findAll(status_filters)
            
            pending_count = sum(1 for c in all_complaints if c.status.value == "Pending")
            in_progress_count = sum(1 for c in all_complaints if c.status.value == "In_Progress")
            resolved_count = sum(1 for c in all_complaints if c.status.value == "Resolved")
            rejected_count = sum(1 for c in all_complaints if c.status.value == "Rejected")
            
            result['pending'] = pending_count
            result['in_progress'] = in_progress_count
            result['resolved'] = resolved_count
            result['rejected'] = rejected_count
            
            logger.info(f"ComplaintService: Listed complaints successfully. Total: {result['total']}")
            
            # Record business event
            self.prometheus.record_business_event("complaint_list", "success")
            
            return result
        
        except Exception as e:
            logger.error("ComplaintService: Failed to list complaints.", exc_info=True)
            raise e

    async def get_complaint(self, complaint_id: str) -> Any:
        try:
            logger.info("ComplaintService: Getting complaint...")
            
            # Convert string to UUID if needed
            try:
                complaint_uuid = UUID(complaint_id) if isinstance(complaint_id, str) else complaint_id
            except ValueError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid complaint ID format"
                )
            
            complaint = await self.complaint_repository.findById(complaint_uuid)
            
            if not complaint:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Complaint not found"
                )
            
            logger.info(f"ComplaintService: Got complaint successfully: {complaint.tracking_id}")
            
            # Convert SQLAlchemy Complaint to Pydantic Complaint schema
            return ComplaintSchema.model_validate(complaint)
        
        except HTTPException:
            raise
        except Exception as e:
            logger.error("ComplaintService: Failed to get complaint.", exc_info=True)
            raise e

    async def get_complaint_by_tracking_id(self, tracking_id: str) -> Any:
        try:
            logger.info("ComplaintService: Getting complaint by tracking_id...")
            
            complaint = await self.complaint_repository.findByTrackingId(tracking_id)
            
            if not complaint:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Complaint not found"
                )
            
            logger.info(f"ComplaintService: Got complaint successfully: {complaint.tracking_id}")
            
            # Convert SQLAlchemy Complaint to Pydantic Complaint schema
            return ComplaintSchema.model_validate(complaint)
        
        except HTTPException:
            raise
        except Exception as e:
            logger.error("ComplaintService: Failed to get complaint by tracking_id.", exc_info=True)
            raise e

    async def create_complaint(self, complaint_data: ComplaintCreate, current_user: User = None) -> Any:
        try:
            logger.info("ComplaintService: Creating complaint...")
            
            # Generate tracking ID and add user_id from authenticated user
            complaint_dict = complaint_data.model_dump()
            complaint_dict["tracking_id"] = ComplaintModel.generate_tracking_id()
            complaint_dict["user_id"] = str(current_user.id)
            
            complaint = await self.complaint_repository.create(complaint_dict)
            logger.info(f"ComplaintService: Complaint created successfully: {complaint.tracking_id}")
            
            # Record business event
            self.prometheus.record_business_event("complaint_creation", "success")
            
            # Convert SQLAlchemy Complaint to Pydantic Complaint schema
            return ComplaintSchema.model_validate(complaint)
        
        except HTTPException:
            raise
        except Exception as e:
            logger.error("ComplaintService: Failed to create complaint.", exc_info=True)
            raise e

    async def update_complaint(self, complaint_id: str, complaint_data: ComplaintUpdate, current_user: User = None) -> Any:
        try:
            logger.info("ComplaintService: Updating complaint...")
            
            # Convert string to UUID if needed
            try:
                complaint_uuid = UUID(complaint_id) if isinstance(complaint_id, str) else complaint_id
            except ValueError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid complaint ID format"
                )
            
            # Check if complaint exists
            existing_complaint = await self.complaint_repository.findById(complaint_uuid)
            if not existing_complaint:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Complaint not found"
                )
            
            # Authorization check: non-admin users can only update their own complaints
            if current_user and current_user.role != Role.admin:
                if str(existing_complaint.user_id) != str(current_user.id):
                    raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN,
                        detail="You can only update your own complaints"
                    )
            
            # Prepare update data
            update_data = complaint_data.model_dump(exclude_unset=True)
            
            # Update complaint
            complaint = await self.complaint_repository.update(complaint_uuid, update_data)
            logger.info(f"ComplaintService: Complaint updated successfully: {complaint.tracking_id}")
            
            # Record business event
            self.prometheus.record_business_event("complaint_update", "success")
            
            # Convert SQLAlchemy Complaint to Pydantic Complaint schema
            return ComplaintSchema.model_validate(complaint)
        
        except HTTPException:
            raise
        except Exception as e:
            logger.error("ComplaintService: Failed to update complaint.", exc_info=True)
            raise e

    async def delete_complaint(self, complaint_id: str) -> Dict[str, Any]:
        try:
            logger.info("ComplaintService: Deleting complaint...")
            
            # Convert string to UUID if needed
            try:
                complaint_uuid = UUID(complaint_id) if isinstance(complaint_id, str) else complaint_id
            except ValueError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid complaint ID format"
                )
            
            # Check if complaint exists
            existing_complaint = await self.complaint_repository.findById(complaint_uuid)
            if not existing_complaint:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Complaint not found"
                )
            
            # Delete complaint
            result = await self.complaint_repository.delete(complaint_uuid)
            
            if not result:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Failed to delete complaint"
                )
            
            logger.info(f"ComplaintService: Complaint deleted successfully: {existing_complaint.tracking_id}")
            
            # Record business event
            self.prometheus.record_business_event("complaint_deletion", "success")
            
            return {"message": "Complaint deleted successfully"}
        
        except HTTPException:
            raise
        except Exception as e:
            logger.error("ComplaintService: Failed to delete complaint.", exc_info=True)
            raise e
