# Guia Rápido — Sensor de Movimento (ElderSync)

> Para fisioterapeutas. Leia antes da primeira sessão com o dispositivo.

---

## 1. O que é o dispositivo?

É um pequeno sensor (ESP32 + acelerômetro) que o paciente veste durante os testes da SPPB e TUG. Ele coleta dados de movimento automaticamente enquanto você aplica os testes pelo sistema.

**Você não precisa mexer no sensor.** Toda a operação é feita pelo computador/tablet.

---

## 2. Ligando o dispositivo

1. Ligue o sensor.
2. Aguarde ~10 segundos — ele se conecta sozinho ao Wi-Fi e ao sistema.
3. Observe a **luz LED** do sensor:

| LED                                   | Significado               | O que fazer                                                                          |
| ------------------------------------- | ------------------------- | ------------------------------------------------------------------------------------ |
| **Apagado**                           | Sem conexão Wi-Fi         | Verifique se o sensor está ligado e se o Wi-Fi está disponível. Aguarde até 20s.     |
| **Piscando devagar** (1x por segundo) | Pronto, esperando comando | Tudo certo! Pode iniciar os testes.                                                  |
| **Piscando rápido** (4x por segundo)  | Calibrando                | Não mexa no sensor. Aguarde ~5 segundos.                                             |
| **Aceso fixo**                        | Medindo (coletando dados) | Teste em andamento, aguarde. Não desligue o sensor e nem pule para um próximo teste. |

> **Regra simples:** piscando devagar = pronto. Aceso fixo = medindo. Piscando rápido = calibrando.

---

## 3. Iniciando uma sessão no sistema

1. Faça login no ElderSync.
2. Selecione o paciente e inicie uma nova sessão de avaliação.
3. Na tela do teste, o sistema mostra um **indicador de status do sensor**:

| Indicador (na tela)   | Cor                | Significado                          |
| --------------------- | ------------------ | ------------------------------------ |
| "Sensor conectado"    | Cinza              | Sensor pronto, nenhuma medição ainda |
| "Calibrando..."       | Amarelo (pulsando) | Calibração em andamento              |
| "Calibrado"           | Verde              | Pronto para iniciar o teste          |
| "Medindo..."          | Verde              | Coleta de dados em andamento         |
| "Dados recebidos"     | Verde              | Dados chegaram com sucesso           |
| "Enviando comando..." | Amarelo (pulsando) | Aguardando resposta do sensor        |
| "Erro sensor"         | Vermelho           | Problema de conexão (veja seção 6)   |

> **Observação:** Dê prioridade para o guia de luzes(item 2).

---

## 4. Fluxo de um teste (passo a passo)

### 4.1 Calibração (uma vez antes de começar)

1. Posicione o sensor no paciente (conforme protocolo).
2. Peça ao paciente para **ficar parado**.
3. Clique em **"Calibrar"** no sistema.
4. O LED pisca rápido (~5 segundos). O indicador na tela fica amarelo.
5. Quando o LED voltar a piscar devagar e a tela mostrar **"Calibrado" (verde)**, está pronto.

> **Importante:** durante a calibração o paciente não deve se mover. É quando o sensor "aprende" a posição de repouso.

### 4.2 Execução do teste

1. Clique em **"Iniciar"** no teste desejado (ex: Equilíbrio A, Marcha 1, etc.).
2. O LED do sensor fica **aceso fixo** — a coleta começou.
3. O cronômetro na tela roda junto.
4. Aplique o teste normalmente com o paciente.
5. Quando terminar, clique em **"Parar"**.
6. O sensor envia os dados automaticamente. Aguarde alguns segundos.

> **Ponto importante:** Não dê inicio a outro teste enquanto a luz do dispositivo estiver acessa de forma continua. Espere a luz começar a a piscar.

### 4.3 Após o teste

1. A tela mostra **"Dados recebidos"** (verde).
2. Os dados do sensor aparecem logo abaixo, com as métricas coletadas (veja seção 5).
3. Um **contador de 15 segundos** vai aparecer(ele pode demorar um pouco a aparecer na tela) — é o tempo de sincronização do sensor.
4. Quando o contador zerar, você pode iniciar o próximo teste.

> **Não inicie o próximo teste antes do contador zerar.** O sensor precisa desse tempo para se preparar.

---

## 5. Entendendo os dados na tela

Após cada teste, o sistema exibe os dados coletados pelo sensor. Você verá métricas diferentes dependendo do tipo de teste:

### Testes de Equilíbrio (Balance A, B, C)

| Métrica          | O que significa                                                               |
| ---------------- | ----------------------------------------------------------------------------- |
| **Amplitude AP** | Quanto o paciente oscilou para frente e para trás (ântero-posterior), em m/s² |
| **Amplitude ML** | Quanto oscilou para os lados (médio-lateral), em m/s²                         |
| **RMS AP**       | Média da oscilação ântero-posterior                                           |
| **RMS ML**       | Média da oscilação médio-lateral                                              |
| **Duração**      | Tempo real da coleta em segundos                                              |

> **Valores maiores = mais oscilação = menos estabilidade.** Compare entre pré e pós intervenção.

### Testes de Marcha e TUG

| Métrica                 | O que significa                                    |
| ----------------------- | -------------------------------------------------- |
| **Índice de Oscilação** | Variabilidade geral do movimento                   |
| **Aceleração Média**    | Intensidade média do movimento durante a caminhada |
| **Duração**             | Tempo real da coleta                               |

### Teste de Sentar/Levantar (Chair Stand)

| Métrica                   | O que significa                                  |
| ------------------------- | ------------------------------------------------ |
| **Índice de Oscilação**   | Variabilidade do movimento                       |
| **Aceleração Média**      | Intensidade média do esforço                     |
| **Ângulo Máximo**         | Maior inclinação do tronco durante as repetições |
| **Ângulos por repetição** | Inclinação em cada uma das 5 repetições          |
| **Duração**               | Tempo real                                       |

---

## 6. Problemas comuns e soluções

### O LED está apagado

- Verifique se o sensor está ligado/carregado.
- Verifique se a rede Wi-Fi está funcionando.
- Aguarde até 30 segundos. Se não piscar, desligue e religue o sensor.

### A tela mostra "Erro sensor" (vermelho)

- O sensor pode ter perdido a conexão momentaneamente.
- **Aguarde 30 segundos** — ele reconecta sozinho automaticamente.
- Se persistir: desligue e religue o sensor. Aguarde o LED piscar devagar.
- Você **não perde a sessão** — os testes já salvos continuam intactos.

### O sensor não responde ao comando "Iniciar"

- Verifique se o LED está piscando devagar (pronto).
- Se o LED está apagado, o sensor perdeu a conexão — aguarde a reconexão.
- Se o indicador na tela está amarelo ("Enviando comando..."), aguarde alguns segundos.

### A tela mostra "Enviando comando..." por muito tempo

- O sensor pode estar fora de alcance do Wi-Fi ou desligado.
- Verifique o LED do sensor.
- Se necessário, cancele e tente novamente.

### Os dados não apareceram após o teste

- Aguarde até 10 segundos — o envio de dados pode demorar um pouco em redes lentas.
- Se não aparecer, o sensor pode ter perdido conexão durante o envio. O teste pode ser repetido.

### O contador de 15 segundos apareceu

- Isso é normal! É o tempo de sincronização entre o sensor e o sistema.
- Aguarde o contador zerar antes de iniciar o próximo teste.

---

## 7. Dicas importantes

- **O sensor é opcional.** Se ele não estiver disponível ou der problema, você pode aplicar os testes normalmente pelo sistema — só não terá os dados de movimento.
- **Não precisa parear via Bluetooth.** O sensor conecta sozinho pelo Wi-Fi.
- **Uma calibração por sessão** é suficiente, a não ser que reposicione o sensor no paciente.
- **O sensor coleta 50 leituras por segundo.** Não se preocupe em sincronizar manualmente — o sistema faz isso.
- **Os dados ficam salvos automaticamente** no sistema junto com o tempo do cronômetro.

---

## Resumo visual rápido

```
LIGAR SENSOR → LED pisca devagar? → SIM → Calibrar → LED pisca rápido (5s)
                                                    → LED pisca devagar = pronto

INICIAR TESTE → LED aceso fixo (medindo) → PARAR TESTE → dados enviados
             → Tela: "Medindo..." (verde)            → Tela: "Dados recebidos"
                                                      → Aguardar 15s
                                                      → Próximo teste
```

---

_ElderSync — Sistema de Avaliação de Mobilidade em Idosos_
