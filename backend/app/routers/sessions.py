from fastapi import APIRouter, UploadFile, File, Form
from ..models import Session
from ..schemas import SessionCreate

router = APIRouter()

@router.post("/upload")
async def upload_session(
    file: UploadFile = File(...),
    driver_name: str = Form(...),
    car: str = Form(...),
    track: str = Form(...),
    duration: float = Form(...)
):
    # For now, just confirm receipt (later, upload to S3 + DB)
    return {
        "filename": file.filename,
        "driver_name": driver_name,
        "car": car,
        "track": track,
        "duration": duration,
    }
