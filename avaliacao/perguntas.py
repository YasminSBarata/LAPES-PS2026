"""
Dataset de avaliação — 20 perguntas para o benchmark.

Estrutura de cada item:
  id       : identificador curto (C=corpus, F=fallback)
  conjunto : "validacao" (usado no desenvolvimento) ou "teste" (resultado oficial)
  tipo     : "corpus" (deve ser respondida pelo RAG) ou "web" (deve ir pro fallback)
  pergunta : o texto perguntado ao sistema
  esperado : resumo da resposta correta (referência para a correção MANUAL)

Divisão: 10 em validação (5 corpus + 5 fallback) e 10 em teste (5 corpus + 5 fallback).
Pelo menos 10 perguntas acionam o fallback por design (todas as F*).
"""

PERGUNTAS = [
    # ---------------- VALIDAÇÃO ----------------
    {"id": "C1", "conjunto": "validacao", "tipo": "corpus",
     "pergunta": "Qual a pontuação máxima da SPPB e o que ela indica?",
     "esperado": "12 pontos; 10 a 12 indica bom desempenho físico."},
    {"id": "C2", "conjunto": "validacao", "tipo": "corpus",
     "pergunta": "Quais são os três componentes (testes) que compõem a SPPB?",
     "esperado": "Equilíbrio, velocidade de marcha e levantar-se da cadeira."},
    {"id": "C3", "conjunto": "validacao", "tipo": "corpus",
     "pergunta": "Por quanto tempo o idoso deve manter cada posição no teste de equilíbrio da SPPB?",
     "esperado": "10 segundos em cada posição (side-by-side, semi-tandem, tandem)."},
    {"id": "C4", "conjunto": "validacao", "tipo": "corpus",
     "pergunta": "Quais fatores aumentam o risco de quedas em idosos?",
     "esperado": "Redução de força/massa muscular, marcha lenta, comorbidades, fatores ambientais."},
    {"id": "C5", "conjunto": "validacao", "tipo": "corpus",
     "pergunta": "O que é o teste Timed Up and Go (TUG)?",
     "esperado": "Mede o tempo para levantar da cadeira, andar 3 metros, voltar e sentar; avalia mobilidade e risco de quedas."},

    {"id": "F1", "conjunto": "validacao", "tipo": "web",
     "pergunta": "Qual a bula e posologia do paracetamol?",
     "esperado": "(fora do corpus) — resposta vinda da web."},
    {"id": "F2", "conjunto": "validacao", "tipo": "web",
     "pergunta": "Quem ganhou a Copa do Mundo de 2022?",
     "esperado": "(fora do corpus) — Argentina."},
    {"id": "F3", "conjunto": "validacao", "tipo": "web",
     "pergunta": "Qual a capital da Austrália?",
     "esperado": "(fora do corpus) — Camberra."},
    {"id": "F4", "conjunto": "validacao", "tipo": "web",
     "pergunta": "Como configurar um servidor nginx?",
     "esperado": "(fora do corpus) — resposta vinda da web."},
    {"id": "F5", "conjunto": "validacao", "tipo": "web",
     "pergunta": "Qual o preço do iPhone lançado em 2025?",
     "esperado": "(fora do corpus) — resposta vinda da web."},

    # ------------------- TESTE -------------------
    {"id": "C6", "conjunto": "teste", "tipo": "corpus",
     "pergunta": "Quais sensores o ElderSync usa na integração IoT?",
     "esperado": "ESP32 e MPU6050."},
    {"id": "C7", "conjunto": "teste", "tipo": "corpus",
     "pergunta": "O que a dissertação da Nakano adaptou/validou para o português?",
     "esperado": "A versão brasileira da SPPB."},
    {"id": "C8", "conjunto": "teste", "tipo": "corpus",
     "pergunta": "Segundo a OMS, como o ambiente físico influencia o risco de quedas?",
     "esperado": "A estrutura do ambiente físico impacta o risco de quedas."},
    {"id": "C9", "conjunto": "teste", "tipo": "corpus",
     "pergunta": "Como o ElderSync classifica o risco (faixas)?",
     "esperado": "Faixas por tempo/cor (ex.: vermelho para dependência funcional, >30 segundos)."},
    {"id": "C10", "conjunto": "teste", "tipo": "corpus",
     "pergunta": "Como é feito o procedimento do teste TUG?",
     "esperado": "Sentado, levanta, anda 3 metros, retorna e senta; cronometrado."},

    {"id": "F6", "conjunto": "teste", "tipo": "web",
     "pergunta": "Me dê uma receita de bolo de cenoura.",
     "esperado": "(fora do corpus) — resposta vinda da web."},
    {"id": "F7", "conjunto": "teste", "tipo": "web",
     "pergunta": "Qual a cotação do dólar hoje?",
     "esperado": "(fora do corpus) — resposta vinda da web."},
    {"id": "F8", "conjunto": "teste", "tipo": "web",
     "pergunta": "Quais os efeitos colaterais da vacina da gripe?",
     "esperado": "(fora do corpus) — resposta vinda da web."},
    {"id": "F9", "conjunto": "teste", "tipo": "web",
     "pergunta": "Quem foi Santos Dumont?",
     "esperado": "(fora do corpus) — aviador/inventor brasileiro."},
    {"id": "F10", "conjunto": "teste", "tipo": "web",
     "pergunta": "Qual a fórmula química da água?",
     "esperado": "(fora do corpus) — H2O."},
]
