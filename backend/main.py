"""
Akij Sales Intelligence System - FastAPI Backend
Multi-Agent Sales Analytics with RAG
"""
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
import sys
import requests

from backend.config import settings
from backend.api.routes_dynamic import router


# Download CSV files from GitHub if not present (for Render deployment)
data_dir = Path(__file__).parent.parent / "data"
csv_files = [
    "product_master.csv",
    "branch_master.csv",
    "division_master.csv",
    "customer_master.csv"
]

# Check if data directory exists and has files
if not data_dir.exists() or not any(data_dir.glob("*.csv")):
    print("\n📥 Data files not found locally. Downloading from GitHub...")
    data_dir.mkdir(exist_ok=True)

    # GitHub raw file URL - UPDATE THIS WITH YOUR ACTUAL REPO
    github_raw = "https://github.com/FahimShahryer/sales_ai/tree/main/data"

    for csv_file in csv_files:
        try:
            file_path = data_dir / csv_file
            if not file_path.exists():
                print(f"   Downloading {csv_file}...")
                response = requests.get(github_raw + csv_file, timeout=10)
                response.raise_for_status()
                with open(file_path, "wb") as f:
                    f.write(response.content)
                print(f"   ✅ {csv_file} downloaded")
        except Exception as e:
            print(f"   ⚠️  Failed to download {csv_file}: {str(e)}")

    print("✅ Data download complete\n")
else:
    print("✅ Data files found locally\n")


# Fix Windows encoding
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

# Create FastAPI app
app = FastAPI(
    title=settings.API_TITLE,
    version=settings.API_VERSION,
    description=settings.API_DESCRIPTION
)

# CORS middleware (allow frontend to connect)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(router)

# Mount static files for frontend
static_path = Path(__file__).parent / "static"
if static_path.exists():
    app.mount("/static", StaticFiles(directory=str(static_path)), name="static")

# Root endpoint - serve index.html
@app.get("/", response_class=HTMLResponse)
async def read_root():
    """Serve the frontend HTML page"""
    html_path = static_path / "index.html"

    if html_path.exists():
        return FileResponse(html_path)
    else:
        return HTMLResponse(content="""
        <html>
            <head>
                <title>Akij Sales Intelligence</title>
            </head>
            <body style="font-family: Arial; padding: 50px; text-align: center;">
                <h1>🚀 Akij Sales Intelligence API</h1>
                <p>Backend server is running successfully!</p>
                <p><a href="/docs">📚 View API Documentation</a></p>
                <p><strong>Note:</strong> Frontend UI not yet deployed. Use API endpoints via /docs</p>
                <hr>
                <h3>Quick Test:</h3>
                <p><a href="/api/test">Test Endpoint</a></p>
                <p><a href="/api/health">Health Check</a></p>
            </body>
        </html>
        """)

@app.get("/favicon.ico")
async def favicon():
    """Return a simple response for favicon requests"""
    return {"message": "No favicon"}

# Startup message
@app.on_event("startup")
async def startup_event():
    print("\n" + "=" * 80)
    print("🚀 AKIJ SALES INTELLIGENCE - FULLY DYNAMIC SYSTEM")
    print("=" * 80)
    print(f"📍 API Server: http://localhost:8000")
    print(f"📚 API Docs: http://localhost:8000/docs")
    print(f"🔧 Health Check: http://localhost:8000/api/health")
    print("=" * 80)
    print("\n✨ Fully Dynamic Multi-Agent Architecture")
    print("   🔹 Query Understanding Agent (LLM analyzes query)")
    print("   🔹 Data Retrieval Agent (LLM generates pandas code)")
    print("   🔹 RAG Agent (LLM retrieves context)")
    print("   🔹 Master Synthesis Agent (LLM combines & answers)")
    print("\n💎 Features:")
    print("   - Zero hardcoded queries")
    print("   - LLM-driven code generation")
    print("   - Fully adaptive to any question")
    print("   - 100% dynamic system")
    print("\n⏳ Agents will initialize on first API request...")
    print("=" * 80 + "\n")


# Run with: uvicorn backend.main:app --reload --port 8000
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "backend.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
