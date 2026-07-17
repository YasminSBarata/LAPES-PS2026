# Benchmark de avaliação — Sistema Agêntico RAG (ElderSync)

## Metodologia

Foram avaliadas **20 perguntas**, divididas em **validação** (10, usadas no desenvolvimento) e **teste** (10, reservadas para o resultado oficial). Metade de cada conjunto é respondível pelo corpus e metade é de **fallback** (fora do domínio, deve ir para a web) — 10 perguntas de fallback no total.

Duas métricas complementares:

1. **Acurácia de roteamento** (automática): a pergunta foi para a fonte certa (corpus→RAG, fallback→web)? *Escolhida porque, num assistente clínico, o erro mais grave é buscar no lugar errado — responder de memória quando deveria buscar, ou dizer "não sei" quando a resposta estava no corpus.*
2. **Correção da resposta** (manual): a resposta final está factualmente correta, responde à pergunta e não inventa? *Avaliada por leitura humana de cada resposta — transparente e sem depender de outro modelo como juiz.*

## Resultados — conjunto de TESTE (oficial)

| ID | Pergunta | Fonte recuperada | Rota | Roteamento | Correção | Resposta (resumo) |
|----|----------|------------------|------|:----------:|:--------:|-------------------|
| C6 | Quais sensores o ElderSync usa na integração IoT? | A_Real_Time_and_Self_Calibrating_Algorit.pdf, ElderSync_v2_Reestruturacao.pdf, GUIA_FISIOTERAPEUTA.md, IOT_INTEGRATION.md | RAG | ✅ | ✅ | O ElderSync utiliza a integração de sensores ESP32 com MPU6050 para o monitoramento de pacientes idosos. O MPU6050 é um sensor que coleta dados de movimento, en… |
| C7 | O que a dissertação da Nakano adaptou/validou para o português? | Nakano_MarciaMariko_M.pdf | RAG | ✅ | ✅ | A dissertação de Márcia Mariko Nakano adaptou culturalmente e validou para a língua portuguesa a Short Physical Performance Battery (SPPB). O estudo avaliou a c… |
| C8 | Segundo a OMS, como o ambiente físico influencia o risco de quedas? | Nakano_MarciaMariko_M.pdf, WHOGlobalReportonFalls PreventioninOlderAge.pdf | RAG | ✅ | ✅ | Segundo a OMS, o ambiente físico influencia o risco de quedas através de fatores de risco ambientais que interagem com as condições físicas dos indivíduos. Esse… |
| C9 | Como o ElderSync classifica o risco (faixas)? | Nakano_MarciaMariko_M.pdf | RAG | ✅ | ❌ | Não encontrei a informação sobre como o ElderSync classifica o risco em faixas nos trechos fornecidos. |
| C10 | Como é feito o procedimento do teste TUG? | GUIA_FISIOTERAPEUTA.md, J American Geriatrics Society - February 1991 - Podsiadlo - The Timed  Up   Go   A Test of Basic Functional Mobility for.pdf, Nakano_MarciaMariko_M.pdf | RAG | ✅ | ✅ | O teste "Timed Up and Go" (TUG) é um procedimento simples e prático que avalia a mobilidade funcional de idosos. O teste consiste nos seguintes passos: 1. **Pre… |
| F6 | Me dê uma receita de bolo de cenoura. | web (Tavily) | fallback | ✅ | ✅ | Aqui está uma receita de bolo de cenoura: **Ingredientes:** - 3 cenouras médias - 3 ovos - 1 xícara de óleo de canola - 2 xícaras de açúcar - 2 xícaras de farin… |
| F7 | Qual a cotação do dólar hoje? | web (Tavily) | fallback | ✅ | ✅ | A cotação do dólar hoje varia conforme as fontes consultadas. Aqui estão algumas cotações: - R$ 5,07 (comercial) - [Dólar Hoje](https://dolarhoje.com) - R$ 5,21… |
| F8 | Quais os efeitos colaterais da vacina da gripe? | web (Tavily) | fallback | ✅ | ✅ | Os efeitos colaterais da vacina da gripe incluem: 1. Dor local da injeção 2. Vermelhidão e endurecimento no local da aplicação (ocorrem em 15% a 20% dos vacinad… |
| F9 | Quem foi Santos Dumont? | web (Tavily) | fallback | ✅ | ✅ | Santos Dumont foi um inventor e aeronauta brasileiro, conhecido como "o pai da aviação". Ele nasceu em 20 de julho de 1873 e faleceu em 23 de julho de 1932. Dum… |
| F10 | Qual a fórmula química da água? | web (Tavily) | fallback | ✅ | ✅ | A fórmula química da água é H2O, o que significa que cada molécula de água é formada por dois átomos de hidrogênio e um átomo de oxigênio. Fontes: - https://www… |

## Resultados — conjunto de VALIDAÇÃO

| ID | Pergunta | Fonte recuperada | Rota | Roteamento | Correção | Resposta (resumo) |
|----|----------|------------------|------|:----------:|:--------:|-------------------|
| C1 | Qual a pontuação máxima da SPPB e o que ela indica? | ElderSync_v2_Reestruturacao.pdf, Nakano_MarciaMariko_M.pdf | RAG | ✅ | ✅ | A pontuação máxima da SPPB (Short Physical Performance Battery) é 12 pontos. Essa pontuação indica um bom desempenho funcional. A graduação dos resultados é a s… |
| C2 | Quais são os três componentes (testes) que compõem a SPPB? | ElderSync_v2_Reestruturacao.pdf, Nakano_MarciaMariko_M.pdf | RAG | ✅ | ✅ | Os três componentes que compõem a SPPB (Short Physical Performance Battery) são: 1. Testes de Equilíbrio (soma dos 3 subtestes) - pontuação máxima de 4 pontos. … |
| C3 | Por quanto tempo o idoso deve manter cada posição no teste de equilíbrio da SPPB? | ElderSync_v2_Reestruturacao.pdf, J American Geriatrics Society - February 1991 - Podsiadlo - The Timed  Up   Go   A Test of Basic Functional Mobility for.pdf, Nakano_MarciaMariko_M.pdf | RAG | ✅ | ✅ | No teste de equilíbrio da SPPB, o idoso deve conseguir manter-se em cada posição (side-by-side, semi-tandem stand, tandem stand) por 10 segundos. (Fonte: Nakano… |
| C4 | Quais fatores aumentam o risco de quedas em idosos? | Nakano_MarciaMariko_M.pdf, WHOGlobalReportonFalls PreventioninOlderAge.pdf | RAG | ✅ | ✅ | Os fatores que aumentam o risco de quedas em idosos incluem uma combinação de condições relacionadas à idade e doenças, além da interação do indivíduo com seu a… |
| C5 | O que é o teste Timed Up and Go (TUG)? | GUIA_FISIOTERAPEUTA.md, J American Geriatrics Society - February 1991 - Podsiadlo - The Timed  Up   Go   A Test of Basic Functional Mobility for.pdf, Nakano_MarciaMariko_M.pdf | RAG | ✅ | ✅ | O teste Timed Up and Go (TUG) é uma avaliação prática e confiável da mobilidade física em idosos. Ele consiste em medir o tempo que uma pessoa leva para se leva… |
| F1 | Qual a bula e posologia do paracetamol? | web (Tavily) | fallback | ✅ | ✅ | A bula e posologia do paracetamol variam conforme a apresentação do medicamento. Aqui estão algumas informações: 1. **Comprimidos de Paracetamol 500 mg**: - Adu… |
| F2 | Quem ganhou a Copa do Mundo de 2022? | web (Tavily) | fallback | ✅ | ✅ | A Copa do Mundo de 2022 foi ganha pela Seleção Argentina, que venceu a França na final após um empate de 3 a 3, levando a decisão para os pênaltis, onde venceu … |
| F3 | Qual a capital da Austrália? | web (Tavily) | fallback | ✅ | ✅ | A capital da Austrália é Camberra. Essa cidade é a sede do governo australiano e foi escolhida como um compromisso entre Sydney e Melbourne. [Fonte: Central de … |
| F4 | Como configurar um servidor nginx? | web (Tavily) | fallback | ✅ | ❌ | Os resultados da busca não fornecem informações específicas sobre como configurar um servidor Nginx. Eles mencionam aspectos gerais sobre a instalação e configu… |
| F5 | Qual o preço do iPhone lançado em 2025? | web (Tavily) | fallback | ✅ | ❌ | Os resultados da busca não contêm informações sobre o preço do iPhone lançado em 2025. Portanto, não posso responder a essa pergunta. |

## Resumo das métricas

| Conjunto | Acurácia de roteamento | Correção da resposta |
|----------|:----------------------:|:--------------------:|
| Teste (oficial) | 10/10 (100%) | 9/10 (90%) |
| Validação | 10/10 (100%) | 8/10 (80%) |
| Geral | 20/20 (100%) | 17/20 (85%) |

## Observações sobre as falhas de correção

- **F4** (Como configurar um servidor nginx?): Roteou p/ web corretamente, mas a busca não trouxe passos de configuração; agente respondeu 'não encontrei'.
- **F5** (Qual o preço do iPhone lançado em 2025?): Roteou p/ web corretamente, mas a busca não trouxe o preço; agente respondeu 'não encontrei'.
- **C9** (Como o ElderSync classifica o risco (faixas)?): Falha de recuperação: o trecho de classificação de risco do ElderSync está no corpus, mas ficou fora do top-8; agente respondeu 'não encontrei' (não alucinou).

> As falhas de correção não são alucinações: em todos os casos o sistema **admitiu não ter encontrado** em vez de inventar. As causas são qualidade de recuperação (modelo de embedding pequeno) e resultados de busca web pobres — melhorias futuras: reranker, modelo de embedding maior, mais resultados no Tavily.
