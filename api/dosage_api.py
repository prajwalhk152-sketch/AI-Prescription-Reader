from fastapi import APIRouter

router = APIRouter()

@router.post("/dosage")
def dosage_api():

    return {
        "status": "success",
        "module": "Dosage API"
    }