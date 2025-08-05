import logging
from typing import List
from google import genai
from google.genai import types
from app.core.config import settings
from app.services.pdf_processor import PDFProcessor
from app.services.embeddings import EmbeddingService
from app.models.schemas import QARequest, QAResponse

logger = logging.getLogger(__name__)

class QAService:
    """
    Main service for document question-answering using Gemini Flash 1.5
    """
    
    def __init__(self):
        self.pdf_processor = PDFProcessor()
        self.embedding_service = EmbeddingService()
        self._initialize_gemini()
    
    def _initialize_gemini(self):
        """
        Initialize Gemini client
        """
        try:
            if not settings.GEMINI_API_KEY:
                raise ValueError("GEMINI_API_KEY is required")
            
            self.client = genai.Client(api_key=settings.GEMINI_API_KEY)
            logger.info("Gemini client initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize Gemini client: {str(e)}")
            self.client = None
            raise ValueError(f"Failed to initialize Gemini client: {str(e)}")
    
    def _generate_answer(self, question: str, context: str) -> str:
        """
        Generate answer using Gemini Flash 1.5
        """
        try:
            prompt = f"""Answer the question using only the provided context.
If the answer is not in the context, reply "Not found in document".
Do not add any explanations, citations, or additional information.
Provide only the direct answer.

Context:
{context}

Question:
{question}

Answer:"""

            logger.info(f"Generating answer for question using Gemini")
            
            response = self.client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt,
                config=types.GenerateContentConfig(
                    temperature=0.1,  # Low temperature for consistent answers
                    max_output_tokens=200,  # Reasonable limit for answers
                )
            )
            
            if not response.text:
                logger.warning("Empty response from Gemini")
                return "Not found in document"
            
            answer = response.text.strip()
            
            # Clean up the answer
            if answer.lower().startswith("answer:"):
                answer = answer[7:].strip()
            
            logger.info("Answer generated successfully")
            return answer
            
        except Exception as e:
            logger.error(f"Failed to generate answer: {str(e)}")
            return "Not found in document"
    
    async def process_qa_request(self, request: QARequest) -> QAResponse:
        """
        Process the complete QA request
        """
        try:
            logger.info(f"Processing QA request with {len(request.questions)} questions")
            
            # Step 1: Process PDF
            chunks = await self.pdf_processor.process_pdf(request.documents)
            logger.info(f"PDF processed into {len(chunks)} chunks")
            
            # Step 2: Create vector index
            self.embedding_service.create_vector_index(chunks)
            logger.info("Vector index created")
            
            # Step 3: Process each question
            answers = []
            
            for i, question in enumerate(request.questions, 1):
                try:
                    logger.info(f"Processing question {i}/{len(request.questions)}")
                    
                    # Get relevant context
                    context = self.embedding_service.get_context_for_question(
                        question, 
                        top_k=settings.TOP_K_CHUNKS
                    )
                    
                    # Generate answer
                    answer = self._generate_answer(question, context)
                    answers.append(answer)
                    
                    logger.info(f"Question {i} processed successfully")
                    
                except Exception as e:
                    logger.error(f"Failed to process question {i}: {str(e)}")
                    answers.append("Not found in document")
            
            # Step 4: Clean up
            self.embedding_service.clear_index()
            
            logger.info(f"QA request completed with {len(answers)} answers")
            return QAResponse(answers=answers)
            
        except Exception as e:
            logger.error(f"QA request processing failed: {str(e)}")
            # Clean up on error
            self.embedding_service.clear_index()
            raise
    
    def get_health_status(self) -> dict:
        """
        Get service health status
        """
        try:
            # Test Gemini connection
            test_response = self.client.models.generate_content(
                model="gemini-2.5-flash",
                contents="Say 'OK' if you can read this."
            )
            
            gemini_status = "healthy" if test_response.text else "unhealthy"
            
        except Exception as e:
            logger.error(f"Gemini health check failed: {str(e)}")
            gemini_status = "unhealthy"
        
        return {
            "pdf_processor": "healthy",
            "embedding_service": "healthy",
            "gemini_client": gemini_status,
            "overall": "healthy" if gemini_status == "healthy" else "unhealthy"
        }
