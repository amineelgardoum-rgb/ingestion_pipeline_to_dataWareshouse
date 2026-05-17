import shutil
import tempfile
from fastapi import APIRouter, UploadFile, File, HTTPException,Request
from backend.api.utils.embedder import load_model
from backend.api.utils.extractor import extract_text
from backend.api.utils.mongo_database import get_mongo_connection, close_mongo_connection
from backend.api.utils.matcher import match_cv
from backend.api.helpers.cleaner import clean_text

app = APIRouter()







@app.post("/match-cv")
async def match_cv_endpoint(request:Request,file: UploadFile = File(...)):
    model = request.app.state.model
    mongo_client=request.app.state.mongo
    # validate file type
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are accepted.")

    # save uploaded file to a temp location
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        shutil.copyfileobj(file.file, tmp)
        tmp_path = tmp.name

    try:
        cv_text = extract_text(tmp_path)
        cv_text = clean_text(cv_text)

        if not cv_text.strip():
            raise HTTPException(status_code=422, detail="Could not extract text from the PDF.")

        results = match_cv(model, mongo_client, cv_text)

        return {
            "filename": file.filename,
            "matches":  results
        }

    except ValueError as e:
        raise HTTPException(status_code=500, detail=str(e))

    finally:
        import os
        os.remove(tmp_path)


