# Download embeddingmodel from Hugging Face and save it physically to a local folder for later use in the project.

from sentence_transformers import SentenceTransformer
from poc_rag.config_env import EMBEDDING_MODEL_NAME, EMBEDDING_MODEL_LOCAL_PATH

def download_and_save():
    print("Downloading and loading the model from Hugging Face...")
    model = SentenceTransformer(EMBEDDING_MODEL_NAME)

    print("Saving the model physically to the local folder...")
    model.save(EMBEDDING_MODEL_LOCAL_PATH)
    print(f"Model saved successfully to {EMBEDDING_MODEL_LOCAL_PATH}")

if __name__ == "__main__":
    download_and_save()