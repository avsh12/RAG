import os
from pathlib import Path

from fastapi import UploadFile


def validate_file(file: UploadFile, max_file_size_bytes):
    status = {"valid": True, "errors": []}
    extensions = {".txt", ".pdf", ".md", ".mdx"}
    filename = Path(file.filename)
    # file exists
    if filename == "":
        status["valid"] = False
        status["errors"].append("No file selected")

    # file extension
    file_extension = filename.suffix.lower()
    if file_extension not in extensions:
        status["valid"] = False
        status["errors"].append("Unsupported file")

    # file size
    file.file.seek(0, os.SEEK_END)
    file_size = file.file.tell()
    file.file.seek(0)

    if file_size <= 0:
        status["valid"] = False
        status["errors"].append("File is empty")
    elif file_size > max_file_size_bytes:
        status["valid"] = False
        status["errors"].append(
            f"File exceeds {max_file_size_bytes/(10*1024*1024)}MB limit"
        )

    return status
