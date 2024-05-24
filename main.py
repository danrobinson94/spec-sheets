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
        pdf_blocks = []
        all_text = ""
        for page_num in range(len(pdf_document)):
            page = pdf_document[page_num]
            pdf_blocks.extend(page.get_text("blocks"))
            all_text += page.get_text("text")

        output_list = []

        for item in pdf_blocks:
            text = item[4].strip()  # Get the text part of the tuple

            # Check if the text starts with relevant sections or is a subsection (1.1-X or A. to Z.)
            if (
                text.startswith('PART') or 
                text.startswith(('1.', '2.', '3.', '4.', '5.', '6.', '7.', '8.', '9.')) or 
                (len(text) > 1 and text[0].isalpha() and text[1] == '.')
            ):
                # Additional filtering to exclude unwanted texts
                if not any(keyword in text for keyword in ['STANDBY', 'GENERATOR', '432.07.100', '02/2024']):
                    output_list.append(text)

        print(output_list)

        regex_pattern = r'(\d+\.\d+.*?)(?=\n\d+\.\d+|\Z)'
        section_pattern = r'(\d+\.\d+.*?)(?=\n\d+\.\d+|\n[A-Z]\.|$)'
        sub_section_pattern = r'([A-Z]\..*?)(?=\n[A-Z]\.|$)'
        sections = re.findall(section_pattern, all_text, re.DOTALL)

        sub_sections = []
        for sub_section in sections:
            sub_sections.append(re.findall(sub_section_pattern, sub_section, re.DOTALL))

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
