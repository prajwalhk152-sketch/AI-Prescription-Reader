from fastapi import APIRouter

router = APIRouter()

@router.post("/ocr")
def ocr_api():

    return {
        "status": "success",
        "module": "OCR API"
    }