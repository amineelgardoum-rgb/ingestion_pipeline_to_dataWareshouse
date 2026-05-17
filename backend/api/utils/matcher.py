import torch
from sentence_transformers import SentenceTransformer, util
from pymongo import MongoClient

from backend.api.utils.embedder import embed, embed_batch, build_job_text
from backend.api.utils.mongo_database import (
    save_job_embedding,
    get_all_embeddings,
    count_embeddings,
    embedding_exists
)
from config.config import TOP_K, SCORE_THRESHOLD


def compute_and_store_embeddings(
    model: SentenceTransformer,
    mongo_client: MongoClient,
    jobs: list[dict]
) -> None:
    jobs_to_embed=[]
    for job in jobs:
        if embedding_exists(mongo_client,job["job_id"]):
            print(f"Skipping existing embeddings:{job['job_id']}")
            continue
        jobs_to_embed.append(job)
    if not jobs_to_embed:
        print("All embeddings already exist")
        return 

    texts = [build_job_text(job) for job in jobs]
    embeddings = embed_batch(model, texts)
    for job, emb in zip(jobs, embeddings):
        save_job_embedding(mongo_client, job, emb.tolist())
    print(f"✓ Stored {len(jobs)} embeddings in MongoDB")


def match_cv(
    model: SentenceTransformer,
    mongo_client: MongoClient,
    cv_text: str
) -> list[dict]:
    total = count_embeddings(mongo_client)
    if total == 0:
        raise ValueError(
            "No embeddings found in MongoDB. "
            "Run scripts/precompute_embeddings.py first."
        )

    print(f"✓ Loaded {total} job embeddings from MongoDB")
    records  = get_all_embeddings(mongo_client)
    job_embs = torch.tensor([r["embedding"] for r in records])
    cv_emb   = embed(model, cv_text)

    scores = util.cos_sim(cv_emb, job_embs)[0]
    top    = scores.topk(min(TOP_K, len(records)))

    return [
        {
            "job_id":    records[i]["job_id"],
            "title":     records[i]["title"],
            "company":   records[i]["company"],
            "job_type":  records[i]["job_type"],
            "location":  records[i]["location"],
            "is_remote": records[i]["is_remote"],
            "job_url":   records[i]["job_url"],
            "job_date":  records[i]["job_date"],
            "score":     round(float(s), 3)
        }
        for s, i in zip(top.values, top.indices)
        if float(s) >= SCORE_THRESHOLD
    ]