# Start Fortes Education Backend
$env:OPENAI_API_KEY='your-openai-api-key-here'
$env:OPENAI_API_BASE='https://api.openai.com/v1'
$env:EMBEDDING_MODEL='text-embedding-3-small'
$env:GENERATION_MODEL='gpt-4o-mini'
$env:PROJECT_NAME='Fortes Education'
$env:VERSION='1.0.0'
$env:RAG_STORE='sqlite'
$env:SQLITE_FILE='./fortes.db'
$env:VECTOR_STORE_TYPE='chroma'
$env:CHROMA_DB_HOST='localhost'
$env:CHROMA_DB_PORT='8000'

Write-Host "================================"
Write-Host "Fortes Education Backend Starting"
Write-Host "================================"
Write-Host ""
Write-Host "OpenAI Key: Configured ✓"
Write-Host "Database: SQLite (fortes.db)"
Write-Host "Port: 8000"
Write-Host ""

Set-Location backend
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

