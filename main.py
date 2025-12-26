# Minimal FastAPI test for Cloud Run
import os
from fastapi import FastAPI

app = FastAPI(title="Test")

@app.get("/")
def root():
    return {"status": "ok", "message": "FastAPI is running on Cloud Run!"}

@app.get("/health")
def health():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8080))
    uvicorn.run(app, host="0.0.0.0", port=port)
