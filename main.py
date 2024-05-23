from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
import os
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
        contents = await pdf_file.read()
        regex_pattern = r'^.*warranty.*$'
        processed_text = extract_specifications_from_pdf(contents, regex_pattern)

        # Process the PDF using the separate function

        # Clean up the temporary file
        os.remove(filename)

        return {"result": processed_text}
    except Exception as e:
        return {"error": str(e)}

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app)