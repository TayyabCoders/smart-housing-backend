"""
Upload Mediator
"""
from fastapi import UploadFile


class UploadMediator:

    def __init__(self, upload_service):
        self.upload_service = upload_service

    async def upload_image(self, file: UploadFile):
        return await self.upload_service.upload_image(file)
