# Fortes Eduction - RAG Q&A System Overview

## Introduction

Fortes Eduction is an advanced Retrieval-Augmented Generation (RAG) question-answering system designed to provide accurate, grounded, and safe responses based on your knowledge base.

## Key Features

### Intelligent Document Management
- Support for multiple document formats: PDF, DOCX, Markdown, and plain text
- Automatic document chunking with citation tracking
- Line number and document ID preservation for precise citations
- Incremental updates and async processing

### Advanced Guardrails
- **Prompt Injection Detection**: Identifies and neutralizes attempts to manipulate the system
- **PII Redaction**: Automatically redacts personally identifiable information (emails, phone numbers)
- **Grounding Score Validation**: Ensures responses are sufficiently supported by knowledge base content

### Attribution and Hallucination Detection
- Sentence-level citation mapping
- Automatic detection of unsupported claims
- Visual markers for hallucinated content
- Confidence scoring for each statement

### Observability
- Token usage tracking
- Cost estimation per request
- Prompt caching for repeated queries
- Comprehensive logging

## Architecture

Fortes Eduction uses a modern tech stack:
- **Backend**: Python FastAPI with async support
- **Frontend**: Next.js 14 with TypeScript
- **Vector Store**: ChromaDB (with support for Qdrant and FAISS)
- **Database**: SQLite by default (MySQL and Pinecone supported)
- **LLM Provider**: OpenAI (with automatic fallback to local stub for development)

## Getting Started

1. Configure your environment variables
2. Upload documents to create a knowledge base
3. Ask questions and receive grounded, cited answers
4. Review citations and grounding scores for transparency

For detailed setup instructions, see the main README.

