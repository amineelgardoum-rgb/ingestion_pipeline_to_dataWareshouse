from pymongo import MongoClient
from config.config import MONGO_URI, MONGO_DB, MONGO_COLLECTION



def get_mongo_connection() -> MongoClient:
    return MongoClient(MONGO_URI)


def clear_embeddings(client: MongoClient) -> int:
    collection = client[MONGO_DB][MONGO_COLLECTION]
    result = collection.delete_many({})
    return result.deleted_count

def embedding_exists(client: MongoClient, job_id: str) -> bool:

    collection = client[MONGO_DB][MONGO_COLLECTION]

    result = collection.find_one(
        {"job_id": job_id},
        {"_id": 1}
    )

    return result is not None

def save_job_embedding(
    client: MongoClient,
    job: dict,
    embedding: list
) -> None:
    collection = client[MONGO_DB][MONGO_COLLECTION]
    collection.update_one(
        {"job_id": job["job_id"]},
        {"$set": {
            "job_id":    job["job_id"],
            "title":     job["title"],
            "company":   job["company"],
            "job_type":  job["job_type"],
            "location":  job["location"],
            "is_remote": job["is_remote"],
            "job_url":   job["job_url"],
            "job_date":  job["job_date"],
            "embedding": embedding
        }},
        upsert=True
    )


def get_all_embeddings(client: MongoClient) -> list[dict]:
    collection = client[MONGO_DB][MONGO_COLLECTION]
    return list(collection.find({}, {
        "job_id":    1,
        "title":     1,
        "company":   1,
        "job_type":  1,
        "location":  1,
        "is_remote": 1,
        "job_url":   1,
        "job_date":  1,
        "embedding": 1
    }))


    
def count_embeddings(client: MongoClient) -> int:
    collection = client[MONGO_DB][MONGO_COLLECTION]
    return collection.count_documents({})


def close_mongo_connection(client: MongoClient) -> None:
    client.close()