from fastapi import APIRouter, UploadFile, File
from app.utils.pdf_processor import process_pdf

router = APIRouter()

@router.post("/process")
async def process(pdf_file: UploadFile = File(...)):
    return await process_pdf(pdf_file)
