from fastapi import APIRouter, UploadFile, File
from app.utils.pdf_processor import process_pdf

router = APIRouter()

@router.post("/process")
async def process(search_terms: list[str], pdf_file: UploadFile = File(...)):
    return await process_pdf(search_terms, pdf_file)
