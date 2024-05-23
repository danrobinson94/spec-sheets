from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
import os
import io
import re
import pymupdf
import fitz
from routes.processPdf import extract_specifications_from_pdf

app = FastAPI()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Allow your frontend domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.post("/process")
async def process(pdf_file: UploadFile = File(...)):
    """Uploads and processes a PDF file.

    Args:
        pdf_file (UploadFile): The uploaded PDF file.

    Returns:
        dict: A dictionary containing the processing result or error message.
    """
    try:
        # Save the uploaded file temporarily
        filename = pdf_file.filename
        file_content = await pdf_file.read()
    
    # Open the PDF from bytes using PyMuPDF
        pdf_document = pymupdf.open(stream=file_content, filetype="pdf")
        # first_page = pdf_document[0]
        # text = first_page.get_text("text")
        all_text = ""
        for page_num in range(len(pdf_document)):
            page = pdf_document[page_num]
            all_text += page.get_text("text")
        # regex_pattern = r'^.*warranty.*$'
        # # return the data from the pdf
        # matches = re.findall(regex_pattern, all_text, re.IGNORECASE | re.MULTILINE)
        # processed_text = extract_specifications_from_pdf(contents, regex_pattern)
        regex_pattern = r'(\d+\.\d+.*?)(?=\n\d+\.\d+|\Z)'
        
        # Find all paragraphs
        paragraphs = re.findall(regex_pattern, all_text, re.DOTALL)
        
        # Filter paragraphs containing the word "warranty"
        warranty_paragraphs = [para for para in paragraphs if re.search(r'cummins', para, re.IGNORECASE)]

        print(warranty_paragraphs)

        return {"result": warranty_paragraphs}
    except Exception as e:
        return {"error": str(e)}

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app)