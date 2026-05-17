from fastapi import APIRouter

router = APIRouter()


@router.get("/")
def hello_message():
    return {"message": "This the backend for the matching system!"}
