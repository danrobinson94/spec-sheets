from transformers import AutoTokenizer, AutoModelForTokenClassification, TokenClassificationPipeline, pipeline
from transformers import logging
import re
import pprint

logging.set_verbosity_warning()

def expand_answer(answer, answer_start, answer_end, entities):
    expanded_answer = answer
    # Find the index of the answer words in the entities list
    start_index = next((i for i, e in enumerate(entities) if e['start'] == answer_start), None)
    end_index = next((i for i, e in enumerate(entities) if e['end'] == answer_end), None)
    
    if start_index is None or end_index is None:
        return answer  # If indices are not found, return the original answer
    
    # Expand the answer backwards until hitting an NN or the beginning of the list
    for i in range(start_index - 1, -1, -1):
        expanded_answer = entities[i]['word'] + " " + expanded_answer
        if entities[i]['entity_group'] == 'NN':
            break
    
    # Expand the answer forwards until hitting an NN or the end of the list
    i = end_index + 1
    while i < len(entities):
        expanded_answer = expanded_answer + " " + entities[i]['word']
        # Check if the next two tokens are POS and PRP$
        if i + 2 < len(entities) and entities[i + 1]['entity_group'] == 'POS' and entities[i + 2]['entity_group'] == 'PRP$':
            expanded_answer = expanded_answer + entities[i + 1]['word'] + entities[i + 2]['word']
            i += 3
            continue
        # Otherwise, check if the current token is NN
        elif entities[i]['entity_group'] == 'NN':
            break
        i += 1
    
    return expanded_answer

async def process_search_terms(search_terms: list[str], pdf_with_ref):
    paragraphs = []
    model_name = "deepset/roberta-base-squad2"

    nlp = pipeline('question-answering', model=model_name, tokenizer=model_name)
    model_name = "QCRI/bert-base-multilingual-cased-pos-english"
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForTokenClassification.from_pretrained(model_name)
    my_pipeline = TokenClassificationPipeline(model=model, tokenizer=tokenizer, aggregation_strategy="simple")

    for search_string in search_terms:
        print('SEARCH', search_string)
        results = [block for block in pdf_with_ref if re.search(search_string, block[1], re.IGNORECASE)]
        paragraphs.append({search_string: results})


        for answer in results:
            contexts = re.split(r'\.\s+(?=[A-Z])', answer[1])

            for context in contexts:
                QA_input = {
                    # Have variables come in and get put here. This is hard coded for an example we can show
                    'question': 'How long is the warranty period?',
                    # 'question': 'What does the warranty include?',
                    # 'question': 'What are the exceptions in the warranty? Also known as \'not acceptable\'',
                    'context': context
                    }
                res = nlp(QA_input)
                
                if res['score'] > 0.1:
                    pprint.pp(res)
                    outputs = my_pipeline(context)
                    expanded_answer = expand_answer(res['answer'], res['start'], res['end'], outputs)
                    print(expanded_answer)
                    print("---------------------------------------------------------------------------")

    return paragraphs

