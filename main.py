"""Extrator Inteligente de Conteúdo - Cloud Run API

API FastAPI para extrair conteúdo de URLs usando Gemini AI
e criar documentos no Google Drive.
"""

import os
import re
import logging
from typing import Optional
from datetime import datetime

from fastapi import FastAPI, HTTPException, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, HttpUrl
import requests
from bs4 import BeautifulSoup
import google.generativeai as genai
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaInMemoryUpload

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Inicialização FastAPI
app = FastAPI(
    title="Extrator Inteligente de Conteúdo",
    description="API para extrair conteúdo de URLs e criar documentos no Google Drive",
    version="1.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configuração Gemini API
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel('gemini-1.5-pro')
else:
    logger.warning("GEMINI_API_KEY não configurada")
    model = None

# Models
class ExtractRequest(BaseModel):
    url: HttpUrl
    folder_id: Optional[str] = None

class ExtractResponse(BaseModel):
    success: bool
    message: str
    document_id: Optional[str] = None
    document_url: Optional[str] = None
    extracted_content: Optional[str] = None

# Funções auxiliares
def fetch_url_content(url: str) -> str:
    """Faz fetch do conteúdo HTML de um URL."""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        return response.text
    except Exception as e:
        logger.error(f"Erro ao fazer fetch do URL: {e}")
        raise HTTPException(status_code=400, detail=f"Erro ao aceder ao URL: {str(e)}")

def extract_text_from_html(html: str) -> str:
    """Extrai texto limpo de HTML."""
    soup = BeautifulSoup(html, 'html.parser')
    
    # Remove scripts, styles, etc.
    for tag in soup(['script', 'style', 'nav', 'footer', 'header']):
        tag.decompose()
    
    # Extrai texto
    text = soup.get_text(separator='\n')
    
    # Limpa espaços em branco
    lines = (line.strip() for line in text.splitlines())
    text = '\n'.join(line for line in lines if line)
    
    return text

def extract_with_gemini(url: str, html_content: str) -> dict:
    """Usa Gemini para extrair informação estruturada."""
    if not model:
        raise HTTPException(status_code=500, detail="Gemini API não configurada")
    
    try:
        # Extrai texto limpo primeiro
        text_content = extract_text_from_html(html_content)
        
        # Limita o tamanho do conteúdo (Gemini tem limites)
        max_chars = 30000
        if len(text_content) > max_chars:
            text_content = text_content[:max_chars] + "...\n[Conteúdo truncado]"
        
        prompt = f"""Analisa o seguinte conteúdo de uma página web e extrai as informações principais.

URL: {url}

Conteúdo:
{text_content}

Por favor, extrai e estrutura as seguintes informações:
1. Título principal
2. Resumo executivo (2-3 frases)
3. Pontos-chave principais (lista)
4. Conclusões ou takeaways importantes

Formata a resposta de forma clara e estruturada."""
        
        response = model.generate_content(prompt)
        
        return {
            "title": f"Extração: {url}",
            "content": response.text,
            "raw_text": text_content[:5000]  # Primeiros 5000 chars do texto original
        }
    
    except Exception as e:
        logger.error(f"Erro ao processar com Gemini: {e}")
        # Fallback: retorna apenas o texto extraído
        return {
            "title": f"Extração: {url}",
            "content": f"Conteúdo extraído (sem processamento IA):\n\n{extract_text_from_html(html_content)[:10000]}",
            "raw_text": extract_text_from_html(html_content)[:5000]
        }

def create_google_doc(title: str, content: str, folder_id: Optional[str] = None) -> dict:
    """Cria um documento no Google Drive.
    
    Nota: Esta função requer configuração de Service Account.
    Por agora, retorna apenas o conteúdo sem criar o documento.
    """
    # TODO: Implementar criação de documento no Drive
    # Requer: GOOGLE_SERVICE_ACCOUNT_KEY como variável de ambiente
    
    logger.info("Criação de documento no Drive ainda não implementada")
    
    return {
        "success": False,
        "message": "Funcionalidade de Google Drive em desenvolvimento",
        "content": content
    }

# Endpoints
@app.get("/")
def root():
    """Serve the frontend HTML interface."""
    import os
    file_path = os.path.join(os.path.dirname(__file__), "index.html")
    if os.path.exists(file_path):
        return FileResponse(file_path, media_type="text/html")
    else:
        # Fallback: return simple HTML redirect
        from fastapi.responses import HTMLResponse
        html_content = """
        <!DOCTYPE html>
        <html>
        <head><title>Extrator Inteligente</title></head>
        <body>
            <h1>API Funcionando!</h1>
            <p>Endpoint de extração: POST /extract</p>
        </body>
        </html>
        """
        return HTMLResponse(content=html_content)
