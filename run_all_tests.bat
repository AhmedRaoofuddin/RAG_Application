@echo off
REM Fortes Education - Run All Tests and Evaluation (Windows)

echo ================================================
echo Fortes Education - Comprehensive Test Suite
echo ================================================
echo.

cd backend

echo 1. Running Chunker Tests...
pytest tests/test_chunker.py -v
if %errorlevel% neq 0 set /a FAILED+=1

echo.
echo 2. Running Guardrails Tests...
pytest tests/test_guardrails.py -v
if %errorlevel% neq 0 set /a FAILED+=1

echo.
echo 3. Running Retriever Tests...
pytest tests/test_retriever.py -v
if %errorlevel% neq 0 set /a FAILED+=1

echo.
echo 4. Running Evaluation Math Tests...
pytest tests/test_eval_math.py -v
if %errorlevel% neq 0 set /a FAILED+=1

echo.
echo 5. Running Full Evaluation Harness...
python run_eval.py
if %errorlevel% neq 0 set /a FAILED+=1

echo.
echo ================================================
echo TEST SUMMARY
echo ================================================

if %FAILED%==0 (
    echo All tests PASSED!
    exit /b 0
) else (
    echo Some tests FAILED
    exit /b 1
)

