from dotenv import load_dotenv
import os

load_dotenv()

MODEL_NAME = "all-MiniLM-L6-v2"

# SQL Server
SQL_SERVER   = os.getenv("SQL_SERVER")
SQL_DATABASE = os.getenv("SQL_DATABASE")
SQL_USERNAME = os.getenv("SQL_USERNAME")
SQL_PASSWORD = os.getenv("SQL_PASSWORD")
SQL_DRIVER   = os.getenv("SQL_DRIVER", "ODBC Driver 17 for SQL Server")
SQL_SCHEMA   = "gold"

# MongoDB
MONGO_URI        = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
MONGO_DB         = os.getenv("MONGO_DB", "vector_store")
MONGO_COLLECTION = os.getenv("MONGO_COLLECTION", "job_embeddings")

TOP_K            = 10
SCORE_THRESHOLD  = 0.40