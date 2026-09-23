import psycopg
from config_env import DB_URL, EMBEDDING_MODEL_LOCAL_PATH
from sentence_transformers import SentenceTransformer


def search_similar_texts(model: SentenceTransformer, query_text: str, top_k: int = 3):
    try:
        with psycopg.connect(DB_URL) as conn:
            with conn.cursor() as cursor:
                embedding = model.encode(query_text).tolist()
                
                search_query = """
                SELECT chunk_id, page, section, text, 1 - (embedding <=> %s::vector) AS similarity
                FROM chunks
                ORDER BY similarity DESC
                LIMIT %s;
                """
                
                cursor.execute(search_query, (embedding, top_k))
                
                return cursor.fetchall()
                
    except Exception as e:
        print(f"Erro na busca vetorial: {e}")
        return []

def show_results(results):
    for i, row in enumerate(results, start=1):
        chunk_id, page, section, text, similarity = row
        
        print(f"{i}. {chunk_id} | score: {similarity:.2f} | página: {page} | seção: {section}")
        print(f"   {text}\n")

def main():
    k = 3
    model = SentenceTransformer(EMBEDDING_MODEL_LOCAL_PATH)

    print("Consulta parecida com trecho existente")
    query = "melhorar o atendimento médico remoto"
    print(f"QUERY: {query}\nTOP-{k} RESULTADOS\n")
    results = search_similar_texts(model, query, top_k=k)
    show_results(results)

    print("Consulta semelhante à primeira mas com palavras diferentes")
    query = "maior disponibiliade e qualidade de serviços médicos à distância"
    print(f"QUERY: {query}\nTOP-{k} RESULTADOS\n")
    results = search_similar_texts(model, query, top_k=k)
    show_results(results)

    print("Consulta ambígua com resultados semanticamente diferentes mas similaridades altas")
    query = "ajuste de impostos para pequenas empresas"
    print(f"QUERY: {query}\nTOP-{k} RESULTADOS\n")
    results = search_similar_texts(model, query, top_k=k)
    show_results(results)

    print("Consulta sem resultados semanticamente relacionados")
    query = "criar bolsa 5G para estagiários"
    print(f"QUERY: {query}\nTOP-{k} RESULTADOS\n")
    results = search_similar_texts(model, query, top_k=k)
    show_results(results)



if __name__ == "__main__":
    main()