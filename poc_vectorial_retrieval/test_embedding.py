from sentence_transformers import SentenceTransformer
from poc_rag.config_env import EMBEDDING_MODEL_LOCAL_PATH

# 1. Load a pretrained Sentence Transformer model
model = SentenceTransformer(EMBEDDING_MODEL_LOCAL_PATH) 

# The sentences to encode
sentences = [
    "O clima está ótimo hoje.",
    "It's so sunny outside!",
    "Ele dirigiu até o estádio",
]

# 2. Calculate embeddings by calling model.encode()
embeddings = model.encode(sentences)
print(embeddings.shape)
# [3, 384]

# 3. Calculate the embedding similarities
similarities = model.similarity(embeddings, embeddings)
print(similarities)

# tensor([[1.0000, 0.6768, 0.1268],
#         [0.6768, 1.0000, 0.2386],
#         [0.1268, 0.2386, 1.0000]])