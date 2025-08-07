from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.responses import JSONResponse
from app.models.schemas import QARequest, QAResponse, ErrorResponse
from app.services.qa_service import QAService
from app.core.auth import verify_token
import logging
import asyncio
import time

logger = logging.getLogger(__name__)

router = APIRouter()

# Initialize QA service
qa_service = QAService()

@router.post("/hackrx/run", response_model=QAResponse)
async def run_qa(
    request: QARequest,
    token: str = Depends(verify_token)
) -> QAResponse:
    """
    Main endpoint for document question-answering
    """
    start_time = time.time()
    
    try:
        logger.info(f"Received QA request with {len(request.questions)} questions")
        logger.info(f"Document URL: {request.documents}")
        
        # Validate request
        if len(request.questions) > 10:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Maximum 10 questions allowed"
            )
        
        # Process request with timeout
        try:
            response = await asyncio.wait_for(
                qa_service.process_qa_request(request),
                timeout=30.0  # 30 second timeout
            )
            
            processing_time = time.time() - start_time
            logger.info(f"QA request completed in {processing_time:.2f} seconds")
            
            return response
            
        except asyncio.TimeoutError:
            logger.error("QA request timed out")
            raise HTTPException(
                status_code=status.HTTP_408_REQUEST_TIMEOUT,
                detail="Request timed out. Please try again with a smaller document or fewer questions."
            )
    
    except HTTPException:
        raise
    except ValueError as e:
        logger.error(f"Validation error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Unexpected error in QA endpoint: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error occurred while processing the request"
        )

@router.get("/health", response_model=dict)
async def health_check():
    """
    Health check endpoint
    """
    try:
        health_status = qa_service.get_health_status()
        
        if health_status["overall"] == "healthy":
            return JSONResponse(
                status_code=200,
                content=health_status
            )
        else:
            return JSONResponse(
                status_code=503,
                content=health_status
            )
    
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return JSONResponse(
            status_code=503,
            content={
                "overall": "unhealthy",
                "error": str(e)
            }
        )

@router.get("/status")
async def status_check():
    """
    Simple status endpoint
    """
    return {
        "status": "running",
        "service": "HackRx 6.0 Document QA API",
        "version": "1.0.0"
    }

# Note: Exception handlers should be added to the main FastAPI app, not router
