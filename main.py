from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
import os
import io
import pymupdf
import fitz
from routes.processPdf import extract_specifications_from_pdf

app = FastAPI()

frontend_url = os.environ.get("FRONTEND_PATH")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[frontend_url],  # Allow your frontend domain
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
        # contents = await pdf_file.read()
        file_content = await pdf_file.read()
    
    # Open the PDF from bytes using PyMuPDF
        pdf_document = pymupdf.open(stream=file_content, filetype="pdf")
        
        # Process the PDF as needed
        # For example, extracting text from the first page
        first_page = pdf_document[0]
        text = first_page.get_text("text")
        # processed_text = extract_specifications_from_pdf(contents, regex_pattern)

        # Process the PDF using the separate function

        # Clean up the temporary file
        os.remove(filename)

        return {"result": text}
    except Exception as e:
        return {"error": str(e)}

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app)