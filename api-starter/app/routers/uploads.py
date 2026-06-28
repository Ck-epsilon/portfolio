# Author: Ck.epsilon
"""File upload router — simple local file storage with size validation."""

import os
import uuid

from fastapi import APIRouter, Depends, HTTPException, UploadFile, status

from app.auth.dependencies import get_current_user
from app.config import settings
from app.models.user import User

router = APIRouter(prefix="/upload", tags=["Files"])

UPLOAD_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "uploads")
MAX_SIZE_MB = 10


@router.post("/")
async def upload_file(
    file: UploadFile,
    current_user: User = Depends(get_current_user),
) -> dict:
    """Upload a file. Requires authentication. Max 10 MB."""
    content = await file.read()
    if len(content) > MAX_SIZE_MB * 1024 * 1024:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File exceeds {MAX_SIZE_MB} MB limit",
        )

    os.makedirs(UPLOAD_DIR, exist_ok=True)
    ext = os.path.splitext(file.filename or "file")[1]
    safe_name = f"{uuid.uuid4().hex}{ext}"
    filepath = os.path.join(UPLOAD_DIR, safe_name)

    with open(filepath, "wb") as f:
        f.write(content)

    return {
        "filename": file.filename,
        "saved_as": safe_name,
        "size_bytes": len(content),
        "uploaded_by": current_user.username,
    }
