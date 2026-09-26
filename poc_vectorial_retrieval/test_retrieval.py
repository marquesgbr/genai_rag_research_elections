import pytest
from poc_rag.config_env import EMBEDDING_MODEL_LOCAL_PATH
from sentence_transformers import SentenceTransformer
from poc_rag.vec_search import search_similar_texts


@pytest.fixture(scope="module")
def model():
    """Fixture para carregar o modelo local uma única vez durante os testes."""
    return SentenceTransformer(EMBEDDING_MODEL_LOCAL_PATH)


def test_embedding_dimension(model):
    """Garante que o modelo local gera vetores na dimensão esperada pelo pgvector (384)."""
    text = "Teste de dimensão de vetor"
    vector = model.encode(text)
    assert vector.shape == (384,), f"Esperado vetor de (384,), retornado {vector.shape}"


def test_top_k_retrieval_limit(model):
    """Valida se o parâmetro top_k altera a quantidade de resultados retornados."""
    query = "saúde e atendimento médico"
    
    res_k1 = search_similar_texts(model, query, top_k=1)
    res_k3 = search_similar_texts(model, query, top_k=3)
    
    assert len(res_k1) == 1
    assert len(res_k3) == 3


def test_similarity_score_ordering(model):
    """Valida se os resultados estão estritamente ordenados do maior score para o menor."""
    query = "tecnologia na educação e escolas"
    results = search_similar_texts(model, query, top_k=3)
    
    assert len(results) > 1, "A base precisa ter mais de 1 registro para testar a ordenação"
    
    scores = [row[4] for row in results]  # Posição 4 é a similarity na query SQL
    
    # Verifica se a lista de scores é decrescente
    assert scores == sorted(scores, reverse=True), f"Scores não estão ordenados: {scores}"


def test_result_structure(model):
    """Valida se a tupla retornada contém os campos essenciais do schema (chunk_id, page, section, text, score)."""
    query = "transporte público"
    results = search_similar_texts(model, query, top_k=1)
    
    assert len(results) == 1
    row = results[0]
    
    chunk_id, page, section, text, similarity = row
    
    assert isinstance(chunk_id, str)
    assert isinstance(page, int)
    assert isinstance(text, str)
    assert 0.0 <= similarity <= 1.0, f"Score fora do intervalo válido (0-1): {similarity}"


def test_empty_query_handling(model):
    """Garante que buscas com texto vazio não quebrem o pipeline nem o SQL."""
    query = ""
    results = search_similar_texts(model, query, top_k=2)
    assert isinstance(results, list)