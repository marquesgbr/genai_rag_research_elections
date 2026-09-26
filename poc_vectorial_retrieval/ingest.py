
import psycopg
import json

from poc_rag.config_env import DB_URL, EMBEDDING_MODEL_LOCAL_PATH
from sentence_transformers import SentenceTransformer

def load_dataset(file_path='toydataset.json'):
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
                INSERT INTO chunks (chunk_id, document_id, page, section, text, candidate, party, office, state, embedding) 
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (chunk_id) DO UPDATE SET
                    document_id = EXCLUDED.document_id,
                    page = EXCLUDED.page,
                    section = EXCLUDED.section,
                    text = EXCLUDED.text,
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
        raise e

def main():
    print("Starting data ingestion process. This may take a few minutes depending on the number of chunks"
    " and the model used for generating embeddings.")

    dataset_jsonfile = 'toydataset.json'
    chunks = load_dataset(dataset_jsonfile)

    print("Generating embeddings for the chunks...")
    chunks_with_embeddings = generate_embeddings(chunks)

    print("Connecting to the database and inserting chunks with embeddings...")
    insert_chunks_into_db(chunks_with_embeddings)
    
    print("Data ingestion completed successfully.")

if __name__ == "__main__":
    main()