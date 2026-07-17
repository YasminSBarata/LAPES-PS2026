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

8 documentos (~mais de 50 mil tokens) num **único domínio clínico**: avaliação da
mobilidade e do risco de quedas em idosos. O corpus foi montado para conectar a
**literatura de referência** (como os testes funcionais funcionam e o que dizem as
evidências) ao **produto real** que motiva o projeto — o **ElderSync**, um sistema
wearable de avaliação de mobilidade desenvolvido em pesquisa CNPq/CESUPA.

### Literatura clínica de referência (`corpus/artigos/`)

- **Nakano (2007) — Validação brasileira da SPPB.** Dissertação que adaptou culturalmente
  e validou para o português a *Short Physical Performance Battery*, avaliando suas
  propriedades psicométricas na população idosa brasileira. É a principal fonte sobre a
  SPPB (pontuação, graduação, subtestes).
- **Guralnik et al. — SPPB original.** Artigo que introduz a bateria (equilíbrio,
  velocidade de marcha, levantar-se da cadeira) como preditora de incapacidade. Era um
  PDF-imagem; foi recuperado por **OCR** (`ingestao/ocr_um_pdf.py`).
- **Podsiadlo & Richardson (1991), JAGS — Teste Timed Up and Go (TUG).** Artigo seminal do
  TUG: mede o tempo para levantar de uma cadeira, andar ~3 m, voltar e sentar, avaliando
  mobilidade funcional e risco de quedas.
- **WHO Global Report on Falls Prevention in Older Age.** Relatório da OMS sobre fatores de
  risco de quedas (biológicos, comportamentais, **ambientais** e socioeconômicos) e
  estratégias de prevenção.
- **Curone et al. (IEEE) — Algoritmo de detecção de postura/atividade.** Algoritmo em tempo
  real, auto-calibrante e independente da orientação do sensor, que classifica postura e
  atividade a partir de um acelerômetro tri-axial vestível (96,2% de acurácia).
  Fundamenta a parte de sensores do ElderSync.

### Documentos internos do ElderSync (`corpus/eldersync/`)

- **Reestruturação do ElderSync v2.** Documento do projeto (CNPq/CESUPA, 2026) que
  redireciona o sistema de "monitoramento contínuo" (v1) para um **registro clínico digital**
  dos testes padronizados (SPPB + TUG). Traz os protocolos adotados, a pontuação da SPPB e
  o papel do dispositivo (ESP32 + MPU6050) na medição de oscilação corporal e marcha.
- **Guia do fisioterapeuta.** Manual prático de uso do sensor durante os testes: estados do
  LED, calibração, fluxo de cada teste e as métricas coletadas (oscilação ântero-posterior
  e médio-lateral, RMS, ângulo do tronco no sentar/levantar, etc.).
- **Integração IoT (ESP32 + MPU6050).** Documento técnico da coleta de dados: as 10 métricas
  do sensor (contagem de passos, cadência, velocidade de marcha, estabilidade postural,
  detecção de quedas, TUG estimado…), a arquitetura (sensor → ESP32 → Supabase → dashboard)
  e os limiares de detecção de eventos.

**Justificativa e coesão:** o corpus é internamente conectado — o próprio documento do
ElderSync v2 cita Nakano (2007) e Podsiadlo & Richardson (1991) como as bases dos protocolos
que implementa. A predominância de material de referência e interno é intencional: perguntas
sobre diretrizes recentes ou temas fora do domínio **caem fora do corpus por design**,
exercitando o fallback web.

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

### Custo (API paga)

O benchmark completo usa o `gpt-4o-mini` (~40 chamadas). Consumo **medido** (não estimado):
**29.224 tokens = US$ 0,0058** (menos de um centavo) para rodar as 20 perguntas.
Detalhes e reprodução em [`avaliacao/custo.md`](avaliacao/custo.md) / `avaliacao/custo.py`.
Embeddings (local) e busca web (Tavily, plano gratuito) não têm custo.

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
