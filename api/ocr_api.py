from datetime import datetime
import json
from pathlib import Path
import sys

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

PROJECT_ROOT = Path(__file__).resolve().parents[1]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from modules.module_05_ocr import (
    OUTPUT_DIR,
    calculate_basic_confidence,
    extract_text_easyocr,
    extract_text_tesseract,
    get_medicine_rescue_matches,
    merge_ocr_texts,
)

router = APIRouter()

ALLOWED_ENGINES = {"Tesseract OCR", "EasyOCR", "Both"}


class OCRRequest(BaseModel):
    image_path: str = Field(
        ...,
        description="Path to a prescription image, relative to the project root or absolute.",
    )
    ocr_engine: str = Field(default="Tesseract OCR")
    handwriting_mode: bool = Field(default=False)
    include_medicine_rescue: bool = Field(default=False)


def resolve_image_path(image_path: str) -> Path:
    path = Path(image_path).expanduser()

    if not path.is_absolute():
        path = PROJECT_ROOT / path

    path = path.resolve()

    if not path.exists() or not path.is_file():
        raise HTTPException(status_code=404, detail=f"Image not found: {image_path}")

    if path.suffix.lower() not in {".jpg", ".jpeg", ".png"}:
        raise HTTPException(
            status_code=400,
            detail="OCR supports only .jpg, .jpeg, and .png images.",
        )

    return path


@router.post("/api/ocr")
@router.post("/ocr")
def ocr_api(request: OCRRequest):
    if request.ocr_engine not in ALLOWED_ENGINES:
        raise HTTPException(
            status_code=400,
            detail=f"ocr_engine must be one of: {', '.join(sorted(ALLOWED_ENGINES))}",
        )

    image_path = resolve_image_path(request.image_path)
    tesseract_text = ""
    easyocr_text = ""

    if request.ocr_engine in {"Tesseract OCR", "Both"}:
        tesseract_text = extract_text_tesseract(
            str(image_path),
            request.handwriting_mode,
        )

    if request.ocr_engine in {"EasyOCR", "Both"}:
        easyocr_text = extract_text_easyocr(
            str(image_path),
            request.handwriting_mode,
        )

    combined_text = merge_ocr_texts(easyocr_text, tesseract_text)
    confidence = calculate_basic_confidence(combined_text)
    rescue_matches = []

    if request.include_medicine_rescue:
        rescue_matches = get_medicine_rescue_matches(combined_text)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_dir = PROJECT_ROOT / OUTPUT_DIR
    output_dir.mkdir(parents=True, exist_ok=True)

    text_path = output_dir / f"ocr_text_{timestamp}.txt"
    json_path = output_dir / f"ocr_result_{timestamp}.json"

    result_data = {
        "status": "success",
        "input_path": str(image_path),
        "ocr_engine": request.ocr_engine,
        "handwriting_mode": request.handwriting_mode,
        "include_medicine_rescue": request.include_medicine_rescue,
        "tesseract_text": tesseract_text,
        "easyocr_text": easyocr_text,
        "combined_text": combined_text,
        "medicine_rescue_matches": rescue_matches,
        "basic_confidence_percent": confidence,
        "text_file_path": str(text_path),
        "json_file_path": str(json_path),
        "created_at": str(datetime.now()),
    }

    text_path.write_text(combined_text, encoding="utf-8")
    json_path.write_text(json.dumps(result_data, indent=4), encoding="utf-8")

    return result_data
