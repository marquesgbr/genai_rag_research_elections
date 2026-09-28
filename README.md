# GenAI RAG Research Elections

Repositório experimental para comparar dois pipelines aplicados a propostas eleitorais:

1. um pipeline de extração estruturada, que usa um Large Language Model (LLM) para transformar trechos em registros estruturados e salvar o resultado em Parquet;
2. um pipeline de retrieval vetorial, que gera embeddings, armazena os vetores em PostgreSQL com pgvector e recupera os trechos semanticamente mais próximos de uma consulta.

Os dois pipelines partem do mesmo dataset de propostas e produzem saídas que poderão ser comparadas em etapas posteriores de avaliação. Este repositório concentra a preparação dos dados, a execução dos pipelines e os experimentos iniciais; a definição das métricas e a comparação formal dos resultados serão adicionadas posteriormente.

O projeto não é uma aplicação web. Os pipelines são executados pela linha de comando e exibem seus resultados no terminal ou gravam arquivos para uso nos experimentos.

## Como o projeto funciona

O fluxo comum começa com um dataset de chunks textuais em formato Silver. O exemplo incluído está em [data/toydataset.json](data/toydataset.json), e [db_seed.py](db_seed.py) pode recriá-lo.

A partir desse dataset, os pipelines seguem caminhos independentes:

### Pipeline de extração estruturada

O módulo [pipelines/structured_extraction](pipelines/structured_extraction) envia cada chunk ao Gemini por meio do Agno. A resposta é validada com os schemas definidos em [schema.py](schema.py), combinada com os metadados Silver e persistida em um arquivo Parquet.

Saída principal:

- `data/StructuredProposals.parquet`, contendo os metadados originais e campos como `is_proposal`, `theme`, `objective` e `proposed_action`.

### Pipeline de retrieval vetorial

O módulo [pipelines/vector_retrieval](pipelines/vector_retrieval) inicializa a extensão pgvector, cria a tabela `chunks`, gera embeddings com `sentence-transformers`, grava os chunks no PostgreSQL e executa uma consulta por similaridade vetorial.

Saída principal:

- resultados de retrieval exibidos no terminal, com `chunk_id`, score de similaridade, página, seção e texto recuperado.

O mesmo modelo de embeddings deve ser usado na ingestão e na consulta. Os dois pipelines são independentes: executar um não exige executar o outro, embora ambos possam usar o mesmo dataset de entrada.

## Requisitos

- Python 3.10 ou superior;
- Docker com Docker Compose, para executar o PostgreSQL com pgvector;
- conexão com a internet na primeira execução, caso o modelo de embeddings ainda não esteja disponível localmente;
- aproximadamente 480 MB livres se o modelo for salvo em `models/`.

O PostgreSQL não precisa ser instalado diretamente na máquina. O serviço usado pelo projeto é definido em [docker-compose.yml](docker-compose.yml).

## Bibliotecas Python

As dependências estão em [requirements.txt](requirements.txt):

- `psycopg`: conexão com PostgreSQL;
- `sentence-transformers`: geração de embeddings para o pipeline vetorial;
- `python-dotenv`: carregamento das variáveis do arquivo `.env`;
- `agno`: orquestração do agente usado na extração estruturada;
- `pydantic`: validação dos schemas de entrada e saída;
- `google-genai`: SDK atual do Gemini, usado pelo adaptador do Agno;
- `polars`: leitura, transformação e gravação dos arquivos Parquet;

## Configuração do ambiente

Crie e ative um ambiente virtual ou use um já existente:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

No Linux ou macOS:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Crie o arquivo local de configuração a partir do exemplo:

```powershell
Copy-Item .env.example .env
```

No Linux ou macOS:

```bash
cp .env.example .env
```

Para o pipeline vetorial, revise as configurações do banco:

```env
DB_HOST=localhost
DB_PORT=5432
DB_NAME=rag_vector_db
DB_USER=postgres
DB_PASSWORD=uma_senha_local
```

Para o modelo de embeddings, os padrões são:

```env
EMBEDDING_MODEL_NAME=paraphrase-multilingual-MiniLM-L12-v2
EMBEDDING_MODEL_LOCAL_PATH=models/multilingual_miniLM_L12_v2
EMBEDDING_VECTOR_DIM=384
```

Para o pipeline de extração estruturada, defina também:

```env
GEMINI_API_KEY=sua_chave_local
GEMINI_MODEL_ID=gemini-3.8-flash
```

O `.env` é local e não deve ser versionado.

## Execução

Os comandos abaixo devem ser executados a partir da raiz do repositório.

### Dataset de exemplo

Para recriar o dataset de exemplo:

```powershell
python db_seed.py
```

O arquivo será salvo em `data/toydataset.json`.

### Pipeline de extração estruturada

Com `GEMINI_API_KEY` configurada:

```powershell
python -m pipelines.structured_extraction `
	--input data/toydataset.json `
	--output data/StructuredProposals.parquet
```

Para executar um teste com apenas um chunk:

```powershell
python -m pipelines.structured_extraction `
	--input data/toydataset.json `
	--output data/StructuredProposals.parquet `
	--limit 1
```

O pipeline atualiza registros existentes por `chunk_id`, evitando duplicações quando é executado novamente.

### Pipeline de retrieval vetorial

Inicie o PostgreSQL:

```powershell
docker compose up -d
```

Execute o pipeline completo:

```powershell
python -m pipelines.vector_retrieval `
	--input data/toydataset.json `
	--query "melhorar o atendimento médico remoto" `
	--top-k 3
```

Esse comando cria a estrutura do banco, gera os embeddings, faz o upsert dos chunks e consulta os resultados mais similares.

Para consultar uma tabela já populada sem repetir a inicialização ou a ingestão:

```powershell
python -m pipelines.vector_retrieval `
	--skip-setup `
	--skip-ingest `
	--query "serviços médicos digitais" `
	--top-k 3
```

O modelo pode ser baixado e salvo localmente antes da execução:

```powershell
python download_model.py
```

Como alternativa, `EMBEDDING_MODEL_LOCAL_PATH` pode apontar diretamente para um identificador disponível no Hugging Face. O modelo usado na ingestão precisa ser o mesmo usado nas consultas.

## Verificações manuais

Para validar a extração de um único chunk usando a API do Gemini:

```powershell
python tests/smoke_test_structured_extraction.py --input data/toydataset.json --row 0
```

Para verificar uma chamada simples ao Gemini por meio do Agno:

```powershell
python tests/test_api.py
```

O pipeline vetorial pode ser verificado de ponta a ponta com o comando descrito na seção anterior, desde que o PostgreSQL esteja em execução e o modelo de embeddings esteja disponível.

## Estrutura principal

| Caminho | Responsabilidade |
| --- | --- |
| `pipelines/structured_extraction/` | Entry point do pipeline LLM que gera o Parquet estruturado |
| `pipelines/vector_retrieval/` | Entry point do pipeline de embeddings e retrieval pgvector |
| `agent_structured_extraction.py` | Lógica de extração e upsert do Parquet |
| `schema.py` | Schemas Pydantic e transformação do dataset Silver |
| `config_env.py` | Configuração carregada do `.env` |
| `db_setup.py` | Criação da extensão e da tabela pgvector |
| `ingest.py` | Geração e persistência dos embeddings |
| `vec_search.py` | Consulta por similaridade vetorial |
| `data/` | Dataset de exemplo e saídas Parquet |
| `schemas/` | Imagens e materiais de referência dos schemas |

## Limites atuais

- os pipelines ainda são executados separadamente pela linha de comando;
- a comparação formal entre as saídas será implementada em uma etapa posterior;
- o banco local não possui volume persistente configurado no Docker Compose;
- `models/`, `.env` e os Parquets gerados pelos pipelines não devem ser commitados; os arquivos de exemplo já versionados em `data/` são a exceção.
