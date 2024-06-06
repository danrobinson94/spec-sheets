import re
import pymupdf
from fastapi import UploadFile

async def process_pdf(pdf_file: UploadFile):
    try:
        file_content = await pdf_file.read()
        # search_terms = search_terms[0].split(',')

        pdf_document = pymupdf.open(stream=file_content, filetype="pdf")
        text = ""
        for page_num in range(len(pdf_document)):
            page = pdf_document[page_num]
            text += page.get_text("text")

        lvl_1 = r'\nPART\s+\d+\s' # PART 1 2 3 etc... 
        lvl_2 = r'\n\d+\.\d+\s+' # 1.1 1.2 2.1 2.2 etc...
        lvl_3 = r'\n[A-Z]\.\s+' # A. B. C. etc...
        lvl_4 = r'\n\d+\.\s+' # 1. 2. 3. etc...
        lvl_5 = r'\n[a-z]\.\s+' # a. b. c. etc...
        lvl_6 = r'\n\d+\)\s+' # 1) 2) 3) etc...
        lvl_7 = r'\n[a-z]\)\s+' # a) b) c) etc...
        lvls = [lvl_1, lvl_2, lvl_3, lvl_4, lvl_5, lvl_6, lvl_7]
        pattern_match = r'|'.join(lvls)

        pdf_layout = []
        reference = []
        ref_layout = {}
        ref_depth = 0
        while text:
            matches = re.findall(pattern_match, text)
            if len(matches) != 0:
                next_match = matches[0]
                #TODO: Watch for when the lvls are skipped
                #TODO: Still needs some fixes for typos and stuff
                for lvl in lvls:
                    if re.match(lvl, next_match):
                        next_match_lvl = lvls.index(lvl)
                        split_text = re.split(lvl, text, maxsplit=1)
                        pdf_layout.append([reference.copy(), split_text[0]])
                        text = next_match.join(split_text[1:])
                        ref_lvl = len(reference) - 1
                        while ref_lvl >= 0:
                            if next_match_lvl <= ref_lvl:
                                reference.pop()
                                ref_depth -= 1
                            ref_lvl -= 1
                        reference.append(next_match)
                        ref_depth += 1
                        ref_layout[next_match] = ref_depth
                        break
            else:
                pdf_layout.append([reference.copy(), text])
                break

        pdf_layout_with_ref = [[" -> ".join([ref.strip() for ref in string[0]]), string[1]] for string in pdf_layout]
        
        return pdf_layout_with_ref
    except Exception as e:
        return {"error": str(e)}