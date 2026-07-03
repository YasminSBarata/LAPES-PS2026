# Integração IoT - ESP32 + MPU6050

Este documento explica como integrar sensores ESP32 com MPU6050 ao sistema de monitoramento de pacientes idosos.

## Métricas Coletadas

| #   | Métrica                            | Tipo                 | Como é medida                                                               |
| --- | ---------------------------------- | -------------------- | --------------------------------------------------------------------------- |
| 1   | **Contagem de passos**             | int (passos/dia)     | Picos no acelerômetro eixo Z > 1.2g, filtro passa-alta, intervalo mín. 0.3s |
| 2   | **Cadência média**                 | float (passos/min)   | Passos detectados / tempo em movimento                                      |
| 3   | **Tempo sentado/em pé/caminhando** | float (horas)        | Classificação por ângulo (giroscópio) + magnitude aceleração                |
| 4   | **Velocidade de marcha**           | float (m/s)          | Cadência × 0.7m (comprimento médio para idosos)                             |
| 5   | **Estabilidade postural**          | float (0-100)        | Desvio padrão da aceleração em pé (janela 10s), normalizado                 |
| 6   | **Quedas detectadas**              | bool + timestamp     | Accel > 2.5g + ângulo ~90°±20° + sem movimento > 5s                         |
| 7   | **Inatividade prolongada**         | int + duração        | Aceleração total < 0.15g por > 2h consecutivas                              |
| 8   | **TUG estimado**                   | float (segundos)     | Tempo sentado→em pé→caminhada→sentado                                       |
| 9   | **Transições bruscas**             | int (quantidade/dia) | Mudanças de orientação > 45° em < 1s                                        |
| 10  | **Padrão circadiano**              | array[24]            | Soma de movimento por hora do dia                                           |

## Arquitetura

```
┌─────────────────┐      ┌──────────────┐      ┌────────────────┐      ┌──────────────┐
│   MPU6050       │ I2C  │   ESP32      │ WiFi │   Supabase     │      │   Dashboard  │
│ (Acelerômetro   │ ───► │ (Processa +  │ ───► │ Edge Functions │ ───► │    React     │
│  + Giroscópio)  │      │   Envia)     │      │   (API REST)   │      │              │
└─────────────────┘      └──────────────┘      └────────────────┘      └──────────────┘
```

## Fluxo de Dados

1. **MPU6050** coleta dados brutos a 20Hz (aceleração 3D + giroscópio 3D)
2. **ESP32** processa localmente: detecta passos, classifica postura, detecta quedas
3. **ESP32** envia métricas agregadas a cada 1 minuto via HTTP POST
4. **Servidor** recebe, valida credenciais, acumula métricas do dia
5. **Dashboard** exibe dados em tempo real e histórico

## Endpoints IoT Disponíveis

| Método | Endpoint                | Autenticação               | Descrição                   |
| ------ | ----------------------- | -------------------------- | --------------------------- |
| POST   | `/iot/metrics`          | X-Device-Key + X-Device-Id | Recebe dados do sensor      |
| POST   | `/iot/reset-daily`      | X-Device-Key + X-Device-Id | Reseta métricas diárias     |
| POST   | `/iot/devices`          | Bearer Token               | Registra novo dispositivo   |
| GET    | `/patients/:id/metrics` | Bearer Token               | Busca histórico de métricas |
| GET    | `/patients/:id/alerts`  | Bearer Token               | Busca alertas do paciente   |

## Passo a Passo

### 1. Registrar um Dispositivo (no Dashboard)

Clique no botão "Registrar Dispositivo" na página do paciente. O sistema gerará:

- **Device ID**: Identificador único do dispositivo
- **API Key**: Chave secreta para autenticação

```javascript
// Exemplo de chamada (feita automaticamente pelo dashboard)
const response = await fetch("/api/iot/devices", {
  method: "POST",
  headers: {
    Authorization: `Bearer ${accessToken}`,
    "Content-Type": "application/json",
  },
  body: JSON.stringify({
    patientId: "uuid-do-paciente",
    deviceName: "Sensor do João",
  }),
});

const { device } = await response.json();
// device.deviceId -> usar no ESP32
// device.apiKey -> usar no ESP32
```

### 2. Configurar o ESP32

Use o código em `docs/esp32_code_example.ino`. Configure:

```cpp
// WiFi
const char* WIFI_SSID = "SuaRedeWiFi";
const char* WIFI_PASSWORD = "SuaSenhaWiFi";

// Servidor Supabase
const char* SERVER_URL = "https://SEU_PROJETO.supabase.co/functions/v1/make-server-ba5f214e/iot/metrics";

// Credenciais (obtidas no passo 1)
const char* DEVICE_ID = "xxxxx-xxxxx-xxxxx";
const char* API_KEY = "yyyyyyyyyyyyyyy";
```

### 3. Bibliotecas Arduino Necessárias

Instale via Arduino IDE (Sketch > Include Library > Manage Libraries):

- **ArduinoJson** (by Benoit Blanchon)
- Board: ESP32 Dev Module

### 4. Conexões do Hardware

```
MPU6050    ESP32
-------    -----
VCC   -->  3.3V
GND   -->  GND
SCL   -->  GPIO 22
SDA   -->  GPIO 21
```

## Formato dos Dados

### Dados enviados pelo ESP32 (métricas processadas):

```json
{
  "metrics": {
    "stepCount": 150,
    "averageCadence": 95.5,
    "timeSeated": 0.5,
    "timeStanding": 0.3,
    "timeWalking": 0.2,
    "gaitSpeed": 0.85,
    "posturalStability": 78,
    "fallDetected": false,
    "inactivityEpisodes": 0,
    "inactivityAvgDuration": 0,
    "tugEstimated": 12.5,
    "abruptTransitions": 2,
    "hourlyActivity": [0, 0, 0, 0, 0, 0, 5.2, 12.1, ...]
  },
  "raw": {
    "accel": { "x": 0.02, "y": -0.05, "z": 0.98 },
    "gyro": { "x": 0.5, "y": -0.3, "z": 0.1 }
  },
  "timestamp": 12345678
}
```

### Resposta do servidor:

```json
{
  "success": true,
  "metricId": "1738934400000-abc12345",
  "updatedMetrics": {
    "stepCount": 3250,
    "averageCadence": 92.3,
    "gaitSpeed": 0.82,
    "posturalStability": 75
  }
}
```

## Detecção de Eventos

### Classificação de Postura (no ESP32)

| Estado     | Ângulo do corpo | Aceleração | Variação  |
| ---------- | --------------- | ---------- | --------- |
| Sentado    | 60° - 100°      | ~1g        | Baixa     |
| Em pé      | < 30°           | ~1g        | Baixa     |
| Caminhando | -               | > 1.15g    | Periódica |

### Detecção de Queda (no ESP32)

1. Impacto: aceleração total > 2.5g
2. Posição horizontal: ângulo 70° - 110°
3. Imobilidade: sem movimento por > 5 segundos
4. Se todos os critérios forem atendidos → queda confirmada

### Inatividade Prolongada

- Detectada quando aceleração total permanece próxima a 1g por > 2 horas
- Gera alerta para verificação do paciente

## Testando sem Hardware

Para testar a API sem o hardware real, use curl ou Postman:

```bash
# Primeiro, registre um dispositivo (precisa de token de usuário)
# Depois, envie dados mock:

curl -X POST "https://SEU_PROJETO.supabase.co/functions/v1/make-server-ba5f214e/iot/metrics" \
  -H "Content-Type: application/json" \
  -H "X-Device-Id: seu-device-id" \
  -H "X-Device-Key: sua-api-key" \
  -d '{
    "metrics": {
      "stepCount": 100,
      "averageCadence": 95,
      "timeSeated": 0.5,
      "timeStanding": 0.3,
      "timeWalking": 0.2,
      "gaitSpeed": 0.85,
      "posturalStability": 80,
      "fallDetected": false,
      "inactivityEpisodes": 0,
      "abruptTransitions": 1,
      "hourlyActivity": 15.5
    },
    "timestamp": 12345678
  }'
```

## Considerações de Segurança

1. **API Key por dispositivo**: Cada dispositivo tem sua própria chave
2. **Associação fixa**: Dispositivo é vinculado a um paciente específico
3. **Validação no servidor**: Todas as credenciais são verificadas antes de aceitar dados
4. **HTTPS obrigatório**: Comunicação criptografada

## Calibração do ESP32

O código do ESP32 pode precisar de ajustes para cada paciente:

| Parâmetro             | Valor padrão | Descrição                          |
| --------------------- | ------------ | ---------------------------------- |
| `STEP_THRESHOLD`      | 1.2g         | Sensibilidade para detectar passos |
| `AVG_STEP_LENGTH`     | 0.7m         | Comprimento médio do passo         |
| `FALL_THRESHOLD`      | 2.5g         | Limite para detectar impacto       |
| `INACTIVITY_DURATION` | 2h           | Tempo para considerar inatividade  |

## Próximos Passos

- [x] UI no dashboard para registrar dispositivos
- [ ] Implementar gráficos de métricas em tempo real (polling a cada 30s)
- [ ] Adicionar notificações push para alertas de queda
- [ ] Criar histórico de métricas por dia/semana
- [ ] Adicionar RTC ao ESP32 para hora real no padrão circadiano
- [ ] Criar tela de histórico de atividades
- [ ] Implementar bateria/status do dispositivo
