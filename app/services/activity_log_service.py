from typing import Optional, Dict, Any
from datetime import datetime

from fastapi import HTTPException, status

from app.schemas.activity_log_schema import ActivityLog, ActivityLogResponse
from app.di.container import container
import structlog
from dependency_injector.wiring import inject, Provide

logger = structlog.get_logger(__name__)


class ActivityLogService:
    @inject
    def __init__(
        self,
        activity_log_repository = Provide["activity_log_repository"],
        prometheus = Provide["prometheus"],
    ):
        self.activity_log_repository = activity_log_repository
        self.prometheus = prometheus
    
    async def get_activity_log(self, limit: int = 15) -> Dict[str, Any]:
        try:
            logger.info("ActivityLogService: Getting activity log...")
            
            # Validate limit
            if limit < 1 or limit > 50:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Limit must be between 1 and 50"
                )
            
            # Get recent logs
            logs = await self.activity_log_repository.findRecentLogs(limit=limit)
            
            # Convert to response format
            activity_responses = []
            for log in logs:
                # Extract time from timestamp (HH:MM format)
                time_str = log.timestamp.strftime("%H:%M")
                
                activity_responses.append(ActivityLogResponse(
                    text=log.text,
                    time=time_str,
                    timestamp=log.timestamp
                ))
            
            logger.info(f"ActivityLogService: Got activity log successfully. Total: {len(activity_responses)}")
            
            # Record business event
            self.prometheus.record_business_event("activity_log", "success")
            
            return {
                "success": True,
                "data": activity_responses
            }
        
        except HTTPException:
            raise
        except Exception as e:
            logger.error("ActivityLogService: Failed to get activity log.", exc_info=True)
            raise e
