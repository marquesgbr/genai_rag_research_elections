import psycopg2
from db_config import DB_URL

def init_db():
    try:
        print("Initializing the database connection...")
        conn = psycopg2.connect(DB_URL)
        cursor = conn.cursor()

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
            embedding vector(384)
        );
        """

        cursor.execute(create_table_query)
        conn.commit()

        print("Database initialized successfully")

        cursor.close()
        conn.close()

    except Exception as e:
        print(f"Error initializing the database: {e}")

if __name__ == "__main__":
    init_db()