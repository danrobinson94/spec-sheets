from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
import os
import re
import pymupdf
import uvicorn

app = FastAPI()

frontend_url = os.environ.get("FRONTEND_PATH", 'http://localhost:3000')

app.add_middleware(
    CORSMiddleware,
    allow_origins=[frontend_url],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.post("/process")
async def process(search_terms: list[str], pdf_file: UploadFile = File(...)):
    try:
        file_content = await pdf_file.read()
        search_terms = search_terms[0].split(',')

        pdf_document = pymupdf.open(stream=file_content, filetype="pdf")
        all_text = ""
        for page_num in range(len(pdf_document)):
            page = pdf_document[page_num]
            all_text += page.get_text("text")

        regex_pattern = r'(\d+\.\d+.*?)(?=\n\d+\.\d+|\Z)'
        paragraphs = re.findall(regex_pattern, all_text, re.DOTALL)
        
        paragraphs2 = []
        for search_string in search_terms:
            answer = [para for para in paragraphs if re.search(search_string, para, re.IGNORECASE)]
            paragraphs2.append({search_string: answer})

        return {"result": paragraphs2}
    except Exception as e:
        return {"error": str(e)}

if __name__ == '__main__':
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port, reload=True)
