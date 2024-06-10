import json
from fastapi import APIRouter, Body, Form, UploadFile, File
from app.services.answer_processor import process_answers
from app.services.search_term_processor import process_search_terms
from app.utils.pdf_processor import process_pdf
from models import SearchTermInput, SearchTermOutput

router = APIRouter()

@router.post("/process")
async def process(search_terms: list[str] = Form(...), pdf_file: UploadFile = File(...)):
    # {"title": "test", "keywords": ["test"], "questions": ["Is this a test?"]} 
    search_terms = [SearchTermInput(**json.loads(item)) for item in search_terms]

    search_term_outputs = []
    processed_pdf = await process_pdf(pdf_file)
    for search_term in search_terms:
        processed_blocks = await process_search_terms(search_term, processed_pdf)
    #     processed_answers = await process_answers(processed_blocks, search_term.questions)
    #     search_term_outputs.append(SearchTermOutput(
    #         title=search_term.title,
    #         keywords=search_term.keywords,
    #         pdf_blocks=processed_answers
    #     ))

    # TODO: Uncomment this and fix it up soon, we're gonna need to dump some stuff eventually
    # final_array = json.dumps(result_arrays)
    # # Print the arrays containing the word 'warranty'
    # print('RESULT', final_array)
    # return {"result": final_array}
    return processed_blocks
