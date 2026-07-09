## Como funciona

1. **Captura de imagem** (`white_filter.py`): captura o frame da câmera (webcam, ou celular via DroidCam USB) e converte para HSV.
2. **Filtro de branco**: aplica um range de cor (ajustável por trackbars) para isolar a faixa branca no chão e remove ruído com operações morfológicas.
3. **Divisão da imagem**: a imagem é dividida em três regiões (esquerda, centro, direita). O programa verifica se a faixa branca toca as regiões laterais.
4. **Decisão de direção**:
   - Faixa branca na região esquerda → vira para a **direita**
   - Faixa branca na região direita → vira para a **esquerda**
   - Caso contrário → mantém o servo **centralizado**
5. **Controle dos motores** (`motores.py`): aciona os motores DC (propulsão) via driver L298N e o servo (direção) via PWM nos pinos GPIO do Raspberry Pi.

Se o `RPi.GPIO` não estiver disponível (ex: rodando em um PC Windows/Linux sem Raspberry Pi), o módulo `motores.py` cai automaticamente para o mock `fake_rpi`, permitindo testar a visão computacional sem hardware.

## Hardware

| Componente              | Pino (BCM) |
|-------------------------|------------|
| Motor esquerdo — ENA     | 12 (PWM)   |
| Motor esquerdo — IN1/IN2 | 23 / 24    |
| Motor direito — ENB      | 13 (PWM)   |
| Motor direito — IN3/IN4  | 27 / 22    |
| Servo de direção         | 18 (PWM)   |

## Instalação

### Utilizando o pip

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux / Raspberry Pi
source venv/bin/activate

pip install -r requirements.txt
```

Também é possível instalar as dependências pelo `pyproject.toml`:

```bash
pip install -e .
```

### Utilizando uv

```bash
uv sync
```

## Uso

### Preview do whitefilter

```bash
python src/white_filter.py
```

Controles da janela:

| Tecla / elemento | Ação                                      |
|------------------|-------------------------------------------|
| `Q`              | Sair                                       |
| `S`              | Salvar o frame atual (`white_filter.png`)  |
| Trackbars        | Ajustar o range de branco (S max, V min) em tempo real |

A janela exibe três imagens lado a lado: frame original (com overlay das regiões), máscara de branco e resultado filtrado.

### Calibração da câmera

```bash
python src/camera_calibration.py
```

O script pede o tamanho real da AprilTag e a distância de referência, detecta a tag pela câmera e salva a calibração em `config/camera_calibration.json`.

### Teste da câmera

```bash
python src/sign_detection.py
```

O script identifica as AprilTags pela câmera e imprime no terminal o ID da tag, a placa associada e a distância aproximada.

## Estrutura do projeto

```
.
├── config/
│   ├── camera_calibration.example.json # Exemplo dos dados de calibração
│   └── signs_id.json                   # Relação entre IDs das AprilTags e placas
├── src/
│   ├── carro/
│   │   ├── __init__.py
│   │   ├── camera.py                   # Funções reutilizáveis para captura de câmera
│   │   ├── signs.py                    # Funções reutilizáveis para detectar placas
│   │   └── terminal.py                 # Funções auxiliares para saída no terminal
│   ├── camera_calibration.py           # Calibração da câmera usando uma AprilTag de referência
│   ├── motores.py                      # Controle dos motores DC e do servo via GPIO/PWM
│   ├── sign_detection.py               # Teste de detecção de placas no terminal
│   └── white_filter.py                 # Captura de câmera, filtro de branco e lógica de direção
├── CONTRIBUTING.md                     # Convenções de commit do projeto
├── README.md                           # Documentação principal
├── pyproject.toml                      # Metadados e dependências do projeto
├── requirements.txt                    # Dependências do projeto para uso com pip
└── uv.lock                             # Lockfile de dependências do uv
```

## Convenções

Veja [CONTRIBUTING.md](CONTRIBUTING.md) para as convenções de commit usadas no projeto.
