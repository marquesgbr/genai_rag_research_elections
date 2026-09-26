import os
from dotenv import load_dotenv

load_dotenv()  # carregar variáveis de ambiente do arquivo .env

# required_vars = ["DB_HOST", "DB_PORT", "DB_NAME", "DB_USER", "DB_PASSWORD"]
# missing_vars = [var for var in required_vars if not os.getenv(var)]
# if missing_vars:
#     raise ValueError(f"Missing required environment variables: {', '.join(missing_vars)}")

DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "rag_vector_db")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "led_senha")
DB_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

EMBEDDING_MODEL_NAME = os.getenv("EMBEDDING_MODEL_NAME", "paraphrase-multilingual-MiniLM-L12-v2")
EMBEDDING_MODEL_LOCAL_PATH = os.getenv("EMBEDDING_MODEL_LOCAL_PATH", "models/multilingual_miniLM_L12_v2")
EMBEDDING_VECTOR_DIM = int(os.getenv("EMBEDDING_VECTOR_DIM", "384"))



