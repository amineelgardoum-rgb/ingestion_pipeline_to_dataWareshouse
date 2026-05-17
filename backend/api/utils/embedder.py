from sentence_transformers import SentenceTransformer
from config.config import MODEL_NAME


def load_model(model_name: str = MODEL_NAME) -> SentenceTransformer:
    print(f"Loading model: {model_name}")
    return SentenceTransformer(model_name)


def build_job_text(job: dict) -> str:
    parts = [
        f"Title: {job['title']}",
        f"Company: {job['company']}",
        f"Job type: {job['job_type']}",
        f"Location: {job['location']}",
        f"Remote: {job['is_remote']}",
        f"Description: {job['description']}",
    ]
    return "\n".join(
        p for p in parts if p.split(": ", 1)[1]
    )


def embed(model: SentenceTransformer, text: str):
    return model.encode(text, convert_to_tensor=True)


def embed_batch(model: SentenceTransformer, texts: list[str]):
    return model.encode(
        texts,
        batch_size=64,
        show_progress_bar=True,
        convert_to_tensor=True
    )