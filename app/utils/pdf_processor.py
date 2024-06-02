import re
import pymupdf
from fastapi import UploadFile

async def process_pdf(search_terms: list[str], pdf_file: UploadFile):
    try:
        file_content = await pdf_file.read()
        search_terms = search_terms[0].split(',')

        pdf_document = pymupdf.open(stream=file_content, filetype="pdf")
        # pdf_blocks will store each individual line of text in the pdf
        pdf_blocks = []
        # all_text = ""
        for page_num in range(len(pdf_document)):
            page = pdf_document[page_num]
            pdf_blocks.extend(page.get_text("blocks"))
            # all_text += page.get_text("text")

        def parse_pdf_array(pdf_array):
            structure = []
            index = 0
            length = len(pdf_array)
            
            def parse_section(path):
                nonlocal index
                current_path = path.copy()
                while index < length:
                    pdf_line = pdf_array[index]
                    text = pdf_line[4]
                    x1_position = pdf_line[0]
                    part_match = re.match(r'PART\s+(\d+)(.*)', text) # PART 1 2 3 etc...
                    frac_number_dot_match = re.match(r'(\d+\.\d+)(.*)', text) # 1.1 1.2 2.1 2.2 etc...
                    frac_number_paren_match = re.match(r'(\d+\.\d+)\)(.*)') # 1.1) 1.2) 2.1) 2.2) etc...
                    whole_number_dot_match = re.match(r'(\d+)\.(.*)', text) # 1. 2. 3. etc...
                    whole_number_paren_match = re.match(r'(\d+)\)(.*)', text) # 1) 2) 3) etc... 
                    letter_dot_match = re.match(r'([A-Za-z])\.(.*)', text) # A. B. C. a. b. c. etc...
                    letter_paren_match = re.match(r'([A-Za-z])\)(.*)', text) # A) B) C) a) b) c) etc...
                    # Roman Numerals???

                    # If x1_position is equal and the match is true --> Bubble Up and add current value (Part 1, 1.1) --> (Part 1, 1.2)
                    # If x1_position is equal and the match is false --> I think this is an error?
                    # If x1_position is less and the match is true --> I also think this is an error?
                    # If x1_position is less and the match is false --> Bubble Up twice and replace with current value (Part 1, 1.1) --> (Part 2)
                    # If x1_position is more and the match is true --> I also think this is an error?
                    # If x1_position is more and the match is false --> Bubble Down and add current value (Part 1) --> (Part 1, 1.1)
                    
                    if part_match:
                        if current_path:
                            return
                        current_path = [f"PART {part_match.group(1)} {part_match.group(2)}"]
                        structure.append((current_path, text))
                        index += 1
                        parse_section(current_path)
                    elif section_match and current_path:
                        if len(current_path) > 1 and not current_path[-1].isdigit():
                            return
                        current_path = path + [section_match.group(1)]
                        structure.append((current_path, text))
                        index += 1
                        parse_section(current_path)
                    elif subsection_match and current_path:
                        if len(current_path) > 2 and current_path[-1].isalpha():
                            return
                        current_path = path + [subsection_match.group(1)]
                        structure.append((current_path, text))
                        index += 1
                        parse_section(current_path)
                    elif subsubsection_match and current_path:
                        if len(current_path) > 3 and current_path[-1].isdigit():
                            return
                        current_path = path + [subsubsection_match.group(1)]
                        structure.append((current_path, text))
                        index += 1
                        parse_section(current_path)
                    else:
                        if current_path:
                            structure.append((current_path, text))
                        index += 1

            parse_section([])
            return structure

        # Parse the PDF array
        pdf_structure = parse_pdf_array(pdf_blocks)

        # Print the structured array
        for item in pdf_structure:
            print(item)

        def search_structure(structure, keyword):
            results = []
            for path, text in structure:
                if keyword.lower() in text.lower():
                    results.append(path)
            return results

        # Search for the keyword
        keyword = "cummins"
        search_results = search_structure(pdf_structure, keyword)

        # Print the results
        for result in search_results:
            print(result)

        # output_list = []

        # for item in pdf_blocks:
        #     text = item[4].strip()  # Get the text part of the tuple

        #     if (
        #         text.startswith('PART') or 
        #         text.startswith(('1.', '2.', '3.', '4.', '5.', '6.', '7.', '8.', '9.')) or 
        #         (len(text) > 1 and text[0].isalpha() and text[1] == '.')
        #     ):
        #         if not any(keyword in text for keyword in ['STANDBY', 'GENERATOR', '432.07.100', '02/2024']):
        #             output_list.append(text)

        regex_pattern = r'(\d+\.\d+.*?)(?=\n\d+\.\d+|\Z)'
        # section_pattern = r'(\d+\.\d+.*?)(?=\n\d+\.\d+|\n[A-Z]\.|$)'
        # sub_section_pattern = r'([A-Z]\..*?)(?=\n[A-Z]\.|$)'
        # sections = re.findall(section_pattern, all_text, re.DOTALL)

        # sub_sections = []
        # for sub_section in sections:
        #     sub_sections.append(re.findall(sub_section_pattern, sub_section, re.DOTALL))

        paragraphs = re.findall(regex_pattern, all_text, re.DOTALL)
        
        paragraphs2 = []
        for search_string in search_terms:
            print('SEARCH', search_string)
            answer = [para for para in paragraphs if re.search(search_string, para, re.IGNORECASE)]
            paragraphs2.append({search_string: answer})

        return {"result": paragraphs2}
    except Exception as e:
        return {"error": str(e)}
