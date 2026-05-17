from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.api.routers import healthRouter, helloRouter, matchRouter,embeddingRouter
from backend.api.utils.embedder import load_model
from backend.api.utils.mongo_database import get_mongo_connection
from backend.api.utils.sql_database import get_sql_connection
from config.config import MODEL_NAME


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    app.state.model = load_model(MODEL_NAME)
    app.state.mongo = get_mongo_connection()
    app.state.sql   = get_sql_connection()
    yield
    # Shutdown
    app.state.sql.close()
    app.state.mongo.close()


app = FastAPI(lifespan=lifespan)  # ← lifespan passed here

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(healthRouter.router)
app.include_router(helloRouter.router)
app.include_router(matchRouter.app)
app.include_router(embeddingRouter.router)


if __name__ == "__main__":
    uvicorn.run("backend.main:app", host="127.0.0.1", port=8000, reload=True)