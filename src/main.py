import time
from utils.motores import iniciar, frente, direita, esquerda, encerrar


def main() -> None:
    print("Iniciando GPIO...")
    # Inicia com velocidade_base 0, assim os motores DC não se movem
    iniciar(0)

    try:
        print("Movendo para o Centro...")
        frente()  # Na sua API, frente() também centraliza o servo
        time.sleep(1)

        print("Virando para a Direita...")
        direita()
        time.sleep(1)

        print("Virando para a Esquerda...")
        esquerda()
        time.sleep(1)

        print("Voltando para o Centro...")
        frente()
        time.sleep(1)

    except KeyboardInterrupt:
        # Permite parar o teste no meio apertando Ctrl+C
        print("\nTeste interrompido pelo usuário.")

    finally:
        print("Limpando GPIO e encerrando...")
        encerrar()
        print("FIM")


if __name__ == "__main__":
    main()
