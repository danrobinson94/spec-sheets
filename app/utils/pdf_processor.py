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
        current_section = []

        for item in pdf_blocks:
            text = item[4].strip()  # Get the text part of the tuple
            # output_list.append((current_section, text))
            section_value = re.split(r'[\s\n]+', text)[0]
            length = len(current_section)
            if section_value.startswith("PART"):
                current_section = []
                current_section.append(section_value + " " + re.split(r'[\s\n]+', text)[1])
            elif length == 0:
                continue
            elif re.match(r'^\d+', section_value) and re.match(r'^\d', current_section[length-1]):
                current_section = current_section[:length-1]
                current_section.append(section_value)
            elif re.match(r'^[A-Za-z]', section_value) and re.match(r'^[A-Za-z]', current_section[length-1]):
                current_section = current_section[:length-1]
                current_section.append(section_value)
            
            else:
                current_section.append(section_value)

            print(current_section)
        paragraphs = []
        for search_string in search_terms:
            answer = [ {"section": section, "text": para} for section, para in output_list if re.search(search_string, para, re.IGNORECASE)]
            paragraphs.append({search_string: answer})

        return {"result": paragraphs}
    except Exception as e:
        return {"error": str(e)}
