from fastapi import APIRouter, HTTPException, Request

from backend.api.utils.embedder import embed_batch, build_job_text
from backend.api.utils.sql_database import get_jobs
from backend.api.utils.mongo_database import embedding_exists, save_job_embedding

router = APIRouter()


@router.post("/embedding")
def embedding_endpoint(request: Request):
    model = request.app.state.model
    mongo = request.app.state.mongo
    sql = request.app.state.sql

    try:
        jobs = get_jobs(sql)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Failed to fetch jobs: {exc}")

    # Skip jobs that already have embeddings
    jobs_to_embed = [
        job for job in jobs
        if not embedding_exists(mongo, job["job_id"])
    ]

    if not jobs_to_embed:
        return {"message": "All embeddings already exist, nothing to do."}

    try:
        texts = [build_job_text(job) for job in jobs_to_embed]
        embeddings = embed_batch(model, texts)

        for job, emb in zip(jobs_to_embed, embeddings):
            save_job_embedding(mongo, job, emb.tolist())

    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Embedding failed: {exc}")

    return {
        "message": "Embeddings computed and stored successfully.",
        "stored": len(jobs_to_embed),
        "skipped": len(jobs) - len(jobs_to_embed),
    }