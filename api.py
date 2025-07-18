from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from rag_pipeline import EnhancedRAGPipeline
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure Redis connection from environment variables
REDIS_HOST = os.getenv('REDIS_HOST', 'localhost')
REDIS_PORT = int(os.getenv('REDIS_PORT', '6379'))
REDIS_PASSWORD = os.getenv('REDIS_PASSWORD', '')

app = FastAPI(
    title="RAG API",
    description="API for Retrieval Augmented Generation with Gemini",
    version="1.0.0"
)

# Initialize RAG pipeline with Redis configuration
api_key = os.getenv('GOOGLE_API_KEY')
if not api_key:
    raise ValueError("GOOGLE_API_KEY not found in environment variables")

rag = EnhancedRAGPipeline(
    api_key=api_key,
    redis_host=REDIS_HOST,
    redis_port=REDIS_PORT,
    redis_password=REDIS_PASSWORD
)

class Query(BaseModel):
    text: str

class Document(BaseModel):
    file_paths: Optional[List[str]] = None
    directory_path: Optional[str] = None

class Response(BaseModel):
    response: str
    retrieved_docs: Optional[List[Dict[str, Any]]] = None

@app.post("/query", response_model=Response)
async def process_query(query: Query):
    try:
        result = rag.process_query(query.text)
        return Response(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/add-documents")
async def add_documents(documents: Document):
    try:
        rag.add_media_documents(
            file_paths=documents.file_paths,
            directory_path=documents.directory_path
        )
        return {"message": "Documents added successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    return {"status": "healthy"}