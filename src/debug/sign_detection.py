import time
from pathlib import Path
import sys

sys.path.append(str(Path(__file__).resolve().parents[1]))

from utils.camera import abrir_camera, fechar_camera, ler_frame
from utils.signs import (
    carregar_calibracao,
    carregar_placas,
    criar_detector_apriltag,
    detectar_tags,
)
from utils.terminal import imprimir_tabela_placas


def main() -> None:
    """Executa o teste de detecção de placas pela webcam."""
    try:
        calibracao = carregar_calibracao()
    except (FileNotFoundError, KeyError, ValueError) as error:
        print(f"Erro ao carregar calibração: {error}")
        return

    try:
        placas = carregar_placas()
    except (FileNotFoundError, ValueError) as error:
        print(f"Erro ao carregar ações das AprilTags: {error}")
        return

    try:
        camera = abrir_camera()
    except RuntimeError as error:
        print(f"Erro: {error}")
        return

    detector = criar_detector_apriltag()

    print("Detectando AprilTags. Pressione Ctrl+C para encerrar.")

    try:
        while True:
            frame = ler_frame(camera)

            if frame is None:
                print("Erro: Falha ao capturar imagem.")
                break

            deteccoes = detectar_tags(frame, detector, calibracao, placas)

            if deteccoes:
                print("\n")
                imprimir_tabela_placas(deteccoes)

            time.sleep(0.2)
    except KeyboardInterrupt:
        print("\nDetecção encerrada.")
    finally:
        fechar_camera(camera)


if __name__ == "__main__":
    main()
