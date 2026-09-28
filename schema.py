from pathlib import Path
from typing import Any, Optional

import polars as pl
from pydantic import BaseModel, Field

from config_env import SILVER_DATASET_COLUMNS


class ProposalSchema(BaseModel):
    is_proposal: str = Field(
        description="Obrigatório. Indica se o trecho contém uma proposta. Retorne 'sim' ou 'nao'."
    )
    theme: str = Field(
        description="Obrigatório. O tema geral do trecho (ex: saúde, educação, segurança)."
    )
    objective: Optional[str] = Field(
        default=None,
        description="O que se quer alcançar com a ação."
    )
    proposed_action: Optional[str] = Field(
        default=None,
        description="A ação de fato que será feita."
    )
    target_population: Optional[str] = Field(
        default=None,
        description="O público atingido. Retorne null/None se não houver citação explícita."
    )
    quantitative_target: Optional[str] = Field(
        default=None,
        description="Metas numéricas. Retorne null/None se não houver citação explícita."
    )
    deadline: Optional[str] = Field(
        default=None,
        description="Prazos definidos. Retorne null/None se não houver citação explícita."
    )

class OutputSchema(BaseModel):
    chunk_id: str
    document_id: str
    page: int
    section: Optional[str] = None
    chunk_index: int
    text: str
    n_chars: int
    dataset_version: str
    is_proposal: str
    theme: str
    objective: Optional[str] = None
    proposed_action: Optional[str] = None
    target_population: Optional[str] = None
    quantitative_target: Optional[str] = None
    deadline: Optional[str] = None

def _read_dataset(path: Path) -> pl.DataFrame:
    if not path.exists():
        raise FileNotFoundError(f"Dataset não encontrado: {path}")

    suffix = path.suffix.lower()
    if suffix == ".json":
        return pl.read_json(path)
    if suffix == ".parquet":
        return pl.read_parquet(path)
    raise ValueError("Formato não suportado. Use um arquivo .json ou .parquet.")

def load_silver_dataset(dataset_path: str | Path) -> pl.DataFrame:
    """Carrega JSON ou Parquet e retorna apenas as colunas do contrato Silver."""
    df = _read_dataset(Path(dataset_path))
    missing_columns = [
        column for column in SILVER_DATASET_COLUMNS if column not in df.columns
    ]
    if missing_columns:
        raise ValueError(
            "Dataset sem colunas Silver obrigatórias: "
            + ", ".join(missing_columns)
        )

    return df.select(SILVER_DATASET_COLUMNS)


def json_to_parquet(json_path: str | Path, parquet_path: str | Path) -> Path:
    """Materializa um dataset JSON validado no formato Silver Parquet."""
    df = load_silver_dataset(json_path)
    output_path = Path(parquet_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    df.write_parquet(output_path)
    return output_path


def build_output_row(
    chunk: dict[str, Any], proposal: ProposalSchema
) -> OutputSchema:
    """Combina os dados Silver do chunk com a resposta validada pelo LLM."""
    silver_chunk = {column: chunk[column] for column in SILVER_DATASET_COLUMNS}
    return OutputSchema(**silver_chunk, **proposal.model_dump())
