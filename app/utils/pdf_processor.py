import re
import pymupdf
from fastapi import UploadFile

def extract_text_with_coords(doc):
    text_with_coords = []
    
    for page_num in range(len(doc)):
        page = doc[page_num]
        blocks = page.get_text("dict")["blocks"]
        
        for block in blocks:
            if block['type'] == 0:  # Text block
                for line in block["lines"]:
                    span_texts = []
                    for span in line["spans"]:
                        span_texts.append(span["text"])
                        x0, y0, x1, y1 = span["bbox"]
                        text_with_coords.append((span["text"], page_num, (x0, y0, x1, y1)))
                    
    return text_with_coords

def clean_text_with_coords(text_with_cords):
    new_text_with_coords = []

    i = 0
    while i < len(text_with_cords) - 1:
        ref = text_with_cords[i]
        next_ref = text_with_cords[i + 1]
        if abs(ref[2][1] - next_ref[2][1]) < 10:
            new_coord = (ref[2][0], ref[2][1], next_ref[2][2], next_ref[2][3])
            new_string = ref[0] + next_ref[0]
            text_with_cords[i] = (new_string, ref[1], new_coord)
            del text_with_cords[i+1]
        else:
            new_text_with_coords.append((ref[0].strip(), ref[1], ref[2]))
            i += 1
    return new_text_with_coords

def combine_lines(pdf_layout):
    final_layout = []

    i = 0
    ref = None
    while i < len(pdf_layout) - 1:
        ref = pdf_layout[i]
        next_ref = pdf_layout[i + 1]
        if ref[0] == next_ref[0]:
            new_coord = (ref[1][0], ref[1][1], next_ref[1][2], next_ref[1][3])
            new_string = ref[2] + "\n" + next_ref[2]
            pdf_layout[i] = [ref[0], new_coord, new_string, next_ref[3], next_ref[4]]
            del pdf_layout[i+1]
        else:
            final_layout.append(ref)
            i += 1
    final_layout.append(ref)
    return final_layout

def join_refs(pdf_layout):
    for index, block in enumerate(pdf_layout):
        ref_string = ""
        ref_annot = ""
        for ref in block[0]:
            ref_string += ref[0] + " --> "
            ref_annot += ref[0] + " --> " + ref[1] + " \n"
        pdf_layout[index] = [ref_string[:-4].strip(), block[1], block[2].strip(), block[3], block[4], ref_annot.strip()]

    return pdf_layout


async def process_pdf(pdf_file: UploadFile):
    try:
        part = r'PART\s+\d{1,2}(?:\s+|$)' # PART 1 2 3 etc...
        section = r'SECTION\s+(?:[IVXLCDM]+)(?:\s+|$)' # SECTION I II III etc...
        digit_dot_digit_header = r'\d{1,2}\.0{1,2}(?:\s+|$)' # 1.0 2.0 3.0 etc...
        digit_dot_digit = r'\d{1,2}\.\d{1,2}(?:\s+|$)' # 1.1 1.2 2.1 2.2 etc...
        digit_dot_digit_2 = r'\d{1,2}\.\d{1,2}\.\d{1,2}(?:\s+|$)' # 1.1.1 1.2.1 2.1.1 etc...
        digit_dot_digit_3 = r'\d{1,2}\.\d{1,2}\.\d{1,2}\.\d{1,2}(?:\s+|$)' # 1.1.1.1 1.1.1.2 1.1.1.3 etc...
        digit_dot = r'\d{1,2}\.(?:\s+|$)' # 1. 2. 3. etc...
        digit_paren = r'\d{1,2}\)(?:\s+|$)' # 1) 2) 3) etc...
        letter_u_dot = r'[A-Z]\.(?:\s+|$)' # A. B. C. etc...
        letter_l_dot = r'[a-z]\.(?:\s+|$)' # a. b. c. etc...
        letter_u_paren = r'[A-Z]\)(?:\s+|$)' # A) B) C) etc...
        letter_l_paren = r'[a-z]\)(?:\s+|$)' # a) b) c) etc...
        sections = [part, section, digit_dot_digit_header, digit_dot_digit, digit_dot_digit_2, digit_dot_digit_3, digit_dot,
                 digit_paren, letter_u_dot, letter_l_dot, letter_u_paren, letter_l_paren]

        file_content = await pdf_file.read()
        pdf_document = pymupdf.open(stream=file_content, filetype="pdf")
        pdf_layout = []
        reference = []
        ref_section = []
        ref_layout = {}
        ref_depth = 0

        text_with_coords = extract_text_with_coords(pdf_document)
        text_with_coords = clean_text_with_coords(text_with_coords)

        for line in text_with_coords:
            match_found = False
            line_text = line[0]
            page_num = line[1]
            line_coords = line[2]
            #TODO: Still needs some fixes for typos and stuff
            for section in sections:
                match = re.match(section, line_text)
                if match:
                    match_end = match.regs[0][1]
                    if section not in ref_layout:
                        ref_depth += 1
                        reference.append([line_text[:match_end].strip(), line_text[match_end:]])
                        ref_section.append(section)
                        ref_layout[section] = ref_depth
                    prev_ref = re.match(section, reference[len(reference)-1][0])
                    if prev_ref:
                        reference[len(reference)-1] = [line_text[:match_end].strip(), line_text[match_end:]]
                        ref_section[len(ref_section)-1] = section
                    else:
                        while len(reference) > 0:
                            prev_ref = re.match(section, reference[len(reference)-1][0])
                            if prev_ref:
                                reference[len(reference)-1] = [line_text[:match_end].strip(), line_text[match_end:]]
                                ref_section[len(ref_section)-1] = section
                                break
                            ref_depth -= 1
                            del ref_layout[ref_section[len(ref_section)-1]]
                            reference.pop()
                            ref_section.pop()
                    split_text = re.split(section, line_text, maxsplit=1)
                    pdf_layout.append([reference.copy(), line_coords, split_text[1], ref_depth, page_num])
                    match_found = True
                    break
            if not match_found:
                pdf_layout.append([reference.copy(), line_coords, line_text, ref_depth, page_num])

        pdf_layout = combine_lines(pdf_layout)

        pdf_layout = join_refs(pdf_layout)

        return pdf_layout
    except Exception as e:
        return {"error": str(e)}