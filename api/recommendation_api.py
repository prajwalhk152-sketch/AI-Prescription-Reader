from fastapi import APIRouter

router = APIRouter()

@router.post("/recommendation")
def recommendation_api():

    return {
        "status": "success",
        "module": "Recommendation API"
    }