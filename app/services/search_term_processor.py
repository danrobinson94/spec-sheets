import json
from app.class_models import SearchTermInput
import spacy

# nlp = spacy.load("en_core_web_sm")

# TODO: Use later
def filter_keywords(text, search_term_input):
    answers = []
    for block in text:
        doc = nlp(block[1])
        for key in search_term_input.keywords:
            subkeys = search_term_input.sub_search_terms
            if key.lower() in doc.text.lower():
                answers.append([sub_kw for sub_kw in subkeys if sub_kw in doc.text])
    return []

async def process_sub_search_terms(search_term: SearchTermInput, pdf_with_ref, depth, title):
    try:
        pdf_blocks = []
        # Iterate through each array in the data
        for index, array in enumerate(pdf_with_ref):
            # Check if the second element contains the search term
            if depth == array[2]:
                return pdf_blocks
            if any(term in array[1].lower() for term in search_term.keywords):
                # Create a dictionary with 'header' and 'value' keys
                term_dict = {
                    'title': search_term.title,
                    'reference': array[0],
                    'value': array[1]
                }
                # Append the dictionary to the search_term_array list
                pdf_blocks.append(term_dict)
        return pdf_blocks
    except Exception as e:
        return {"error": str(e)}
    

async def process_search_terms(search_term: SearchTermInput, pdf_with_ref):
    try:
        pdf_blocks = []
        # Iterate through each array in the data
        for index, array in enumerate(pdf_with_ref):
            # Check if the second element contains the search term
            if any(term in array[1].lower() for term in search_term.keywords):
                # Create a dictionary with 'header' and 'value' keys
                term_dict = {
                    'title': search_term.title,
                    'reference': array[0],
                    'value': array[1]
                }
                # Append the dictionary to the search_term_array list
                pdf_blocks.append(term_dict)

                if search_term.subSearchTerms:
                    # Iterate through sub search terms
                    for sub_search_term in search_term.subSearchTerms:
                        # Recursively call process_search_terms with sub search term
                        sub_blocks = await process_sub_search_terms(sub_search_term, pdf_with_ref[index+1:], array[2], search_term.title)
                        # Extend the pdf_blocks list with the results from sub search
                        pdf_blocks.extend(sub_blocks)
        if len(pdf_blocks) == 0:
            empty_block = {
                    'title': search_term.title,
                    'reference': "NOT FOUND",
                    'value': ""
            }
            pdf_blocks.append(empty_block)
        return pdf_blocks
    except Exception as e:
        return {"error": str(e)}
