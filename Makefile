# Fortes Education - Makefile for easy command execution

.PHONY: help dev backend frontend test eval ingest clean

help:
	@echo "Fortes Education - Available Commands"
	@echo "===================================="
	@echo ""
	@echo "  make dev        - Start both backend and frontend in development mode"
	@echo "  make backend    - Start backend only"
	@echo "  make frontend   - Start frontend only"
	@echo "  make test       - Run all tests"
	@echo "  make eval       - Run evaluation harness"
	@echo "  make ingest     - Ingest sample corpus"
	@echo "  make clean      - Clean generated files"
	@echo ""

dev:
	@echo "Starting Fortes Education in development mode..."
	@echo "Backend will run on http://localhost:8000"
	@echo "Frontend will run on http://localhost:3000"
	@echo ""
	@echo "NOTE: Run 'make backend' and 'make frontend' in separate terminals"

backend:
	@echo "Starting Fortes Education Backend..."
	cd backend && uvicorn app.main:app --reload --port 8000

frontend:
	@echo "Starting Fortes Education Frontend..."
	cd frontend && npm run dev

test:
	@echo "Running Fortes Education Tests..."
	cd backend && pytest tests/ -v

eval:
	@echo "Running Evaluation Harness..."
	cd backend && python run_eval.py

ingest:
	@echo "Ingesting sample corpus..."
	@echo "NOTE: Use the web interface to upload documents from the corpus/ directory"
	@echo "Or use the API: POST /api/knowledge-bases/{id}/documents"

clean:
	@echo "Cleaning generated files..."
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	rm -f backend/fortes.db
	rm -f eval_report.json
	@echo "Clean complete!"

