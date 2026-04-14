import logging
import os
import shutil
import uuid
from pathlib import Path
from typing import Annotated

from api.routers.auth import User, authenticate_api
from api.utils.file_validation import validate_file
from api.utils.util import get_rag_engine
from fastapi import (
    APIRouter,
    BackgroundTasks,
    Depends,
    File,
    HTTPException,
    UploadFile,
    status,
)
from rag.pipeline.pipeline import RAG
from rag.utils.config import settings

router = APIRouter(tags=["File Uploading"])


def generate_filename(filename: Path) -> Path:
    filename = filename
    file_extension = filename.suffix.lower()
    original_name = filename.stem

    filename = Path(f"{uuid.uuid4()}_{original_name}{file_extension}")
    return filename


@router.post("/file")
def save_file(
    background_tasks: BackgroundTasks,
    rag: Annotated[RAG, Depends(get_rag_engine)],
    user: Annotated[User, Depends(authenticate_api)],
    file: UploadFile = File(),
):
    validation_status = validate_file(file, settings.MAX_FILE_SIZE_BYTES)

    if not validation_status["valid"]:
        raise HTTPException(status_code=400, detail=validation_status["errors"])

    filename = Path(file.filename)
    filename = generate_filename(filename)

    db_path = settings.OBJ_FILE_DB_PATH

    filepath = db_path / filename
    print(f"FILEPATH: {filepath.absolute()}")
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

    background_tasks.add_task(rag.ingest, user.client_id, filepath)

    return {
        "message": "File uploaded successfully!",
        "file name": file.filename,
        "content type": file.content_type,
    }
