# HackRx 6.0 - Postman Testing Guide

## API Endpoint

**Base URL:** `https://your-deployment-url.replit.app`
**Endpoint:** `POST /hackrx/run`

## Authentication

**Type:** Bearer Token

```
Authorization: Bearer hackrx-secret-key-2024
Content-Type: application/json
```

## Test Cases

### Test Case 1: Single Question
```json
{
  "documents": "https://www.adobe.com/content/dam/acom/en/devnet/acrobat/pdfs/pdf_reference_1-7.pdf",
  "questions": [
    "What is this document about?"
  ]
}
```

**Expected Response:**
```json
{
  "answers": [
    "Acrobat Developer Docs"
  ]
}
```

### Test Case 2: Multiple Questions
```json
{
  "documents": "https://www.adobe.com/content/dam/acom/en/devnet/acrobat/pdfs/pdf_reference_1-7.pdf",
  "questions": [
    "What is this document about?",
    "What programming resources are mentioned?",
    "What APIs are available?"
  ]
}
```

**Expected Response:**
```json
{
  "answers": [
    "Acrobat Developer Docs",
    "Acrobat and PDFL SDKs, Document Services APIs, Document Services SDK, PDF Services API",
    "Document Services APIs and PDF Services API"
  ]
}
```

### Test Case 3: Maximum Questions (10)
```json
{
  "documents": "https://www.adobe.com/content/dam/acom/en/devnet/acrobat/pdfs/pdf_reference_1-7.pdf",
  "questions": [
    "What is this document about?",
    "What programming languages are supported?",
    "What APIs are mentioned?",
    "Is this for developers?",
    "What SDKs are available?",
    "Are there code examples?",
    "What platforms are supported?",
    "Is this a technical document?",
    "What services are offered?",
    "What is the main purpose?"
  ]
}
```

## Health Check Endpoints

### Basic Health Check
```
GET /health
```

### Simple Status
```
GET /status
```

### Root Endpoint
```
GET /
```

## Error Scenarios

### Invalid Token
```
Authorization: Bearer invalid-token
```
**Expected:** `401 Unauthorized`

### Invalid PDF URL
```json
{
  "documents": "https://invalid-url.com/nonexistent.pdf",
  "questions": ["What is this about?"]
}
```
**Expected:** `400 Bad Request` with error details

### Too Many Questions
```json
{
  "documents": "https://valid-url.com/document.pdf",
  "questions": ["Q1", "Q2", "Q3", "Q4", "Q5", "Q6", "Q7", "Q8", "Q9", "Q10", "Q11"]
}
```
**Expected:** `400 Bad Request` - Maximum 10 questions allowed

## Performance

- **Response Time:** < 30 seconds
- **PDF Size Limit:** 50MB
- **Questions Limit:** 10 per request
- **Authentication Required:** Yes (Bearer token)

## Success Criteria

✅ Returns structured JSON with "answers" array
✅ Answer order matches question order
✅ Handles authentication properly
✅ Processes PDFs and extracts text
✅ Uses Gemini Flash 1.5 for intelligent answers
✅ Returns "Not found in document" for unanswerable questions
✅ Completes within 30-second timeout
✅ Proper error handling and status codes