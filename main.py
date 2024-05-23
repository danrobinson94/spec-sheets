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
    print('STARTING')
    """Uploads and processes a PDF file.

    Args:
        pdf_file (UploadFile): The uploaded PDF file.

    Returns:
        dict: A dictionary containing the processing result or error message.
    """
    try:
        # Save the uploaded file temporarily
        filename = pdf_file.filename
        print(filename)
        contents = await pdf_file.read()
        with open(f"{filename}", "wb") as buffer:
            buffer.write(contents)  # Corrected to write the contents of the file

        regex_pattern = r'^.*warranty.*$'
        # Process the PDF using the separate function
        processed_text = extract_specifications_from_pdf(open(filename, "rb").read(), regex_pattern)

        # Clean up the temporary file
        os.remove(filename)

        return {"result": processed_text}
    except Exception as e:
        return {"error": str(e)}
