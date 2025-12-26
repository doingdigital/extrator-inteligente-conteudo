# Extrator Inteligente de Conteúdo - Cloud Run
# FastAPI Application for Web Scraping + Gemini AI + Google Drive

import os
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import requests
from bs4 import BeautifulSoup
import google.generativeai as genai

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
    folder_name: str
    gemini_key: str

@app.get("/", response_class=HTMLResponse)
async def root():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Arquivador Inteligente - Cloud Run</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                max-width: 800px;
                margin: 50px auto;
                padding: 20px;
            }
            h1 { color: #4285f4; }
            input, button {
                width: 100%;
                padding: 10px;
                margin: 10px 0;
                font-size: 16px;
            }
            button {
                background: #4285f4;
                color: white;
                border: none;
                cursor: pointer;
            }
            #result { margin-top: 20px; padding: 10px; background: #f0f0f0; }
        </style>
    </head>
    <body>
        <h1>🚀 Arquivador Inteligente - Cloud Run Edition</h1>
        <input type="text" id="gemini_key" placeholder="Chave API Gemini">
        <input type="text" id="url" placeholder="URL do Artigo">
        <input type="text" id="folder" placeholder="Nome da Pasta">
        <button onclick="process()">Processar e Arquivar</button>
        <div id="result"></div>
        
        <script>
            async function process() {
                const result = document.getElementById('result');
                result.innerHTML = '⏳ Processando...';
                
                try {
                    const response = await fetch('/process', {
                        method: 'POST',
                        headers: {'Content-Type': 'application/json'},
                        body: JSON.stringify({
                            gemini_key: document.getElementById('gemini_key').value,
                            url: document.getElementById('url').value,
                            folder_name: document.getElementById('folder').value
                        })
                    });
                    
                    const data = await response.json();
                    if (response.ok) {
                        result.innerHTML = `✅ ${data.message}`;
                    } else {
                        result.innerHTML = `❌ Erro: ${data.detail}`;
                    }
                } catch (error) {
                    result.innerHTML = `❌ Erro: ${error.message}`;
                }
            }
        </script>
    </body>
    </html>
    """

@app.post("/process")
async def process_url(request: ProcessRequest):
    try:
        # 1. Scrape content
        response = requests.get(request.url, timeout=30)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Extract text
        title = soup.find('title').get_text() if soup.find('title') else "Untitled"
        paragraphs = soup.find_all(['p', 'h1', 'h2', 'h3'])
        content = "\n\n".join([p.get_text().strip() for p in paragraphs if p.get_text().strip()])
        
        # 2. Process with Gemini
        genai.configure(api_key=request.gemini_key)
        model = genai.GenerativeModel('gemini-pro')
        
        prompt = f"""Organize and format this article content:
        
Title: {title}
        
Content:
        {content[:5000]}
        
Create a well-structured summary in Portuguese."""
        
        response = model.generate_content(prompt)
        processed_content = response.text
        
        # 3. Return result (Drive upload would go here)
        return {
            "success": True,
            "message": f"Conteúdo processado com sucesso! Título: {title}",
            "content_length": len(content),
            "summary": processed_content[:200] + "..."
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8080))
    uvicorn.run(app, host="0.0.0.0", port=port)
