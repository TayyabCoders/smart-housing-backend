"""
Upload Service for Cloudinary
"""
from fastapi import UploadFile
import cloudinary.uploader


class UploadService:

    async def upload_image(self, file: UploadFile):
        """Upload image to Cloudinary"""
        result = cloudinary.uploader.upload(
            file.file,
            folder="smart-housing"
        )

        return {
            "url": result["secure_url"],
            "public_id": result["public_id"]
        }
