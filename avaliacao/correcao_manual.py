"""
Correção MANUAL das respostas do benchmark.

Cada resposta gerada foi lida por um humano e recebeu:
  correto : True (resposta certa) ou False (errada/não respondeu)
  nota    : justificativa curta quando a nota exige explicação

Critério: a resposta é "correta" quando (a) está factualmente certa,
(b) realmente responde à pergunta e (c) não inventa informação.

Fica separado do runner de propósito: rodar o benchmark de novo regenera
o resultados.json (respostas), mas ESTAS notas humanas permanecem aqui.
"""

CORRECAO = {
    # --- Corpus (validação) ---
    "C1": {"correto": True,  "nota": ""},
    "C2": {"correto": True,  "nota": ""},
    "C3": {"correto": True,  "nota": ""},
    "C4": {"correto": True,  "nota": ""},
    "C5": {"correto": True,  "nota": ""},
    # --- Fallback (validação) ---
    "F1": {"correto": True,  "nota": ""},
    "F2": {"correto": True,  "nota": ""},
    "F3": {"correto": True,  "nota": ""},
    "F4": {"correto": False, "nota": "Roteou p/ web corretamente, mas a busca não trouxe passos de configuração; agente respondeu 'não encontrei'."},
    "F5": {"correto": False, "nota": "Roteou p/ web corretamente, mas a busca não trouxe o preço; agente respondeu 'não encontrei'."},

    # --- Corpus (teste) ---
    "C6": {"correto": True,  "nota": ""},
    "C7": {"correto": True,  "nota": ""},
    "C8": {"correto": True,  "nota": ""},
    "C9": {"correto": False, "nota": "Falha de recuperação: o trecho de classificação de risco do ElderSync está no corpus, mas ficou fora do top-8; agente respondeu 'não encontrei' (não alucinou)."},
    "C10": {"correto": True, "nota": ""},
    # --- Fallback (teste) ---
    "F6": {"correto": True,  "nota": ""},
    "F7": {"correto": True,  "nota": ""},
    "F8": {"correto": True,  "nota": ""},
    "F9": {"correto": True,  "nota": ""},
    "F10": {"correto": True, "nota": ""},
}
