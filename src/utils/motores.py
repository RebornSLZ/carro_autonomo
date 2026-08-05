"""
Controle de motores — 2 DC (propulsão) + 1 servo (direção)

Pinagem:

    Propulsão — L298N  →  GPIO (BCM)
    ──────────────────────────────────
    ENA  →  12   (PWM motor esquerdo)
    IN1  →  23
    IN2  →  24
    ENB  →  13   (PWM motor direito)
    IN3  →  27
    IN4  →  22

    Direção — Servo  →  GPIO (BCM)
    ──────────────────────────────
    Sinal  →  18   (PWM 50 Hz)

Servo: duty cycle (porcentagem do tempo em que o sinal fica ligado) para 50 Hz (período = 20 ms)
    Esquerda →  5.0 %  (~1.0 ms)
    Centro   →  7.5 %  (~1.5 ms)
    Direita  → 10.0 %  (~2.0 ms)

API pública:
    iniciar(velocidade_base)  — configura GPIO e inicia PWM
    frente()                  — segue reto
    direita()                 — vira para a direita
    esquerda()                — vira para a esquerda
    parar()                   — para os motores de propulsão
    encerrar()                — libera GPIO
"""


#Testa se tem GPIO, caso não tenha, entra em mockup
# try:
#     import RPi.GPIO as GPIO
# except ImportError:
#     from fake_rpi.RPi import GPIO

import RPi.GPIO as GPIO


# Pinos (BCM)
ENA = 12
IN1 = 23
IN2 = 24

ENB = 13
IN3 = 27
IN4 = 22

SERVO_PIN = 18

# Parâmetros de propulsão
FREQ_MOTOR_HZ = 1000
VEL_BASE      = 70     # duty cycle em reta (0–100)

# Parâmetros do servo (50 Hz) 
FREQ_SERVO_HZ   = 50
SERVO_ESQUERDA  = 5.0   # duty cycle → ~1.0 ms
SERVO_CENTRO    = 7.5   # duty cycle → ~1.5 ms
SERVO_DIREITA   = 10.0  # duty cycle → ~2.0 ms

# ── Objetos PWM ───────────────────────────────────────────────────────────────
_pwm_esq:   GPIO.PWM | None = None
_pwm_dir:   GPIO.PWM | None = None
_pwm_servo: GPIO.PWM | None = None


def iniciar(velocidade_base: int = VEL_BASE) -> None:
    """Configura GPIO e inicia todos os canais PWM."""
    global _pwm_esq, _pwm_dir, _pwm_servo, VEL_BASE

    VEL_BASE = velocidade_base

    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)

    GPIO.setup([ENA, IN1, IN2, ENB, IN3, IN4, SERVO_PIN], GPIO.OUT)

    _pwm_esq   = GPIO.PWM(ENA,       FREQ_MOTOR_HZ)
    _pwm_dir   = GPIO.PWM(ENB,       FREQ_MOTOR_HZ)
    _pwm_servo = GPIO.PWM(SERVO_PIN, FREQ_SERVO_HZ)

    _pwm_esq.start(0)
    _pwm_dir.start(0)
    _pwm_servo.start(SERVO_CENTRO)   # inicia com direção centralizada


# Motores de propulsão

def _motor_esquerdo(duty: int) -> None:
    GPIO.output(IN1, GPIO.HIGH)
    GPIO.output(IN2, GPIO.LOW)
    _pwm_esq.ChangeDutyCycle(duty)

def _motor_direito(duty: int) -> None:
    GPIO.output(IN3, GPIO.HIGH)
    GPIO.output(IN4, GPIO.LOW)
    _pwm_dir.ChangeDutyCycle(duty)

def _parar_motores() -> None:
    GPIO.output(IN1, GPIO.LOW)
    GPIO.output(IN2, GPIO.LOW)
    GPIO.output(IN3, GPIO.LOW)
    GPIO.output(IN4, GPIO.LOW)
    _pwm_esq.ChangeDutyCycle(0)
    _pwm_dir.ChangeDutyCycle(0)


# Servo de direção

def _servo(duty: float) -> None:
    _pwm_servo.ChangeDutyCycle(duty)


def servo_direita() -> None:
    _servo(SERVO_DIREITA)


def servo_esquerda() -> None:
    _servo(SERVO_ESQUERDA)


def servo_centro() -> None:
    _servo(SERVO_CENTRO)


# Comandos principais

def frente() -> None:
    """Segue reto: servo centralizado, ambos os motores na velocidade base."""
    _servo(SERVO_CENTRO)
    _motor_esquerdo(VEL_BASE)
    _motor_direito(VEL_BASE)


def direita() -> None:
    """Vira para a direita: servo direita, motores em velocidade base."""
    _servo(SERVO_DIREITA)
    _motor_esquerdo(VEL_BASE)
    _motor_direito(VEL_BASE)


def esquerda() -> None:
    """Vira para a esquerda: servo esquerda, motores em velocidade base."""
    _servo(SERVO_ESQUERDA)
    _motor_esquerdo(VEL_BASE)
    _motor_direito(VEL_BASE)


def parar() -> None:
    """Para os motores de propulsão e centraliza o servo."""
    _servo(SERVO_CENTRO)
    _parar_motores()


def encerrar() -> None:
    """Para tudo e libera os pinos GPIO."""
    parar()
    if _pwm_esq:
        _pwm_esq.stop()
    if _pwm_dir:
        _pwm_dir.stop()
    if _pwm_servo:
        _pwm_servo.stop()
    GPIO.cleanup()
