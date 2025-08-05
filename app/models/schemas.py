from pydantic import BaseModel, Field, validator
from typing import List, Optional
import re

class QARequest(BaseModel):
    documents: str = Field(..., description="Public URL to PDF document")
    questions: List[str] = Field(..., min_length=1, max_length=10, description="List of questions to answer")
    
    @validator('documents')
    def validate_pdf_url(cls, v):
        if not v or not isinstance(v, str):
            raise ValueError("Document URL is required and must be a string")
        
        # Basic URL validation
        url_pattern = re.compile(
            r'^https?://'  # http:// or https://
            r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain...
            r'localhost|'  # localhost...
            r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
            r'(?::\d+)?'  # optional port
            r'(?:/?|[/?]\S+)$', re.IGNORECASE)
        
        if not url_pattern.match(v):
            raise ValueError("Invalid URL format")
        
        # Check if URL points to a PDF (optional, as some URLs might not have .pdf extension)
        if not (v.lower().endswith('.pdf') or 'pdf' in v.lower()):
            # Allow it but log a warning
            pass
            
        return v
    
    @validator('questions')
    def validate_questions(cls, v):
        if not v:
            raise ValueError("At least one question is required")
        
        if len(v) > 10:
            raise ValueError("Maximum 10 questions allowed")
        
        for i, question in enumerate(v):
            if not question or not question.strip():
                raise ValueError(f"Question {i+1} cannot be empty")
            
            if len(question.strip()) < 3:
                raise ValueError(f"Question {i+1} must be at least 3 characters long")
        
        return [q.strip() for q in v]

class QAResponse(BaseModel):
    answers: List[str] = Field(..., description="List of answers corresponding to questions")
    
class ErrorResponse(BaseModel):
    error: str = Field(..., description="Error message")
    details: Optional[str] = Field(None, description="Additional error details")
    status_code: int = Field(..., description="HTTP status code")

class DocumentChunk(BaseModel):
    content: str
    chunk_id: int
    page_number: Optional[int] = None
    embedding: Optional[List[float]] = None
