# Extrator Inteligente de Conteúdo - Cloud Run
# FastAPI Application - Minimal version for stable startup

import os
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Extrator Inteligente de Conteúdo")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ProcessRequest(BaseModel):
    url: str
    folder_name: str = "Arquivos"
    gemini_key: str = None

@app.get("/", response_class=HTMLResponse)
async def root():
    gemini_configured = "Yes" if os.getenv("GEMINI_API_KEY") else "No"
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Extrator Inteligente - Cloud Run</title>
        <style>
            body {{
                font-family: Arial, sans-serif;
                max-width: 800px;
                margin: 50px auto;
                padding: 20px;
            }}
            .status {{ color: green; }}
            .config {{ background: #f0f0f0; padding: 10px; margin: 10px 0; }}
        </style>
    </head>
    <body>
        <h1>🚀 Extrator Inteligente de Conteúdo</h1>
        <p class="status">✅ Serviço Cloud Run Online!</p>
        <div class="config">
            <h3>Configuração:</h3>
            <p>GEMINI_API_KEY: {gemini_configured}</p>
            <p>Port: 8080</p>
        </div>
        <h3>Endpoints disponíveis:</h3>
        <ul>
            <li><a href="/health">GET /health</a> - Health check</li>
            <li><a href="/docs">GET /docs</a> - API Documentation (Swagger)</li>
            <li>POST /process - Processar URL (em desenvolvimento)</li>
        </ul>
    </body>
    </html>
    """

@app.get("/health")
async def health():
    return {{
        "status": "healthy",
        "service": "extrator-inteligente",
        "gemini_api_configured": bool(os.getenv("GEMINI_API_KEY"))
    }}

@app.post("/process")
async def process_url(request: ProcessRequest):
    """Process URL endpoint - placeholder for full implementation"""
    logger.info(f"Processing URL: {{request.url}}")
    
    # Validate GEMINI_API_KEY
    api_key = request.gemini_key or os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise HTTPException(
            status_code=400,
            detail="GEMINI_API_KEY not configured. Set environment variable or provide in request."
        )
    
    return {{
        "status": "success",
        "message": "URL processing functionality will be implemented here",
        "url": request.url,
        "folder": request.folder_name
    }}

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8080))
    uvicorn.run(app, host="0.0.0.0", port=port)
