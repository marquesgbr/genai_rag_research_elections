# GenAI RAG Research Elections

Projeto experimental de busca semântica aplicado a propostas eleitorais. A ideia é transformar os textos das propostas em vetores (embeddings), armazená-los no PostgreSQL com a extensão pgvector e recuperar os trechos mais parecidos com uma consulta em texto livre.

O projeto usa um dataset pequeno, criado para facilitar os testes e a compreensão do pipeline. Ele não é uma aplicação web: o resultado é exibido diretamente no terminal.

## Como o projeto funciona

O fluxo principal é:

1. subir um banco PostgreSQL com suporte a vetores;
2. criar a extensão `vector` e a tabela `chunks`;
3. gerar um dataset de exemplo;
4. carregar o modelo de embeddings;
5. transformar os textos do dataset em vetores e salvá-los no banco;
6. fazer consultas semânticas e mostrar os trechos mais similares.

## Ferramentas necessárias

- Python 3.10 ou superior;
- Docker, com Docker Compose;
- Git, para clonar o repositório;
- conexão com a internet na primeira execução do modelo do Hugging Face;
- aproximadamente 480 MB livres caso o modelo seja salvo localmente, além do espaço usado pelo ambiente Python.

O Docker é usado para executar o PostgreSQL com a extensão pgvector. Não é necessário instalar o PostgreSQL diretamente na máquina.

## Bibliotecas Python

As dependências do projeto estão em [requirements.txt](requirements.txt):

- `psycopg`: conexão com o PostgreSQL;
- `sentence-transformers`: carregamento do modelo e geração dos embeddings;
- `python-dotenv`: leitura das variáveis definidas no arquivo `.env`.

## Configuração do ambiente

Crie um ambiente virtual e instale as dependências:

```bash
python -m venv .venv
```

No Windows:

```powershell
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

No Linux ou macOS:

```bash
source .venv/bin/activate
pip install -r requirements.txt
```

Crie o arquivo `.env` a partir do exemplo:

```powershell
Copy-Item .env.example .env
```

No Linux ou macOS:

```bash
cp .env.example .env
```

Revise principalmente estas variáveis:

```env
DB_HOST=localhost
DB_PORT=5432
DB_NAME=rag_vector_db
DB_USER=postgres
DB_PASSWORD=led_senha
```

O arquivo `.env` é local e não deve ser versionado. Use uma senha própria em vez do valor de exemplo.

## Executando o projeto

Os comandos abaixo devem ser executados a partir da raiz do repositório.

### 1. Inicie o banco de dados

```bash
docker compose up -d
```

Esse comando inicia o container `pgvector-db` usando a imagem `pgvector/pgvector:pg16`.

Para verificar os containers em execução:

```bash
docker compose ps
```

### 2. Gere o dataset de exemplo

O script [db_seed.py](db_seed.py) cria o arquivo `toydataset.json` com propostas fictícias:

```bash
python db_seed.py
```

O arquivo já pode existir no repositório, mas executar o script novamente permite recriá-lo a partir do código.

### 3. Crie a extensão e a tabela

Execute [db_setup.py](db_setup.py):

```bash
python db_setup.py
```

Esse script:

- conecta ao banco usando as variáveis do `.env`;
- habilita a extensão `vector`;
- cria a tabela `chunks`, caso ela ainda não exista;
- configura a coluna de embedding com a dimensão definida em `EMBEDDING_VECTOR_DIM`.

### 4. Escolha e carregue o modelo

Por padrão, a busca usa o caminho local definido em `EMBEDDING_MODEL_LOCAL_PATH`:

```env
EMBEDDING_MODEL_LOCAL_PATH=models/multilingual_miniLM_L12_v2
```

Para baixar o modelo e salvá-lo nessa pasta, execute:

```bash
python download_model.py
```

O download utiliza o nome definido em `EMBEDDING_MODEL_NAME` e salva os arquivos no caminho de `EMBEDDING_MODEL_LOCAL_PATH`. A pasta `models/` está no `.gitignore`, portanto o modelo não é enviado para o Git.

### 5. Insira os embeddings no banco

Com o banco inicializado e o modelo disponível, execute:

```bash
python ingest.py
```

O script lê o `toydataset.json`, gera um embedding para cada proposta e insere ou atualiza os registros na tabela `chunks`.

### 6. Faça buscas semânticas

Execute:

```bash
python vec_search.py
```

O script faz algumas consultas de exemplo e mostra no terminal o `chunk_id`, o score de similaridade, a página, a seção e o texto encontrado.

Para testar outras consultas, altere os textos da função `main` em [vec_search.py](vec_search.py).

## Usando o modelo diretamente do Hugging Face

Não é obrigatório salvar o modelo localmente. O `SentenceTransformer` também aceita o identificador do modelo no Hugging Face:

```env
EMBEDDING_MODEL_NAME=paraphrase-multilingual-MiniLM-L12-v2
```

Se você não quiser manter a pasta local de aproximadamente 480 MB, altere o valor usado pela busca para o identificador do Hugging Face:

```env
EMBEDDING_MODEL_LOCAL_PATH=paraphrase-multilingual-MiniLM-L12-v2
```

Ou altere manualmente o argumento da instância do modelo em [vec_search.py](vec_search.py) e [ingest.py](ingest.py)

```python
model=SentenceTransformer(EMBEDDING_MODEL_NAME)
```

E

```python
model=instantiate_model(EMBEDDING_MODEL_NAME)
```

Assim, quando `vec_search.py` executar `SentenceTransformer(EMBEDDING_MODEL_LOCAL_PATH)`, o modelo será baixado pelo cache do Hugging Face na primeira utilização, em vez de ser lido da pasta `models/`.

 Se você escolher outro modelo, mantenha o mesmo modelo na ingestão e na busca. Caso contrário, os vetores podem ficar incompatíveis ou representar espaços semânticos diferentes.

## Arquivos principais

| Arquivo | Função |
| --- | --- |
| `config_env.py` | Carrega as configurações do `.env` |
| `docker-compose.yml` | Inicia o PostgreSQL com pgvector |
| `db_seed.py` | Gera o dataset fictício |
| `db_setup.py` | Cria a extensão e a tabela do banco |
| `download_model.py` | Baixa e salva o modelo localmente |
| `ingest.py` | Gera e persiste os embeddings |
| `vec_search.py` | Executa a busca por similaridade |
| `toydataset.json` | Dataset usado no exemplo |

## Observações

- O banco precisa estar em execução antes de rodar `db_setup.py`, `ingest.py` ou `vec_search.py`.
- A dimensão do modelo precisa ser compatível com `EMBEDDING_VECTOR_DIM`. O modelo usado no exemplo gera vetores de 384 dimensões.
- O nome ou caminho do modelo usado na ingestão deve ser o mesmo usado na busca.
- O arquivo `.env`, a pasta `models/` e outros arquivos locais não devem ser commitados.
- O `docker compose down` para e remove o container do banco, mas os dados podem ser perdidos dependendo da configuração usada. Posteriormente, adicionar um volume persistente.