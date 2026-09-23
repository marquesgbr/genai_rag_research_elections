### Generate sample data for the database in a "toydataset.json" file. 
# This dataset will be used to populate the database with sample data for 
# testing purposes.
import json

textos = [
    # Similar meanings (Medical related; used for testing the embedding similarity)
    "Expandir serviços de telemedicina para municípios do interior",
    "Ampliar o atendimento de saúde por meio de consultas remotas",
    "Criar pólos regionais de atendimento médico digital",
    
    # High similairty but different goals (Economic related) 
    "Reduzir os impostos para pequenas empresas",
    "Manter a carga tributária atual das pequenas empresas",
    
    # Not related (Education, Security, Infrastructure, etc.)
    "Aumentar o efetivo policial nas áreas de fronteira",
    "Construir 100 novas creches em período integral",
    "Revitalizar a malha ferroviária para escoamento de safra",
    "Implementar sistema de reconhecimento facial na segurança pública",
    "Dobrar o piso salarial dos professores da rede básica",
    "Privatizar rodovias estaduais que apresentam déficit de manutenção",
    "Fomentar a agricultura familiar com linhas de crédito subsidiadas",
    "Zerar o desmatamento ilegal através de monitoramento via satélite",
    "Incentivar a instalação de painéis solares em residências de baixa renda",
    "Criar um programa de bolsa permanência para estudantes universitários"
]

dataset = []

for i, texto in enumerate(textos, start=1):
    if i <= 3:
        section = "Saúde"
    elif i <= 5:
        section = "Economia"
    else:
        section = "Geral"

    chunk = {
        "chunk_id": f"PRES_001_p10_c{i:03d}",
        "document_id": "PRES_001",
        "page": 10 + (i % 5), 
        "section": section,
        "text": texto,
        "candidate": "Fictício Silva",
        "party": "PEX",
        "office": "Presidente",
        "state": "BR"
    }
    dataset.append(chunk)

# Export to toydataset.json
with open("toydataset.json", "w", encoding="utf-8") as f:
    json.dump(dataset, f, ensure_ascii=False, indent=4)

print("Sample dataset 'toydataset.json' generated successfully.")