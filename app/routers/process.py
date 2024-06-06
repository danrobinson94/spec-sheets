from fastapi import APIRouter, UploadFile, File
from app.services.search_term_processor import process_search_terms
from app.utils.pdf_processor import process_pdf

router = APIRouter()

@router.post("/process")
async def process(search_terms: list[str], pdf_file: UploadFile = File(...)):
    processed_pdf = await process_pdf(pdf_file)
    processed_terms = await process_search_terms(search_terms, processed_pdf)
    return processed_terms
