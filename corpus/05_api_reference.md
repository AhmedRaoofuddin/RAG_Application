# Fortes Eduction API Reference

## Authentication

Currently, Fortes Eduction operates in guest mode with no authentication required. All API endpoints are publicly accessible.

## Base URL

```
http://localhost:8000/api
```

## Endpoints

### Knowledge Base Management

#### Create Knowledge Base

```http
POST /knowledge-bases
Content-Type: application/json

{
  "name": "My Knowledge Base",
  "description": "Description of the knowledge base"
}
```

**Response**: 201 Created
```json
{
  "id": 1,
  "name": "My Knowledge Base",
  "description": "Description of the knowledge base",
  "created_at": "2024-01-01T00:00:00Z"
}
```

#### List Knowledge Bases

```http
GET /knowledge-bases
```

**Response**: 200 OK
```json
[
  {
    "id": 1,
    "name": "My Knowledge Base",
    "description": "Description",
    "document_count": 5,
    "created_at": "2024-01-01T00:00:00Z"
  }
]
```

### Document Upload

#### Upload Document

```http
POST /knowledge-bases/{kb_id}/documents
Content-Type: multipart/form-data

file: <binary>
```

**Response**: 202 Accepted
```json
{
  "upload_id": "abc123",
  "status": "processing",
  "filename": "document.pdf"
}
```

#### Check Upload Status

```http
GET /knowledge-bases/{kb_id}/documents/{upload_id}/status
```

**Response**: 200 OK
```json
{
  "upload_id": "abc123",
  "status": "completed",
  "chunks_created": 42,
  "processing_time_ms": 1234
}
```

### Chat and Q&A

#### Create Chat Session

```http
POST /chats
Content-Type: application/json

{
  "title": "My Chat",
  "knowledge_base_ids": [1, 2]
}
```

**Response**: 201 Created
```json
{
  "id": 1,
  "title": "My Chat",
  "knowledge_base_ids": [1, 2],
  "created_at": "2024-01-01T00:00:00Z"
}
```

#### Send Message (Streaming)

```http
POST /chats/{chat_id}/messages
Content-Type: application/json

{
  "messages": [
    {
      "role": "user",
      "content": "What is Fortes Eduction?"
    }
  ]
}
```

**Response**: 200 OK (Server-Sent Events)
```
0:"Fortes Eduction is an advanced RAG system... [citation:1]"
d:{"finishReason":"stop","grounding_score":0.85,"has_hallucination":false}
```

### Retrieval Testing

#### Test Retrieval

```http
POST /knowledge-bases/{kb_id}/test-retrieval
Content-Type: application/json

{
  "query": "How do I install?",
  "top_k": 5
}
```

**Response**: 200 OK
```json
{
  "query": "How do I install?",
  "results": [
    {
      "doc_id": "installation_guide.md",
      "chunk_id": "chunk_0",
      "content": "Installation steps...",
      "line_start": 10,
      "line_end": 20,
      "similarity_score": 0.92
    }
  ],
  "grounding_score": 0.92
}
```

## Response Metadata

All chat responses include metadata:

```json
{
  "finishReason": "stop",
  "grounding_score": 0.85,
  "has_hallucination": false,
  "attribution": {
    "sentences": [...],
    "total_sentences": 5,
    "supported_sentences": 5
  },
  "guardrails": {
    "pii_redacted": false,
    "input_warnings": []
  }
}
```

## Error Responses

### 400 Bad Request
```json
{
  "detail": "Invalid request parameters"
}
```

### 404 Not Found
```json
{
  "detail": "Resource not found"
}
```

### 500 Internal Server Error
```json
{
  "detail": "Internal server error occurred"
}
```

## Rate Limiting

Currently no rate limiting is enforced. For production deployments, implement appropriate rate limiting based on your requirements.

