import psycopg
from poc_rag.config_env import DB_URL, EMBEDDING_VECTOR_DIM

def init_db_table():
    try:
        print("Initializing the database connection...")
        with psycopg.connect(DB_URL, autocommit=True) as conn:
            with conn.cursor() as cursor:

                print("Enabling pgvector Extension...")
                cursor.execute("CREATE EXTENSION IF NOT EXISTS vector;")

                print("Creating 'chunks' table...")

                create_table_query = """
                CREATE TABLE IF NOT EXISTS chunks (
                    chunk_id VARCHAR(100) PRIMARY KEY,
                    document_id VARCHAR(50) NOT NULL,
                    page INT NOT NULL, 
                    section VARCHAR(100),
                    text TEXT NOT NULL,
                    candidate VARCHAR(100),
                    party VARCHAR(50),
                    office VARCHAR(50),
                    state VARCHAR(2),
                    embedding vector(%s)
                );
                """

                cursor.execute(create_table_query, (EMBEDDING_VECTOR_DIM,))

                print("Database initialized successfully")
                
    except Exception as e:
        print(f"Error initializing the database: {e}")


if __name__ == "__main__":
    init_db_table()