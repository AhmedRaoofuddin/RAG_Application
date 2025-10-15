# Fortes Education Installation Guide

## Prerequisites

Before installing Fortes Education, ensure you have:
- Python 3.9 or higher
- Node.js 18 or higher
- 8GB+ RAM recommended
- Optional: Docker & Docker Compose for containerized deployment

## Installation Steps

### 1. Clone the Repository

```bash
git clone https://github.com/your-org/fortes-eduction.git
cd fortes-eduction
```

### 2. Backend Setup

Navigate to the backend directory and install dependencies:

```bash
cd backend
pip install -r requirements.txt
```

### 3. Frontend Setup

Navigate to the frontend directory and install dependencies:

```bash
cd frontend
npm install
# or
pnpm install
```

### 4. Environment Configuration

Copy the example environment file and configure:

```bash
cp env.example .env
```

Edit `.env` and set your configuration:
- `OPENAI_API_KEY`: Your OpenAI API key (optional, will use stub if not provided)
- `RAG_STORE`: Choose `sqlite` (default), `pinecone`, or `mysql`
- `GROUNDING_THRESHOLD`: Set the minimum grounding score (default: 0.62)

### 5. Database Initialization

The database will auto-initialize on first run. For SQLite (default), no manual setup is required.

For MySQL (XAMPP):
1. Start XAMPP MySQL server
2. Set `RAG_STORE=mysql` in `.env`
3. Configure MySQL credentials in `.env`

### 6. Start the Application

#### Development Mode

Start the backend:
```bash
cd backend
uvicorn app.main:app --reload --port 8000
```

Start the frontend:
```bash
cd frontend
npm run dev
```

Access the application at http://localhost:3000

## Verification

After installation, verify the system is working:
1. Upload a sample document
2. Wait for processing to complete
3. Ask a question related to your document
4. Verify citations and grounding score appear correctly

## Troubleshooting

If you encounter issues:
- Check logs for error messages
- Ensure all dependencies are installed
- Verify environment variables are set correctly
- See the troubleshooting guide for common issues

