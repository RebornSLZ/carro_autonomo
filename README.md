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

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux / Raspberry Pi
source venv/bin/activate

pip install -r requirements.txt
```

## Uso

```bash
python white_filter.py
```

### Controles da janela

| Tecla / elemento | Ação                                      |
|------------------|-------------------------------------------|
| `Q`              | Sair                                       |
| `S`              | Salvar o frame atual (`white_filter.png`)  |
| Trackbars        | Ajustar o range de branco (S max, V min) em tempo real |

A janela exibe três imagens lado a lado: frame original (com overlay das regiões), máscara de branco e resultado filtrado.

## Estrutura do projeto

```
.
├── motores.py       # Controle dos motores DC e do servo via GPIO/PWM
├── white_filter.py  # Captura de câmera, filtro de branco e lógica de direção
└── requirements.txt # Dependências do projeto
```

## Convenções

Veja [CONTRIBUTING.md](CONTRIBUTING.md) para as convenções de commit usadas no projeto.
