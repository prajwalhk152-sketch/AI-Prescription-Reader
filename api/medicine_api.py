from fastapi import APIRouter

router = APIRouter()

@router.post("/medicine")
def medicine_api():

    return {
        "status": "success",
        "module": "Medicine Detection API"
    }