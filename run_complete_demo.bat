@echo off
echo ================================================
echo Fortes Education - Complete End-to-End Demo
echo ================================================
echo.

REM Set OpenAI API Key
set OPENAI_API_KEY=your-openai-api-key-here
set OPENAI_API_BASE=https://api.openai.com/v1
set EMBEDDING_MODEL=text-embedding-3-small
set GENERATION_MODEL=gpt-4o-mini
set RAG_STORE=sqlite
set SQLITE_FILE=./fortes.db
set PROJECT_NAME=Fortes Education
set VERSION=1.0.0
set VECTOR_STORE_TYPE=chroma
set ENABLE_TOKEN_LOGGING=true
set ENABLE_COST_TRACKING=true
set ENABLE_PROMPT_CACHE=true

echo ✓ OpenAI API Key configured
echo ✓ Environment variables set
echo.

cd backend

echo ================================================
echo 1. Running Chunker Tests
echo ================================================
pytest tests/test_chunker.py -v
if %errorlevel% neq 0 (
    echo ✗ Chunker tests failed
) else (
    echo ✓ Chunker tests passed
)
echo.

echo ================================================
echo 2. Running Guardrails Tests
echo ================================================
pytest tests/test_guardrails.py -v
if %errorlevel% neq 0 (
    echo ✗ Guardrails tests failed
) else (
    echo ✓ Guardrails tests passed
)
echo.

echo ================================================
echo 3. Running Retriever Tests
echo ================================================
pytest tests/test_retriever.py -v
if %errorlevel% neq 0 (
    echo ✗ Retriever tests failed
) else (
    echo ✓ Retriever tests passed
)
echo.

echo ================================================
echo 4. Running Evaluation Math Tests
echo ================================================
pytest tests/test_eval_math.py -v
if %errorlevel% neq 0 (
    echo ✗ Eval math tests failed
) else (
    echo ✓ Eval math tests passed
)
echo.

echo ================================================
echo 5. Running Full Evaluation Harness
echo ================================================
python run_eval.py
if %errorlevel% neq 0 (
    echo ✗ Evaluation harness failed
) else (
    echo ✓ Evaluation harness completed
)
echo.

echo ================================================
echo DEMO COMPLETE
echo ================================================
echo.
echo Results:
echo - All tests executed
echo - Evaluation report: eval_report.json
echo.
echo To start the application:
echo   Backend:  cd backend ^& uvicorn app.main:app --reload
echo   Frontend: cd frontend ^& npm run dev
echo.

pause

