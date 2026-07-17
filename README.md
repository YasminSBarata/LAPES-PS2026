# ElderSync — Sistema Agêntico RAG com Fallback Web

Assistente que responde perguntas sobre **mobilidade, testes funcionais (SPPB, TUG) e
risco de quedas em idosos**, a partir de um corpus clínico próprio. Quando a pergunta
sai do domínio do corpus, o sistema **busca automaticamente na web**. Cada execução gera
um **trace JSON** auditável.

Desafio LAPES 2026 — Trilha de Dados.
Autora: Yasmin dos Santos Barata · yasmin24300096@aluno.cesupa.br

---

## Visão geral

O sistema é composto por **quatro agentes** orquestrados com **LangGraph**:

| Agente | Papel |
|--------|-------|
| **Reformulador** | reescreve a pergunta em termos clínicos, para melhorar a busca |
| **Recuperador** | busca no índice vetorial e decide a rota (corpus ou web) pela distância |
| **Respondedor** | gera a resposta a partir dos trechos do corpus, citando a fonte |
| **Busca Web** | fallback: busca na web (Tavily) e responde citando os links |

### Fluxo

```
pergunta
   |
[Reformulador]
   |
[Recuperador] --- distância <= 12.5 ---> [Respondedor]  (corpus)
   |                                          |
   '------- distância > 12.5 -------> [Busca Web]  (fallback)
                                              |
                          resposta final + trace JSON (traces/)
```

---

## Estrutura do projeto

```
ingestao/       leitura do corpus, chunking e geração do índice FAISS
agentes/        os quatro agentes (um arquivo cada), executáveis isoladamente
orquestracao/   orquestrador LangGraph que amarra os agentes + gera o trace
interface/      interface web (Streamlit)
avaliacao/      benchmark: perguntas, runner, correção manual e relatório
corpus/         os documentos-fonte (artigos + documentos ElderSync)
traces/         traces JSON de cada execução (auditoria)
indice/         índice FAISS gerado (não versionado — recriar com a ingestão)
```

---

## Corpus

8 documentos, todos no domínio de **mobilidade e risco de quedas em idosos**:

**Artigos e literatura clínica** (`corpus/artigos/`)
- Dissertação de Nakano — validação brasileira da SPPB
- Podsiadlo & Richardson (1991) — teste Timed Up and Go (TUG)
- Guralnik et al. — Short Physical Performance Battery (recuperado por OCR)
- WHO Global Report on Falls Prevention in Older Age
- A Real-Time and Self-Calibrating Algorithm (sensores/marcha)

**Documentos internos ElderSync** (`corpus/eldersync/`)
- Reestruturação do sistema ElderSync v2
- Guia do fisioterapeuta
- Integração IoT (sensores ESP32 + MPU6050)

**Justificativa:** o corpus é coeso (um único domínio clínico) e conecta a literatura de
referência ao produto real (ElderSync). A predominância de material mais antigo/interno é
intencional: perguntas sobre diretrizes recentes ou temas fora do domínio **caem fora do
corpus por design**, exercitando o fallback web.

---

## Escolhas técnicas e trade-offs

- **Embeddings:** `paraphrase-multilingual-MiniLM-L12-v2` (local, gratuito). Multilíngue
  porque o corpus é bilíngue (artigos em inglês + documentos e perguntas em português).
  *Trade-off:* modelo pequeno (384 dimensões) — rápido e reprodutível, mas com recall
  limitado em fatos muito específicos (ver Limitações).
- **Chunking em tokens** (120 tokens, overlap 24): a janela do modelo é de 128 tokens;
  medir o chunk em tokens (e não em caracteres) garante que nenhum trecho seja truncado
  na hora de gerar o embedding.
- **Vector store: FAISS.** O corpus é estático (ingere uma vez, consulta muitas), então
  FAISS é mais simples, rápido e reprodutível que um banco vetorial com servidor.
- **Limiar do fallback = 12.5** (distância L2), calibrado empiricamente
  (`agentes/calibrar_limiar.py`): perguntas de dentro do corpus deram distância <= 11.46 e
  as de fora >= 13.75; 12.5 é o meio do intervalo.
- **Busca em união:** o Recuperador busca com a pergunta original **e** a reformulada,
  unindo os resultados. Motivo: medimos que reformular nem sempre ajuda — às vezes a
  original recupera o trecho que a reformulada perde.
- **LLM:** OpenAI `gpt-4o-mini` (`temperature=0`). A troca por um modelo local (Ollama) é
  de poucas linhas via LangChain.
- **Busca web:** Tavily (buscador voltado para IA, devolve texto já limpo).

---

## Como reproduzir do zero

### 1. Pré-requisitos
- Python 3.12
- Chave da OpenAI (obrigatória) e chave do Tavily (gratuita, para o fallback web)

### 2. Ambiente e dependências
```bash
python3 -m venv .venv
source .venv/bin/activate

# torch na versão CPU (evita o download gigante da GPU)
pip install torch --index-url https://download.pytorch.org/whl/cpu

pip install -r requirements.txt
```

### 3. Chaves de API
```bash
cp .env.example .env
# edite o .env e preencha:
#   OPENAI_API_KEY=sk-...
#   TAVILY_API_KEY=tvly-...
```

### 4. Gerar o índice (ingestão)
Lê o corpus, faz o chunking e cria o índice FAISS em `indice/`:
```bash
./.venv/bin/python ingestao/run.py
```

### 5. Rodar o sistema

**Interface web (recomendado):**
```bash
./.venv/bin/streamlit run interface/app.py
```

**Linha de comando:**
```bash
./.venv/bin/python orquestracao/orquestrador.py "qual a pontuação máxima da SPPB?"
```

---

## Avaliação (benchmark)

20 perguntas (10 respondíveis pelo corpus + 10 de fallback), divididas em **validação** e
**teste**. Rodar:
```bash
./.venv/bin/python avaliacao/rodar_benchmark.py    # roda tudo e gera os traces
./.venv/bin/python avaliacao/gerar_relatorio.py    # monta o relatório
```

**Métricas:** (1) acurácia de roteamento (automática) e (2) correção da resposta (manual).
**Resultado no conjunto de teste: roteamento 100%, correção 90%.**
Relatório completo em [`avaliacao/resultados.md`](avaliacao/resultados.md).

---

## Observabilidade

Cada execução gera um trace em `traces/<timestamp>.json` contendo: pergunta original e
reformulada, qual agente processou cada etapa, trechos e fontes recuperados, se o fallback
foi acionado e por quê, e a resposta final.

---

## Limitações e melhorias futuras

- **Recall em fatos específicos:** o modelo de embedding pequeno ocasionalmente não
  recupera o trecho exato (1 falha no benchmark). O sistema **admite não saber** em vez de
  inventar. Melhoria: reranker (cross-encoder) ou modelo de embedding maior.
- **Qualidade da busca web** depende dos resultados do Tavily.
- **Migração para LLM local** (Ollama) e integração com dados clínicos reais (Supabase)
  são próximos passos previstos.
