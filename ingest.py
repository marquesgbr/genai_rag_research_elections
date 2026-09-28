
import psycopg
import json
from pathlib import Path

from config_env import DB_URL, EMBEDDING_MODEL_LOCAL_PATH
from sentence_transformers import SentenceTransformer

def load_dataset(file_path="data/toydataset.json"):
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def instantiate_model(model_name=EMBEDDING_MODEL_LOCAL_PATH):
    model = SentenceTransformer(model_name)
    return model

def generate_embeddings(chunks: list[dict]):
    model = instantiate_model()
    texts = [chunk['text'] for chunk in chunks]
    embeddings = model.encode(texts).tolist()
    for chunk, emb in zip(chunks, embeddings):
        chunk['embedding'] = emb
    return chunks

def insert_chunks_into_db(chunks: list[dict]):
    try:
        with psycopg.connect(DB_URL) as conn:
            with conn.cursor() as cursor:

                # %s placeholders are used to let psycopg handle the proper formatting required
                insert_query = """
                INSERT INTO chunks (chunk_id, document_id, page, section, text, chunk_index, n_chars, dataset_version, candidate, party, office, state, embedding)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (chunk_id) DO UPDATE SET
                    document_id = EXCLUDED.document_id,
                    page = EXCLUDED.page,
                    section = EXCLUDED.section,
                    text = EXCLUDED.text,
                    chunk_index = EXCLUDED.chunk_index,
                    n_chars = EXCLUDED.n_chars,
                    dataset_version = EXCLUDED.dataset_version,
                    candidate = EXCLUDED.candidate,
                    party = EXCLUDED.party,
                    office = EXCLUDED.office,
                    state = EXCLUDED.state,
                    embedding = EXCLUDED.embedding;
                """

                records = [
                    (
                        chunk['chunk_id'],
                        chunk['document_id'],
                        chunk['page'],
                        chunk['section'],
                        chunk['text'],
                        chunk['chunk_index'],
                        chunk['n_chars'],
                        chunk['dataset_version'],
                        chunk['candidate'],
                        chunk['party'],
                        chunk['office'],
                        chunk['state'],
                        chunk['embedding'] 
                    ) for chunk in chunks
                ]

                cursor.executemany(insert_query, records)
                
    except Exception as e:
        print(f"Error inserting chunks into the database: {e}")
        raise


def ingest_dataset(file_path: str | Path = "data/toydataset.json") -> None:
    chunks = load_dataset(file_path)
    chunks_with_embeddings = generate_embeddings(chunks)
    insert_chunks_into_db(chunks_with_embeddings)

def main():
    print("Starting data ingestion process. This may take a few minutes depending on the number of chunks"
    " and the model used for generating embeddings.")

    print("Generating embeddings for the chunks...")
    dataset_jsonfile = "data/toydataset.json"
    print("Connecting to the database and inserting chunks with embeddings...")
    ingest_dataset(dataset_jsonfile)
    
    print("Data ingestion completed successfully.")

if __name__ == "__main__":
    main()