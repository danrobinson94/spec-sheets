import fitz  # PyMuPDF
import requests
import re
 

def extract_specifications_from_pdf(pdf_path, regex_pattern):

    """

    Extracts data based on a regex pattern from a given PDF file.

 

    :param pdf_path: Path to the PDF file.

    :param regex_pattern: Regular expression pattern to match the specifications.

    :return: A list of all matched specifications.

    """

    # Open the PDF file

    doc = fitz.open(pdf_path)

    text = ""

    # Extract text from each page

    for page in doc:

        text += page.get_text()

    for page in doc:
        ### SEARCH
        text2 = "warranty"
        text_instances = page.search_for(text2)

        ### HIGHLIGHT
        for inst in text_instances:
            highlight = page.add_highlight_annot(inst)
            highlight.update()

    ### OUTPUT
    doc.save("output.pdf", garbage=4, deflate=True, clean=True)

    doc.close()

   

    # Find all matches of the regex pattern

    matches = re.findall(regex_pattern, text, re.IGNORECASE | re.MULTILINE)

   

    return matches

 



# Example usage
#"263213generators.pdf"
pdf_path = "16815generator.pdf"

# Define your regex pattern here. Example pattern for matching something like a model number "Model XYZ1234"

regex_pattern = r'^.*warranty.*$'

matches = extract_specifications_from_pdf(pdf_path, regex_pattern)

 

print("Found specifications:", matches) # type: ignore