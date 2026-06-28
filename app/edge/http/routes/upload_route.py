"""
Upload Route
"""
from fastapi import APIRouter, UploadFile, File, Depends
from app.di.container import container

router = APIRouter(
    prefix="/upload",
    tags=["Upload"]
)


@router.post("/")
async def upload_image(
    file: UploadFile = File(...),
    upload_controller = Depends(lambda: container.resolve('upload_controller'))
):
    result = await upload_controller.upload_image(file)
    return {
        "success": True,
        "message": "Image uploaded successfully",
        "data": result
    }
