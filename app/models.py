from pydantic import BaseModel

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
    questions: list[str]

class SearchTermOutput(BaseModel):
    title: str
    keywords: list[str]
    pdf_blocks: list[PDFBlocks]
