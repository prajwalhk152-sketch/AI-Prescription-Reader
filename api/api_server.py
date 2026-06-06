from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

try:
    from .ocr_api import router as ocr_router
    from .workflow_api import router as workflow_router
    from .medicine_api import router as medicine_router
    from .dosage_api import router as dosage_router
    from .interaction_api import router as interaction_router
    from .recommendation_api import router as recommendation_router
except ImportError:
    from ocr_api import router as ocr_router
    from workflow_api import router as workflow_router
    from medicine_api import router as medicine_router
    from dosage_api import router as dosage_router
    from interaction_api import router as interaction_router
    from recommendation_api import router as recommendation_router

PROJECT_ROOT = Path(__file__).resolve().parents[1]
PUBLIC_DIR = PROJECT_ROOT / "public"
OUTPUTS_DIR = PROJECT_ROOT / "outputs"
ASSETS_DIR = PROJECT_ROOT / "assets"

app = FastAPI(
    title="AI Prescription Reader API",
    version="1.0"
)

app.include_router(ocr_router)
app.include_router(workflow_router)
app.include_router(medicine_router)
app.include_router(dosage_router)
app.include_router(interaction_router)
app.include_router(recommendation_router)

app.mount("/static", StaticFiles(directory=PUBLIC_DIR), name="static")
app.mount("/outputs", StaticFiles(directory=OUTPUTS_DIR), name="outputs")
app.mount("/assets", StaticFiles(directory=ASSETS_DIR), name="assets")


@app.get("/api/health")
def home():
    return {
        "message": "AI Prescription Reader API Running"
    }


@app.get("/")
def frontend():
    return FileResponse(PUBLIC_DIR / "index.html")
