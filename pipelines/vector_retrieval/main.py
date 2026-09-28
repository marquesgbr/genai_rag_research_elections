import argparse

from sentence_transformers import SentenceTransformer

from config_env import EMBEDDING_MODEL_LOCAL_PATH
from db_setup import init_db_table
from ingest import ingest_dataset
from vec_search import search_similar_texts, show_results


DEFAULT_QUERY = "melhorar o atendimento médico remoto"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Inicializa, popula e consulta o pipeline de retrieval vetorial."
    )
    parser.add_argument(
        "--input",
        default="data/toydataset.json",
        help="Dataset JSON usado para gerar e persistir os embeddings.",
    )
    parser.add_argument(
        "--query",
        default=DEFAULT_QUERY,
        help="Consulta textual enviada ao retrieval.",
    )
    parser.add_argument("--top-k", type=int, default=3)
    parser.add_argument(
        "--skip-setup",
        action="store_true",
        help="Não cria a extensão e a tabela antes da ingestão.",
    )
    parser.add_argument(
        "--skip-ingest",
        action="store_true",
        help="Consulta a tabela sem regenerar os embeddings.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.top_k < 1:
        print("Erro: --top-k deve ser maior que zero.")
        return 1

    try:
        if not args.skip_setup:
            init_db_table()
        if not args.skip_ingest:
            ingest_dataset(args.input)

        model = SentenceTransformer(EMBEDDING_MODEL_LOCAL_PATH)
        results = search_similar_texts(model, args.query, top_k=args.top_k)
    except Exception as error:
        print(f"Erro no retrieval vetorial: {error}")
        return 1

    print(f"QUERY: {args.query}\nTOP-{args.top_k} RESULTADOS\n")
    show_results(results)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())