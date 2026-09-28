"""Teste mínimo de geração de texto com Gemini por meio do Agno.

Uso:
    python testeapi.py
    python testeapi.py "Qual é a importância da educação?"
"""

import json
import os
import sys

from agno.agent import Agent
from agno.models.google import Gemini

from config_env import GEMINI_API_KEY, GEMINI_MODEL_ID


DEFAULT_PROMPT = "Responda em uma frase: o Gemini está funcionando?"


def main() -> int:
    """Envia um prompt ao Gemini e confirma que houve resposta."""
    if not GEMINI_API_KEY:
        print(
            "Erro: GEMINI_API_KEY não foi definida. "
            "Configure essa variável no arquivo .env."
        )
        return 1

    if not GEMINI_MODEL_ID:
        print(
            "Erro: GEMINI_MODEL_ID não foi definida. "
            "Configure essa variável no arquivo .env."
        )
        return 1

    prompt = " ".join(sys.argv[1:]).strip() or DEFAULT_PROMPT
    agente = Agent(model=Gemini(id=GEMINI_MODEL_ID, api_key=GEMINI_API_KEY))

    print(f"Modelo: {GEMINI_MODEL_ID}")
    print(f"Prompt: {prompt}")

    try:
        resposta = agente.run(prompt)
    except Exception as error:
        print(f"Erro ao consultar o Gemini: {error}")
        return 1

    conteudo = resposta.content
    if not isinstance(conteudo, str) or not conteudo.strip():
        print("Erro: o Gemini não retornou conteúdo de texto.")
        return 1
    try:
        erro_api = json.loads(conteudo)
    except json.JSONDecodeError:
        erro_api = None
    if isinstance(erro_api, dict) and "error" in erro_api:
        print(f"Erro retornado pelo Gemini: {conteudo.strip()}")
        return 1

    print("\nResposta recebida:")
    print(conteudo.strip())
    print("\nTeste concluído com sucesso.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
