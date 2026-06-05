from fastapi import FastAPI

from ocr_api import router as ocr_router
from medicine_api import router as medicine_router
from dosage_api import router as dosage_router
from interaction_api import router as interaction_router
from recommendation_api import router as recommendation_router

app = FastAPI(
    title="AI Prescription Reader API",
    version="1.0"
)

app.include_router(ocr_router)
app.include_router(medicine_router)
app.include_router(dosage_router)
app.include_router(interaction_router)
app.include_router(recommendation_router)

@app.get("/")
def home():
    return {
        "message": "AI Prescription Reader API Running"
    }