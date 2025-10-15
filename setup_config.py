#!/usr/bin/env python3
"""
Setup configuration for Fortes Education with OpenAI API key
"""

import os

# Set environment variables
os.environ['OPENAI_API_KEY'] = 'your-openai-api-key-here'
os.environ['OPENAI_API_BASE'] = 'https://api.openai.com/v1'
os.environ['EMBEDDING_MODEL'] = 'text-embedding-3-small'
os.environ['GENERATION_MODEL'] = 'gpt-4o-mini'
os.environ['RAG_STORE'] = 'sqlite'
os.environ['SQLITE_FILE'] = './fortes.db'
os.environ['PROJECT_NAME'] = 'Fortes Education'
os.environ['VERSION'] = '1.0.0'

print("✓ OpenAI API key configured")
print("✓ Using SQLite database")
print("✓ Fortes Education ready to run")

