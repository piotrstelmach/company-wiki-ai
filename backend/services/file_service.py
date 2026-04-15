from datetime import datetime
import os
import shutil
from typing import Annotated

from fastapi import Depends, UploadFile, BackgroundTasks
from sqlmodel import Session

from database import db_connection
from file_ingestor import FileIngestor
from models import UploadedFiles

UPLOAD_DIR = "storage"
os.makedirs(UPLOAD_DIR, exist_ok=True)


class IFileService:
    def process_file(self, file: UploadFile, background_tasks: BackgroundTasks, extra_data: dict) -> UploadedFiles:
        pass


class FileService(IFileService):
    def __init__(self, database: Session = Depends(db_connection)):
        self.database = database

    def process_file(self, file: UploadFile, background_tasks: BackgroundTasks, extra_data: dict) -> UploadedFiles:
        file_ingestor = FileIngestor()
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_filename = f"{timestamp}_{file.filename}"
        file_location = os.path.join(UPLOAD_DIR, safe_filename)

        with open(file_location, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        new_doc = UploadedFiles(
            filename=file.filename,
            file_path=file_location,
            chunk_count=0,
            status="processing"
        )

        self.database.add(new_doc)
        self.database.commit()
        self.database.refresh(new_doc)

        background_tasks.add_task(
            file_ingestor.process,
            new_doc.id,
            file_location,
            extra_data,
        )

        return new_doc


def get_file_service(database: Session = Depends(db_connection)) -> IFileService:
    return FileService(database)


FileServiceDep = Annotated[IFileService, Depends(get_file_service)]
