import logging
import os
import shutil
import uuid
from pathlib import Path
from typing import Annotated

from fastapi import APIRouter, File, HTTPException, UploadFile, status

from .file_validation import validate_file


def generate_filename(filename: Path) -> Path:
    filename = filename
    file_extension = filename.suffix.lower()
    original_name = filename.stem

    filename = f"{uuid.uuid4()}_{original_name}{file_extension}"
    return filename


router = APIRouter(tags=["File Uploading"])


@router.post("/file")
def save_file(file: UploadFile = File()):
    # 10MB limit
    MAX_FILE_SIZE_BYTES = 10 * 1024 * 1024
    validation_status = validate_file(file, MAX_FILE_SIZE_BYTES)

    if not validation_status["valid"]:
        raise HTTPException(status_code=400, detail=validation_status["errors"])

    filename = Path(file.filename)
    filename = generate_filename(filename)

    db_path = Path("data/user/")
    db_path.mkdir(parents=True, exist_ok=True)

    filepath = db_path / filename
    try:
        with open(filepath, "wb") as f:
            shutil.copyfileobj(file.file, f)
    except Exception as e:
        logging.error(f"Failed to save file: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="There was an error uploading the file.",
        )
    finally:
        file.file.close()

    return {
        "message": "File uploaded successfully!",
        "file name": file.filename,
        "content type": file.content_type,
    }
