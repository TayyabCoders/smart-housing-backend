"""
Upload Controller
"""
from fastapi import UploadFile


class UploadController:

    def __init__(self, upload_mediator):
        self.upload_mediator = upload_mediator

    async def upload_image(self, file: UploadFile):
        return await self.upload_mediator.upload_image(file)
