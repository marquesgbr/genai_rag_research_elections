"""Smoke test real da extração estruturada usando um chunk de um Parquet."""

import argparse
from pathlib import Path

from agent_structured_extraction import build_extraction_agent, extract_proposal
from schema import json_to_parquet, load_silver_dataset


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Testa a extração de uma proposta a partir de um Parquet."
    )
    parser.add_argument(
        "--input",
        type=Path,
        default=Path("data/silver.parquet"),
        help="Parquet Silver de entrada.",
    )
    parser.add_argument(
        "--source-json",
        type=Path,
        default=Path("data/toydataset.json"),
        help="JSON usado para criar o Parquet caso ele não exista.",
    )
    parser.add_argument(
        "--row",
        type=int,
        default=0,
        help="Índice zero-based do chunk a ser testado.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()

    if args.row < 0:
        print("Erro: --row deve ser maior ou igual a zero.")
        return 1

    if not args.input.exists():
        print(f"Parquet não encontrado. Criando: {args.input}")
        try:
            json_to_parquet(args.source_json, args.input)
        except Exception as error:
            print(f"Erro ao criar o Parquet: {error}")
            return 1

    try:
        silver_dataset = load_silver_dataset(args.input)
        if args.row >= len(silver_dataset):
            print(
                f"Erro: o Parquet possui {len(silver_dataset)} chunks; "
                f"o índice solicitado foi {args.row}."
            )
            return 1

        chunk = silver_dataset.row(args.row, named=True)
        print(f"Processando chunk: {chunk['chunk_id']}")
        print(f"Texto: {chunk['text']}")

        agent = build_extraction_agent()
        proposal = extract_proposal(agent, str(chunk["text"]))

    except Exception as error:
        print(f"Erro no smoke test: {error}")
        return 1

    print("\nProposalSchema retornado:")
    for field, value in proposal.model_dump().items():
        print(f"{field}: {value}")
    print("\nSmoke test concluído com sucesso.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())