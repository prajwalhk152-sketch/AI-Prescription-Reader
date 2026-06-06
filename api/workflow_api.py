from datetime import datetime
import csv
import json
import re
import shutil
from pathlib import Path
import sys
from itertools import combinations
import os

import cv2
import numpy as np
from fastapi import APIRouter, File, HTTPException, UploadFile
from pydantic import BaseModel

try:
    from pymongo import MongoClient
    from pymongo.errors import PyMongoError, ServerSelectionTimeoutError
except ImportError:
    MongoClient = None
    PyMongoError = ServerSelectionTimeoutError = Exception

PROJECT_ROOT = Path(__file__).resolve().parents[1]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

UPLOAD_DIR = PROJECT_ROOT / "outputs" / "module_03_upload"
PREPROCESS_DIR = PROJECT_ROOT / "outputs" / "module_04_preprocessed"
OCR_DIR = PROJECT_ROOT / "outputs" / "module_05_ocr"
MEDICINE_DIR = PROJECT_ROOT / "outputs" / "module_06_medicines"
DOSAGE_DIR = PROJECT_ROOT / "outputs" / "module_07_dosage"
BENEFITS_DIR = PROJECT_ROOT / "outputs" / "module_08_benefits"
INTERACTIONS_DIR = PROJECT_ROOT / "outputs" / "module_09_interactions"
RECOMMENDATIONS_DIR = PROJECT_ROOT / "outputs" / "module_10_recommendations"

OUTPUT_DIRECTORIES = [
    UPLOAD_DIR,
    PREPROCESS_DIR,
    OCR_DIR,
    MEDICINE_DIR,
    DOSAGE_DIR,
    BENEFITS_DIR,
    INTERACTIONS_DIR,
    RECOMMENDATIONS_DIR,
    PROJECT_ROOT / "outputs" / "module_12_database_storage",
]

for directory in OUTPUT_DIRECTORIES:
    directory.mkdir(parents=True, exist_ok=True)

router = APIRouter(prefix="/api")


class PreprocessRequest(BaseModel):
    image_path: str
    apply_gray: bool = True
    apply_noise: bool = True
    apply_contrast: bool = True
    apply_threshold: bool = True
    handwriting_enhancement: bool = True


class TextAnalysisRequest(BaseModel):
    text: str = ""
    ocr_text_path: str = ""


class BenefitsRequest(BaseModel):
    medicines: list[dict] = []
    medicine_file_path: str = ""
    use_api_genai: bool = False


class InteractionsRequest(BaseModel):
    medicines: list[dict] = []
    medicine_file_path: str = ""


class RecommendationsRequest(BaseModel):
    medicines: list[dict] = []
    medicine_file_path: str = ""


class StoreAnalysisRequest(BaseModel):
    user_id: str = "Guest"
    file_name: str = "latest_prescription"


def safe_filename(file_name: str) -> str:
    cleaned = re.sub(r"[^A-Za-z0-9_.-]+", "_", file_name.strip())
    return cleaned.strip("_") or "prescription_upload"


def relative_path(path: Path) -> str:
    return path.resolve().relative_to(PROJECT_ROOT).as_posix()


def output_url(path: Path) -> str:
    return f"/{relative_path(path)}"


def resolve_project_file(path_value: str, allowed_dirs: list[Path]) -> Path:
    path = Path(path_value)
    if not path.is_absolute():
        path = PROJECT_ROOT / path

    resolved = path.resolve()
    allowed = [directory.resolve() for directory in allowed_dirs]

    if not any(resolved == directory or directory in resolved.parents for directory in allowed):
        raise HTTPException(status_code=400, detail="Path is outside allowed output folders.")

    if not resolved.exists() or not resolved.is_file():
        raise HTTPException(status_code=404, detail=f"File not found: {path_value}")

    return resolved


def preprocess_image(
    image_path: Path,
    apply_gray: bool,
    apply_noise: bool,
    apply_contrast: bool,
    apply_threshold: bool,
    handwriting_enhancement: bool,
):
    image = cv2.imread(str(image_path))
    if image is None:
        raise HTTPException(status_code=400, detail="Unable to read image.")

    if handwriting_enhancement:
        height, width = image.shape[:2]
        if width < 1800:
            scale = 1800 / width
            image = cv2.resize(image, None, fx=scale, fy=scale, interpolation=cv2.INTER_CUBIC)

    processed = image.copy()

    if apply_gray:
        processed = cv2.cvtColor(processed, cv2.COLOR_BGR2GRAY)

    if apply_noise:
        processed = cv2.medianBlur(processed, 3)

    if apply_contrast:
        if len(processed.shape) == 3:
            lab = cv2.cvtColor(processed, cv2.COLOR_BGR2LAB)
            l_channel, a_channel, b_channel = cv2.split(lab)
            clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
            merged = cv2.merge((clahe.apply(l_channel), a_channel, b_channel))
            processed = cv2.cvtColor(merged, cv2.COLOR_LAB2BGR)
        else:
            clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
            processed = clahe.apply(processed)

    if apply_threshold:
        processed_gray = cv2.cvtColor(processed, cv2.COLOR_BGR2GRAY) if len(processed.shape) == 3 else processed

        if handwriting_enhancement:
            processed_gray = cv2.fastNlMeansDenoising(processed_gray, None, 18, 7, 21)
            processed_gray = cv2.addWeighted(
                processed_gray,
                1.55,
                cv2.GaussianBlur(processed_gray, (0, 0), 1.2),
                -0.55,
                0,
            )
            processed = cv2.adaptiveThreshold(
                processed_gray,
                255,
                cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                cv2.THRESH_BINARY,
                31,
                9,
            )
            inverted = cv2.bitwise_not(processed)
            repaired = cv2.morphologyEx(
                inverted,
                cv2.MORPH_CLOSE,
                cv2.getStructuringElement(cv2.MORPH_RECT, (2, 2)),
                iterations=1,
            )
            return cv2.bitwise_not(repaired)

        processed = cv2.adaptiveThreshold(
            processed_gray,
            255,
            cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY,
            11,
            2,
        )

    return processed


def get_request_text(request: TextAnalysisRequest) -> str:
    if request.text.strip():
        return request.text.strip()

    if request.ocr_text_path.strip():
        text_path = resolve_project_file(request.ocr_text_path, [OCR_DIR])
        return text_path.read_text(encoding="utf-8").strip()

    latest = sorted(OCR_DIR.glob("*.txt"), key=lambda path: path.stat().st_mtime, reverse=True)
    if latest:
        return latest[0].read_text(encoding="utf-8").strip()

    raise HTTPException(status_code=400, detail="Provide text, ocr_text_path, or run OCR first.")


@router.get("/files")
def list_files(kind: str = "all"):
    groups = {
        "uploads": (UPLOAD_DIR, {".jpg", ".jpeg", ".png"}),
        "preprocessed": (PREPROCESS_DIR, {".jpg", ".jpeg", ".png"}),
        "ocr": (OCR_DIR, {".txt", ".json"}),
        "medicines": (MEDICINE_DIR, {".csv", ".json"}),
        "dosage": (DOSAGE_DIR, {".csv", ".json"}),
        "benefits": (BENEFITS_DIR, {".csv", ".json"}),
        "interactions": (INTERACTIONS_DIR, {".csv", ".json"}),
        "recommendations": (RECOMMENDATIONS_DIR, {".csv", ".json"}),
    }

    selected = groups if kind == "all" else {kind: groups.get(kind)}
    if any(value is None for value in selected.values()):
        raise HTTPException(status_code=400, detail="Unknown file kind.")

    response = {}
    for name, (directory, extensions) in selected.items():
        files = []
        for path in sorted(directory.iterdir(), key=lambda item: item.stat().st_mtime, reverse=True):
            if path.is_file() and path.suffix.lower() in extensions:
                files.append(
                    {
                        "name": path.name,
                        "path": relative_path(path),
                        "url": output_url(path),
                        "updated_at": datetime.fromtimestamp(path.stat().st_mtime).isoformat(),
                    }
                )
        response[name] = files

    return response


@router.post("/upload")
async def upload_prescription(file: UploadFile = File(...)):
    extension = Path(file.filename or "").suffix.lower()
    if extension not in {".jpg", ".jpeg", ".png"}:
        raise HTTPException(status_code=400, detail="Upload a JPG, JPEG, or PNG image.")

    content = await file.read()
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    saved_name = f"{timestamp}_{safe_filename(file.filename or 'prescription.png')}"
    saved_path = UPLOAD_DIR / saved_name
    saved_path.write_bytes(content)

    metadata = {
        "original_file_name": file.filename,
        "saved_file_name": saved_name,
        "file_type": file.content_type,
        "file_size_kb": round(len(content) / 1024, 2),
        "saved_path": relative_path(saved_path),
        "url": output_url(saved_path),
        "upload_time": str(datetime.now()),
    }

    metadata_path = UPLOAD_DIR / f"{timestamp}_metadata.json"
    metadata_path.write_text(json.dumps(metadata, indent=4), encoding="utf-8")

    return {"status": "success", "file": metadata}


@router.post("/preprocess")
def preprocess_prescription(request: PreprocessRequest):
    image_path = resolve_project_file(request.image_path, [UPLOAD_DIR, PREPROCESS_DIR])
    final_output = preprocess_image(
        image_path,
        request.apply_gray,
        request.apply_noise,
        request.apply_contrast,
        request.apply_threshold,
        request.handwriting_enhancement,
    )

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_path = PREPROCESS_DIR / f"preprocessed_{timestamp}.png"
    cv2.imwrite(str(output_path), final_output)

    return {
        "status": "success",
        "input_path": relative_path(image_path),
        "output_path": relative_path(output_path),
        "url": output_url(output_path),
    }


@router.post("/medicines")
def detect_medicines_api(request: TextAnalysisRequest):
    from modules.module_06_medicine_detection import detect_medicines

    text = get_request_text(request)
    medicines = detect_medicines(text)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    json_path = MEDICINE_DIR / f"detected_medicines_{timestamp}.json"
    csv_path = MEDICINE_DIR / f"detected_medicines_{timestamp}.csv"

    result = {
        "status": "success",
        "medicine_count": len(medicines),
        "medicines": medicines,
        "json_file_path": relative_path(json_path),
        "csv_file_path": relative_path(csv_path),
    }

    json_path.write_text(json.dumps(result, indent=4), encoding="utf-8")
    if medicines:
        with csv_path.open("w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(handle, fieldnames=medicines[0].keys())
            writer.writeheader()
            writer.writerows(medicines)
    else:
        csv_path.write_text("medicine_name,category,confidence,detection_method,score\n", encoding="utf-8")

    return result


@router.post("/dosage")
def extract_dosage_api(request: TextAnalysisRequest):
    from modules.module_07_dosage_extraction import (
        extract_dosage,
        extract_frequency,
        extract_medicine_entities,
        extract_timing,
    )

    text = get_request_text(request)
    result = {
        "status": "success",
        "medicines": extract_medicine_entities(text),
        "dosages": extract_dosage(text),
        "timings": extract_timing(text),
        "frequencies": extract_frequency(text),
    }

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    json_path = DOSAGE_DIR / f"dosage_timing_{timestamp}.json"
    json_path.write_text(json.dumps(result, indent=4), encoding="utf-8")
    result["json_file_path"] = relative_path(json_path)

    return result


def latest_csv_rows(directory: Path) -> tuple[list[dict], str]:
    latest = sorted(directory.glob("*.csv"), key=lambda path: path.stat().st_mtime, reverse=True)
    for path in latest:
        with path.open(newline="", encoding="utf-8") as handle:
            rows = list(csv.DictReader(handle))
        if any(str(row.get("medicine_name", "")).strip() for row in rows):
            return rows, relative_path(path)

    return [], ""


def latest_file(directory: Path, extensions: set[str]) -> Path | None:
    files = [
        path
        for path in directory.iterdir()
        if path.is_file() and path.suffix.lower() in extensions
    ]
    if not files:
        return None
    return max(files, key=lambda path: path.stat().st_mtime)


def read_csv_rows(path: Path | None) -> list[dict]:
    if path is None:
        return []
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


@router.post("/benefits")
def generate_benefits_api(request: BenefitsRequest):
    from modules.module_08_benefits import generate_genai_benefit

    medicines = request.medicines
    input_file = ""

    if not medicines and request.medicine_file_path.strip():
        medicine_path = resolve_project_file(request.medicine_file_path, [MEDICINE_DIR])
        with medicine_path.open(newline="", encoding="utf-8") as handle:
            medicines = list(csv.DictReader(handle))
        input_file = relative_path(medicine_path)

    if not medicines:
        medicines, input_file = latest_csv_rows(MEDICINE_DIR)

    if not medicines:
        raise HTTPException(
            status_code=400,
            detail="No detected medicines found. Run Medicine Detection first.",
        )

    benefits_output = []
    status_messages = []

    for item in medicines:
        medicine_name = str(item.get("medicine_name", "")).strip()
        category = str(item.get("category", "Unknown")).strip() or "Unknown"
        if not medicine_name:
            continue

        explanation, genai_status = generate_genai_benefit(
            medicine_name,
            category,
            request.use_api_genai,
        )
        status_messages.append(genai_status)
        benefits_output.append(
            {
                "medicine_name": medicine_name,
                "category": category,
                "benefit_explanation": explanation,
                "generation_method": genai_status,
                "patient_note": "Take this medicine only as prescribed by your doctor.",
            }
        )

    if not benefits_output:
        raise HTTPException(status_code=400, detail="Medicine rows did not contain medicine names.")

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    json_path = BENEFITS_DIR / f"medicine_benefits_{timestamp}.json"
    csv_path = BENEFITS_DIR / f"medicine_benefits_{timestamp}.csv"

    result = {
        "status": "success",
        "input_file": input_file,
        "benefits": benefits_output,
        "total_medicines": len(benefits_output),
        "generation_status": sorted(set(status_messages)),
        "json_file_path": relative_path(json_path),
        "csv_file_path": relative_path(csv_path),
        "created_at": str(datetime.now()),
    }

    json_path.write_text(json.dumps(result, indent=4), encoding="utf-8")
    with csv_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=benefits_output[0].keys())
        writer.writeheader()
        writer.writerows(benefits_output)

    return result


@router.get("/benefits/latest")
def latest_benefits_api():
    latest = sorted(BENEFITS_DIR.glob("*.json"), key=lambda path: path.stat().st_mtime, reverse=True)
    for path in latest:
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            continue

        benefits = data.get("benefits", [])
        if benefits:
            data["json_file_path"] = relative_path(path)
            return data

    raise HTTPException(
        status_code=404,
        detail="No generated benefits found. Click Generate Benefits first.",
    )


def normalize_interaction_medicine_name(name: str) -> str:
    cleaned = re.sub(
        r"\b\d+(\.\d+)?\s*(mg|mcg|g|ml|iu|units?|tablet|tablets|tab|capsule|capsules|cap)\b",
        "",
        str(name),
        flags=re.IGNORECASE,
    )
    cleaned = re.sub(r"\s+", " ", cleaned).strip()
    return cleaned.title()


def get_medicine_rows_for_analysis(medicines: list[dict], medicine_file_path: str) -> tuple[list[dict], str]:
    input_file = ""

    if medicines:
        return medicines, input_file

    if medicine_file_path.strip():
        medicine_path = resolve_project_file(medicine_file_path, [MEDICINE_DIR])
        with medicine_path.open(newline="", encoding="utf-8") as handle:
            return list(csv.DictReader(handle)), relative_path(medicine_path)

    return latest_csv_rows(MEDICINE_DIR)


@router.post("/interactions")
def check_interactions_api(request: InteractionsRequest):
    from modules.module_09_interactions import check_interaction

    medicine_rows, input_file = get_medicine_rows_for_analysis(
        request.medicines,
        request.medicine_file_path,
    )

    medicines = []
    seen = set()
    for row in medicine_rows:
        name = normalize_interaction_medicine_name(row.get("medicine_name", ""))
        if name and name not in seen:
            medicines.append(name)
            seen.add(name)

    if len(medicines) < 2:
        raise HTTPException(
            status_code=400,
            detail="At least two detected medicines are required to check interactions.",
        )

    interaction_results = []
    for med1, med2 in combinations(medicines, 2):
        interaction = check_interaction(med1, med2)
        interaction_results.append(
            {
                "medicine_1": med1,
                "medicine_2": med2,
                "risk_percent": interaction["risk"],
                "risk_level": interaction["level"],
                "warning": interaction["warning"],
            }
        )

    high_risk_count = sum(1 for item in interaction_results if item["risk_level"] == "High")
    moderate_risk_count = sum(1 for item in interaction_results if item["risk_level"] == "Moderate")
    low_risk_count = sum(1 for item in interaction_results if item["risk_level"] == "Low")

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    csv_path = INTERACTIONS_DIR / f"drug_interactions_{timestamp}.csv"
    json_path = INTERACTIONS_DIR / f"drug_interactions_{timestamp}.json"

    result = {
        "status": "success",
        "input_file": input_file,
        "medicines_checked": medicines,
        "total_pairs_checked": len(interaction_results),
        "high_risk_count": high_risk_count,
        "moderate_risk_count": moderate_risk_count,
        "low_risk_count": low_risk_count,
        "interaction_results": interaction_results,
        "csv_file_path": relative_path(csv_path),
        "json_file_path": relative_path(json_path),
        "created_at": str(datetime.now()),
    }

    json_path.write_text(json.dumps(result, indent=4), encoding="utf-8")
    with csv_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=interaction_results[0].keys())
        writer.writeheader()
        writer.writerows(interaction_results)

    return result


@router.get("/interactions/latest")
def latest_interactions_api():
    latest = sorted(INTERACTIONS_DIR.glob("*.json"), key=lambda path: path.stat().st_mtime, reverse=True)
    for path in latest:
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            continue

        interaction_results = data.get("interaction_results", [])
        if interaction_results:
            data["json_file_path"] = relative_path(path)
            return data

    raise HTTPException(
        status_code=404,
        detail="No generated interaction results found. Click Check Drug Interactions first.",
    )


@router.post("/recommendations")
def generate_recommendations_api(request: RecommendationsRequest):
    from modules.module_10_recommendations import get_recommendations

    medicine_rows, input_file = get_medicine_rows_for_analysis(
        request.medicines,
        request.medicine_file_path,
    )

    if not medicine_rows:
        raise HTTPException(
            status_code=400,
            detail="No detected medicines found. Run Medicine Detection first.",
        )

    recommendation_output = []
    for row in medicine_rows:
        medicine_name = str(row.get("medicine_name", "")).strip()
        category = str(row.get("category", "Unknown")).strip() or "Unknown"
        if not medicine_name:
            continue

        recommendations = get_recommendations(
            normalize_interaction_medicine_name(medicine_name),
            category,
        )
        recommendation_output.append(
            {
                "medicine_name": medicine_name,
                "category": category,
                "recommendations": ", ".join(recommendations),
                "note": "Use alternatives only after doctor consultation.",
            }
        )

    if not recommendation_output:
        raise HTTPException(status_code=400, detail="Medicine rows did not contain medicine names.")

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    csv_path = RECOMMENDATIONS_DIR / f"medicine_recommendations_{timestamp}.csv"
    json_path = RECOMMENDATIONS_DIR / f"medicine_recommendations_{timestamp}.json"

    result = {
        "status": "success",
        "input_file": input_file,
        "recommendations": recommendation_output,
        "total_medicines": len(recommendation_output),
        "csv_file_path": relative_path(csv_path),
        "json_file_path": relative_path(json_path),
        "created_at": str(datetime.now()),
    }

    json_path.write_text(json.dumps(result, indent=4), encoding="utf-8")
    with csv_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=recommendation_output[0].keys())
        writer.writeheader()
        writer.writerows(recommendation_output)

    return result


@router.get("/recommendations/latest")
def latest_recommendations_api():
    latest = sorted(RECOMMENDATIONS_DIR.glob("*.json"), key=lambda path: path.stat().st_mtime, reverse=True)
    for path in latest:
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            continue

        recommendations = data.get("recommendations", [])
        if recommendations:
            data["json_file_path"] = relative_path(path)
            return data

    raise HTTPException(
        status_code=404,
        detail="No generated recommendations found. Click Generate Recommendations first.",
    )


@router.get("/dashboard")
def dashboard_api():
    uploaded_image = latest_file(UPLOAD_DIR, {".jpg", ".jpeg", ".png"})
    preprocessed_image = latest_file(PREPROCESS_DIR, {".jpg", ".jpeg", ".png"})
    ocr_text_file = latest_file(OCR_DIR, {".txt"})
    medicine_csv = latest_file(MEDICINE_DIR, {".csv"})
    dosage_csv = latest_file(DOSAGE_DIR, {".csv"})
    benefits_csv = latest_file(BENEFITS_DIR, {".csv"})
    interactions_csv = latest_file(INTERACTIONS_DIR, {".csv"})
    recommendations_csv = latest_file(RECOMMENDATIONS_DIR, {".csv"})

    ocr_text = ""
    if ocr_text_file:
        ocr_text = ocr_text_file.read_text(encoding="utf-8")

    medicines = read_csv_rows(medicine_csv)
    dosage = read_csv_rows(dosage_csv)
    benefits = read_csv_rows(benefits_csv)
    interactions = read_csv_rows(interactions_csv)
    recommendations = read_csv_rows(recommendations_csv)

    high_risk = sum(1 for row in interactions if row.get("risk_level") == "High")
    moderate_risk = sum(1 for row in interactions if row.get("risk_level") == "Moderate")

    completed = sum(
        [
            uploaded_image is not None,
            preprocessed_image is not None,
            bool(ocr_text),
            bool(medicines),
            bool(dosage),
            bool(benefits),
            bool(interactions),
            bool(recommendations),
        ]
    )

    def file_info(path: Path | None):
        if path is None:
            return None
        return {
            "name": path.name,
            "path": relative_path(path),
            "url": output_url(path),
            "updated_at": datetime.fromtimestamp(path.stat().st_mtime).isoformat(),
        }

    return {
        "status": "success",
        "completed_steps": completed,
        "total_steps": 8,
        "files": {
            "uploaded_image": file_info(uploaded_image),
            "preprocessed_image": file_info(preprocessed_image),
            "ocr_text": file_info(ocr_text_file),
            "medicines": file_info(medicine_csv),
            "dosage": file_info(dosage_csv),
            "benefits": file_info(benefits_csv),
            "interactions": file_info(interactions_csv),
            "recommendations": file_info(recommendations_csv),
        },
        "ocr_text": ocr_text,
        "medicines": medicines,
        "dosage": dosage,
        "benefits": benefits,
        "interactions": interactions,
        "recommendations": recommendations,
        "counts": {
            "medicines": len(medicines),
            "dosage": len(dosage),
            "benefits": len(benefits),
            "interactions": len(interactions),
            "recommendations": len(recommendations),
            "high_risk_interactions": high_risk,
            "moderate_risk_interactions": moderate_risk,
        },
    }


def serialize_mongo_value(value):
    if isinstance(value, datetime):
        return value.isoformat()
    if isinstance(value, list):
        return [serialize_mongo_value(item) for item in value]
    if isinstance(value, dict):
        return {key: serialize_mongo_value(item) for key, item in value.items()}
    return str(value) if value.__class__.__name__ == "ObjectId" else value


def get_mongo_connection():
    if MongoClient is None:
        raise RuntimeError("pymongo is not installed. Run: python -m pip install -r requirements.txt")

    uri = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
    db_name = os.getenv("MONGODB_DB_NAME", "ai_prescription_reader")
    timeout = int(os.getenv("MONGODB_TIMEOUT", "5000"))
    client = MongoClient(uri, serverSelectionTimeoutMS=timeout, connectTimeoutMS=timeout)
    client.admin.command("ping")
    return client, client[db_name], uri, db_name


@router.get("/database/status")
def database_status_api():
    try:
        client, db, uri, db_name = get_mongo_connection()
        collections = ["prescriptions", "medicines", "reports"]
        stats = {
            name: {"total_documents": db[name].count_documents({})}
            for name in collections
        }
        client.close()
        return {
            "status": "connected",
            "database_name": db_name,
            "uri_configured": bool(uri),
            "collections": stats,
        }
    except (PyMongoError, ServerSelectionTimeoutError, Exception) as error:
        return {
            "status": "disconnected",
            "database_name": os.getenv("MONGODB_DB_NAME", "ai_prescription_reader"),
            "uri_configured": bool(os.getenv("MONGODB_URI", "")),
            "error": str(error),
            "collections": {
                "prescriptions": {"total_documents": 0},
                "medicines": {"total_documents": 0},
                "reports": {"total_documents": 0},
            },
        }


@router.post("/database/store-latest")
def database_store_latest_api(request: StoreAnalysisRequest):
    dashboard = dashboard_api()

    try:
        client, db, _, db_name = get_mongo_connection()
        document = {
            "user_id": request.user_id.strip() or "Guest",
            "file_name": request.file_name.strip() or "latest_prescription",
            "medicines": dashboard["medicines"],
            "dosage": dashboard["dosage"],
            "benefits": dashboard["benefits"],
            "interactions": dashboard["interactions"],
            "recommendations": dashboard["recommendations"],
            "ocr_text": dashboard["ocr_text"],
            "metadata": {"source": "React/FastAPI latest dashboard"},
            "created_at": datetime.now(),
            "updated_at": datetime.now(),
        }
        result = db["prescriptions"].insert_one(document)
        client.close()
        return {
            "status": "success",
            "database_name": db_name,
            "prescription_id": str(result.inserted_id),
        }
    except Exception as error:
        raise HTTPException(
            status_code=503,
            detail=f"MongoDB storage failed: {error}",
        )


@router.get("/database/records")
def database_records_api(user_id: str = "", limit: int = 10):
    try:
        client, db, _, db_name = get_mongo_connection()
        query = {"user_id": user_id} if user_id else {}
        records = list(
            db["prescriptions"]
            .find(query)
            .sort("created_at", -1)
            .limit(max(1, min(limit, 50)))
        )
        client.close()
        return {
            "status": "success",
            "database_name": db_name,
            "records": [serialize_mongo_value(record) for record in records],
        }
    except Exception as error:
        return {
            "status": "disconnected",
            "database_name": os.getenv("MONGODB_DB_NAME", "ai_prescription_reader"),
            "records": [],
            "error": f"MongoDB records unavailable: {error}",
        }


@router.post("/clear-outputs")
def clear_outputs_api():
    deleted_files = 0
    deleted_dirs = 0

    for directory in OUTPUT_DIRECTORIES:
        directory.mkdir(parents=True, exist_ok=True)
        for path in directory.iterdir():
            if path.is_file():
                path.unlink()
                deleted_files += 1
            elif path.is_dir():
                shutil.rmtree(path)
                deleted_dirs += 1

    return {
        "status": "success",
        "deleted_files": deleted_files,
        "deleted_dirs": deleted_dirs,
    }
