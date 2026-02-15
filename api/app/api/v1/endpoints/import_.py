from typing import Annotated

from fastapi import APIRouter, Depends, File, UploadFile, status
from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.db.session import get_db
from app.exceptions import BadRequestError, InternalServerError
from app.models.user import User
from app.schemas.import_schema import ImportResponse
from app.services.import_service import ImportService

router = APIRouter()


async def get_import_service(
    db: Annotated[AsyncSession, Depends(get_db)],
) -> ImportService:
    return ImportService(db)


@router.post("/excel", response_model=ImportResponse, status_code=status.HTTP_200_OK)
async def import_excel_file(
    file: Annotated[UploadFile, File()],
    service: Annotated[ImportService, Depends(get_import_service)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    if not file.filename or not file.filename.endswith((".xlsx", ".xls")):
        raise BadRequestError(detail="File must be an Excel file (.xlsx or .xls)")

    try:
        result = await service.import_excel(file.file, current_user.id)
        return result
    except Exception as e:
        logger.error(f"Failed to process Excel file: {str(e)}")
        raise InternalServerError(
            detail=f"Failed to process Excel file: {str(e)}"
        ) from e
