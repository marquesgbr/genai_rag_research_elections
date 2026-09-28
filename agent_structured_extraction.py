import argparse
from pathlib import Path

import polars as pl
from agno.agent import Agent
from agno.models.google import Gemini

from config_env import GEMINI_API_KEY, GEMINI_MODEL_ID, SILVER_DATASET_COLUMNS
from schema import (
    OutputSchema,
    ProposalSchema,
    build_output_row,
    load_silver_dataset,
)


PROPOSALS_OUTPUT_COLUMNS = SILVER_DATASET_COLUMNS + [
    "is_proposal",
    "theme",
    "objective",
    "proposed_action",
    "target_population",
    "quantitative_target",
    "deadline",
]


def build_extraction_agent() -> Agent:
    if not GEMINI_API_KEY:
        raise ValueError("GEMINI_API_KEY não foi definida no ambiente.")

    return Agent(
        model=Gemini(id=GEMINI_MODEL_ID, api_key=GEMINI_API_KEY),
        output_schema=ProposalSchema,
        structured_outputs=True,
        description=(
            "Você é um especialista em analisar planos de governo "
            "e extrair propostas políticas."
        ),
        instructions=(
            "Leia o trecho fornecido. Se não houver metas numéricas ou "
            "prazos explícitos, retorne null."
        ),
    )


def extract_proposal(agent: Agent, text: str) -> ProposalSchema:
    response = agent.run(text)
    proposal = response.content
    if not isinstance(proposal, ProposalSchema):
        proposal = getattr(response, "data", None)
    if not isinstance(proposal, ProposalSchema):
        raise TypeError("O agente não retornou uma ProposalSchema válida.")
    return proposal


def upsert_proposals(rows: list[OutputSchema], output_path: str | Path) -> Path:
    """Atualiza chunks existentes e adiciona chunks novos no Parquet final."""
    path = Path(output_path)
    new_df = pl.DataFrame([row.model_dump() for row in rows])

    if path.exists():
        existing_df = pl.read_parquet(path).select(PROPOSALS_OUTPUT_COLUMNS)
        new_df = pl.concat([existing_df, new_df], how="vertical_relaxed")

    new_df = new_df.select(PROPOSALS_OUTPUT_COLUMNS).unique(
        subset=["chunk_id"], keep="last", maintain_order=True
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    new_df.write_parquet(path)
    return path


def process_dataset(
    input_path: str | Path,
    output_path: str | Path,
    limit: int | None = None,
    agent: Agent | None = None,
) -> Path:
    df_silver = load_silver_dataset(input_path)
    if limit is not None:
        if limit < 1:
            raise ValueError("O limite deve ser maior que zero.")
        df_silver = df_silver.head(limit)

    extraction_agent = agent or build_extraction_agent()
    rows: list[OutputSchema] = []
    raw_chunks = df_silver.to_dicts()
    for raw_chunk in raw_chunks:
        chunk = {str(key): value for key, value in raw_chunk.items()}
        proposal = extract_proposal(extraction_agent, chunk["text"])
        rows.append(build_output_row(chunk, proposal))

    if not rows:
        raise ValueError("O dataset não contém chunks para processar.")
    return upsert_proposals(rows, output_path)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Extrai propostas estruturadas de um dataset Silver."
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
