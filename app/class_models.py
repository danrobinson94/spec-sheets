from pydantic import BaseModel
from typing import Optional

class QAs(BaseModel):
    question: str
    answer: str

class PDFBlocks(BaseModel):
    reference: str
    answers: list[QAs]
    value: str

class SearchTermInput(BaseModel):
    title: str
    keywords: list[str]
    subSearchTerms: Optional[list['SearchTermInput']] = []

class SearchTermOutput(BaseModel):
    title: str
    keywords: list[str]
    pdf_blocks: list[PDFBlocks]

SearchTermInput.model_rebuild()