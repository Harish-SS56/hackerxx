# HackRx 6.0 - Document QA API

A Python-based Intelligent Document Question-Answering API using Google's Gemini Flash 1.5.

## Features

✅ **PDF Processing**: Downloads and extracts text from public PDF URLs  
✅ **AI-Powered Q&A**: Uses Gemini Flash 1.5 for intelligent question answering  
✅ **Multiple Questions**: Handle up to 10 questions per request  
✅ **Bearer Authentication**: Secure API access with token authentication  
✅ **FastAPI Framework**: High-performance async API with automatic documentation  
✅ **Error Handling**: Robust error handling and validation  

## Installation

### Local Installation

1. **Clone or download the project**
2. **Create virtual environment**:
   ```bash
   python -m venv .venv
   .venv\Scripts\activate  # Windows
   # or
   source .venv/bin/activate  # Linux/Mac
   ```

3. **Install dependencies**:
   ```bash
   pip install -e .
   ```

4. **Set up environment variables**:
   Create a `.env` file with:
   ```
   GEMINI_API_KEY=your-gemini-api-key-here
   SECRET_API_KEY=hackrx-secret-key-2024
   ```

5. **Run the server**:
   ```bash
   python main.py
   ```

The API will be available at `http://localhost:5000`

## API Usage

### Authentication
```
Authorization: Bearer hackrx-secret-key-2024
Content-Type: application/json
```

### Request Format
```json
{
  "documents": "https://example.com/document.pdf",
  "questions": [
    "What is this document about?",
    "What are the main topics?"
  ]
}
```

### Response Format
```json
{
  "answers": [
    "This document is about...",
    "The main topics are..."
  ]
}
```

## Testing with Postman

1. Create a POST request to `http://localhost:5000/hackrx/run`
2. Add headers:
   - `Authorization: Bearer hackrx-secret-key-2024`
   - `Content-Type: application/json`
3. Use the request format shown above

## API Endpoints

- `POST /hackrx/run` - Main QA endpoint
- `GET /health` - Health check
- `GET /status` - Simple status check
- `GET /` - Root endpoint

## Requirements

- Python 3.11+
- Gemini API Key (free from Google AI Studio)
- Public PDF URLs (max 50MB)

## Architecture

- **FastAPI**: High-performance web framework
- **Google Gemini 2.5 Flash**: AI language model
- **PyMuPDF**: PDF text extraction
- **Keyword Search**: Lightweight text matching for relevant chunks