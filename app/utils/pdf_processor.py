import re
import pymupdf
from fastapi import UploadFile

async def process_pdf(search_terms: list[str], pdf_file: UploadFile):
    try:
        file_content = await pdf_file.read()
        search_terms = search_terms[0].split(',')

        pdf_document = pymupdf.open(stream=file_content, filetype="pdf")
        pdf_blocks = []
        for page_num in range(len(pdf_document)):
            page = pdf_document[page_num]
            pdf_blocks.extend(page.get_text("blocks"))

        output_list = []

        for item in pdf_blocks:
            text = item[4].strip()  # Get the text part of the tuple

            if (
                text.startswith('PART') or 
                text.startswith(('1.', '2.', '3.', '4.', '5.', '6.', '7.', '8.', '9.')) or 
                (len(text) > 1 and text[0].isalpha() and text[1] == '.')
            ):
                if not any(keyword in text for keyword in ['STANDBY', 'GENERATOR', '432.07.100', '02/2024']):
                    output_list.append(text)
        
        paragraphs = []
        for search_string in search_terms:
            answer = [para for para in output_list if re.search(search_string, para, re.IGNORECASE)]
            paragraphs.append({search_string: answer})

        return {"result": paragraphs}
    except Exception as e:
        return {"error": str(e)}
