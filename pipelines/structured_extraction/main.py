import argparse

from agent_structured_extraction import process_dataset


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Executa o pipeline de extração estruturada de propostas."
    )
    parser.add_argument(
        "--input",
        default="data/toydataset.json",
        help="Arquivo Silver de entrada (.json ou .parquet).",
    )
    parser.add_argument(
        "--output",
        default="data/StructuredProposals.parquet",
        help="Arquivo Parquet de saída.",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help="Processa somente os primeiros N chunks.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        output_path = process_dataset(
            input_path=args.input,
            output_path=args.output,
            limit=args.limit,
        )
    except Exception as error:
        print(f"Erro na extração estruturada: {error}")
        return 1

    print(f"Extração concluída. Resultado salvo em: {output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())