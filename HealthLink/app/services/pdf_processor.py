import requests
import fitz  # PyMuPDF
import logging
import tempfile
import os
from typing import List, Tuple
from app.models.schemas import DocumentChunk
from app.core.config import settings

logger = logging.getLogger(__name__)

class PDFProcessor:
    """
    Handles PDF downloading, text extraction, and chunking
    """
    
    def __init__(self):
        self.chunk_size = settings.CHUNK_SIZE
        self.chunk_overlap = settings.CHUNK_OVERLAP
        self.max_file_size = settings.MAX_FILE_SIZE
    
    async def download_pdf(self, url: str) -> bytes:
        """
        Download PDF from public URL
        """
        try:
            logger.info(f"Downloading PDF from: {url}")
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            response = requests.get(url, headers=headers, timeout=30, stream=True)
            response.raise_for_status()
            
            # Check content type
            content_type = response.headers.get('content-type', '').lower()
            if 'pdf' not in content_type and not url.lower().endswith('.pdf'):
                logger.warning(f"Content type might not be PDF: {content_type}")
            
            # Check file size
            content_length = response.headers.get('content-length')
            if content_length and int(content_length) > self.max_file_size:
                raise ValueError(f"File too large: {content_length} bytes")
            
            # Download content
            pdf_content = b''
            total_size = 0
            
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    total_size += len(chunk)
                    if total_size > self.max_file_size:
                        raise ValueError(f"File too large: {total_size} bytes")
                    pdf_content += chunk
            
            logger.info(f"Downloaded PDF: {total_size} bytes")
            return pdf_content
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to download PDF: {str(e)}")
            raise ValueError(f"Failed to download PDF: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error downloading PDF: {str(e)}")
            raise ValueError(f"Error downloading PDF: {str(e)}")
    
    def extract_text_from_pdf(self, pdf_content: bytes) -> List[Tuple[str, int]]:
        """
        Extract text from PDF content
        Returns list of (text, page_number) tuples
        """
        try:
            logger.info("Extracting text from PDF")
            
            # Create temporary file
            with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as temp_file:
                temp_file.write(pdf_content)
                temp_file_path = temp_file.name
            
            try:
                # Open PDF with PyMuPDF
                doc = fitz.open(temp_file_path)
                text_pages = []
                
                for page_num in range(len(doc)):
                    page = doc[page_num]
                    text = page.get_text()
                    
                    # Clean up text
                    text = self._clean_text(text)
                    
                    if text.strip():  # Only add non-empty pages
                        text_pages.append((text, page_num + 1))
                
                doc.close()
                logger.info(f"Extracted text from {len(text_pages)} pages")
                return text_pages
                
            finally:
                # Clean up temporary file
                if os.path.exists(temp_file_path):
                    os.unlink(temp_file_path)
                    
        except Exception as e:
            logger.error(f"Failed to extract text from PDF: {str(e)}")
            raise ValueError(f"Failed to extract text from PDF: {str(e)}")
    
    def _clean_text(self, text: str) -> str:
        """
        Clean extracted text
        """
        # Remove excessive whitespace
        text = ' '.join(text.split())
        
        # Remove special characters that might interfere
        text = text.replace('\x00', ' ')
        text = text.replace('\ufffd', ' ')
        
        return text.strip()
    
    def chunk_text(self, text_pages: List[Tuple[str, int]]) -> List[DocumentChunk]:
        """
        Split text into overlapping chunks
        """
        try:
            logger.info("Chunking text into segments")
            chunks = []
            chunk_id = 0
            
            for text, page_num in text_pages:
                words = text.split()
                
                # Create overlapping chunks
                for i in range(0, len(words), self.chunk_size - self.chunk_overlap):
                    chunk_words = words[i:i + self.chunk_size]
                    
                    if len(chunk_words) < 10:  # Skip very small chunks
                        continue
                    
                    chunk_text = ' '.join(chunk_words)
                    
                    chunk = DocumentChunk(
                        content=chunk_text,
                        chunk_id=chunk_id,
                        page_number=page_num
                    )
                    
                    chunks.append(chunk)
                    chunk_id += 1
            
            logger.info(f"Created {len(chunks)} text chunks")
            return chunks
            
        except Exception as e:
            logger.error(f"Failed to chunk text: {str(e)}")
            raise ValueError(f"Failed to chunk text: {str(e)}")
    
    async def process_pdf(self, url: str) -> List[DocumentChunk]:
        """
        Complete PDF processing pipeline
        """
        try:
            # Download PDF
            pdf_content = await self.download_pdf(url)
            
            # Extract text
            text_pages = self.extract_text_from_pdf(pdf_content)
            
            if not text_pages:
                raise ValueError("No text could be extracted from the PDF")
            
            # Chunk text
            chunks = self.chunk_text(text_pages)
            
            if not chunks:
                raise ValueError("No valid chunks could be created from the PDF")
            
            return chunks
            
        except Exception as e:
            logger.error(f"PDF processing failed: {str(e)}")
            raise
