from fastapi import APIRouter

router = APIRouter()

@router.post("/interaction")
def interaction_api():

    return {
        "status": "success",
        "module": "Drug Interaction API"
    }