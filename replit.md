# Overview

This is a Python-based Intelligent Document Question-Answering API built for HackRx 6.0. The system uses Google's Gemini Flash 1.5 model to extract and answer questions from PDF documents. Users can submit a public PDF URL along with natural language questions, and the API returns accurate answers extracted from the document using keyword-based search and AI-powered text analysis.

**Status: ✅ FULLY FUNCTIONAL** - API successfully deployed and tested with real PDF processing and question answering capabilities.

# User Preferences

Preferred communication style: Simple, everyday language.

# System Architecture

## Backend Framework
- **FastAPI**: Chosen for its high performance, automatic API documentation, and excellent async support
- **Python 3.x**: Primary programming language with strong AI/ML ecosystem support
- **Uvicorn**: ASGI server for production deployment

## AI/ML Components
- **Google Gemini 2.5 Flash**: Primary language model for question answering, selected for its fast inference and cost-effectiveness
- **Keyword-Based Search**: Lightweight text matching for document chunk retrieval (replaced heavy ML dependencies due to disk space constraints)
- **Text Chunking**: Simple overlap-based chunking for document processing

## Document Processing Pipeline
- **PyMuPDF (fitz)**: PDF text extraction with support for complex layouts
- **Text Chunking**: Documents split into 400-token chunks with 50-token overlap for optimal context preservation
- **Semantic Search**: Top-K retrieval (default 5 chunks) to find most relevant content for each question

## Security & Authentication
- **Bearer Token Authentication**: Simple token-based auth using SECRET_API_KEY
- **Input Validation**: Pydantic schemas for request/response validation
- **Rate Limiting**: Maximum 10 questions per request with 30-second timeout

## API Design
- **RESTful Architecture**: Single primary endpoint `/hackrx/run` for document QA
- **CORS Enabled**: Allows cross-origin requests for web frontend integration
- **Structured Responses**: Standardized JSON responses with error handling

## Configuration Management
- **Environment Variables**: Centralized config using Pydantic Settings
- **Configurable Parameters**: Chunk sizes, timeouts, and model settings easily adjustable

# External Dependencies

## AI/ML Services
- **Google Generative AI API**: Gemini Flash 1.5 model access (requires GEMINI_API_KEY)
- **Hugging Face**: Sentence Transformers model repository

## Core Libraries
- **FastAPI**: Web framework for API development
- **PyMuPDF**: PDF processing and text extraction
- **FAISS**: Vector similarity search library
- **Sentence Transformers**: Text embedding generation
- **Pydantic**: Data validation and settings management
- **Requests**: HTTP client for PDF download
- **NumPy**: Numerical operations for embeddings

## Development & Deployment
- **Uvicorn**: ASGI server for running the application
- **Python Logging**: Built-in logging for monitoring and debugging

## File Processing
- **Public PDF URLs**: System downloads PDFs from public URLs (max 50MB)
- **Temporary File Handling**: Safe PDF processing using temporary files
- **Content Type Validation**: Ensures downloaded content is PDF format