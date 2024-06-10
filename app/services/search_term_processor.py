import json
from models import SearchTermInput

async def process_search_terms(search_term: SearchTermInput, pdf_with_ref):
    try:
        pdf_blocks = []
        # Iterate through each array in the data
        for array in pdf_with_ref:
            # Check if the second element contains the search term
            if any(term in array[1].lower() for term in search_term.keywords):
                # Create a dictionary with 'header' and 'value' keys
                term_dict = {
                    'reference': array[0],
                    'value': array[1]
                }
                # Append the dictionary to the search_term_array list
                pdf_blocks.append(term_dict)
        return pdf_blocks
    except Exception as e:
        return {"error": str(e)}
