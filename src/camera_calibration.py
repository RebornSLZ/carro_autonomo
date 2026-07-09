import json
import statistics
from pathlib import Path

import cv2  # Esta biblioteca é a 'opencv-contrib-python' e não a 'opencv-python'.
import numpy as np


PASTA_CONFIG = Path(__file__).resolve().parent.parent / "config"
ARQUIVO_CALIBRACAO = PASTA_CONFIG / "camera_calibration.json"
TAMANHO_PADRAO_TAG_M = 0.025      # 25 Centímetros
DISTANCIA_PADRAO_TAG_M = 0.3      # 30 Centímetros
AMOSTRAS_PARA_COLETAR = 30


def calcular_tamanho_tag_px(cantos_tag: np.ndarray) -> float:
    """Calcula o tamanho médio do lado da AprilTag em pixels.

    Parâmetros:
    - cantos_tag: matriz com os quatro cantos detectados da AprilTag.

    Retorna:
    - Tamanho médio do lado da tag em pixels.
    """
    cantos = cantos_tag.reshape((4, 2))

    tamanhos_lados_px = [
        np.linalg.norm(cantos[0] - cantos[1]),
        np.linalg.norm(cantos[1] - cantos[2]),
        np.linalg.norm(cantos[2] - cantos[3]),
        np.linalg.norm(cantos[3] - cantos[0]),
    ]
    return float(np.mean(tamanhos_lados_px))


def pedir_float(mensagem: str, padrao: float | None = None) -> float:
    """Pede um número decimal ao usuário pelo terminal.

    Parâmetros:
    - mensagem: texto exibido no terminal antes da entrada.
    - padrao: valor usado quando o usuário pressiona Enter sem digitar nada.

    Retorna:
    - Número informado pelo usuário, ou o valor padrão quando ele existir.
    """
    while True:
        valor = input(mensagem).strip().replace(",", ".")

        if not valor and padrao is not None:
            return padrao

        try:
            valor_convertido = float(valor)
        except ValueError:
            print("Digite um número válido.")
            continue

        if valor_convertido <= 0:
            print("Digite um valor maior que zero.")
            continue

        return valor_convertido


def salvar_calibracao(tamanho_tag_m: float, distancia_focal_px: float) -> None:
    """Salva os dados de calibração da câmera em um arquivo JSON.

    Parâmetros:
    - tamanho_tag_m: tamanho real do lado da AprilTag em metros.
    - distancia_focal_px: distância focal estimada da câmera em pixels.
    """
    calibracao = {
        "tag_size_m": round(tamanho_tag_m, 6),
        "focal_length_px": round(distancia_focal_px, 2),
    }

    PASTA_CONFIG.mkdir(exist_ok=True)

    with ARQUIVO_CALIBRACAO.open("w", encoding="utf-8") as arquivo:
        json.dump(calibracao, arquivo, indent=2)
        arquivo.write("\n")


def main() -> None:
    """Executa a calibração da câmera usando uma AprilTag de referência."""
    print("Calibração da câmera com AprilTag")
    print("Use a mesma tag e a mesma resolução da câmera depois no sign_detection.py.\n")

    tamanho_tag_m = pedir_float(
        f"Medida com comprimento da tag em metros [{TAMANHO_PADRAO_TAG_M}]: ",
        TAMANHO_PADRAO_TAG_M,
    )
    distancia_referencia_m = pedir_float(
        f"Distância da câmera até a tag, em metros [{DISTANCIA_PADRAO_TAG_M}]: ",
        DISTANCIA_PADRAO_TAG_M,
    )

    input(
        "\nPosicione a tag nessa distância, deixe-a visível para a câmera "
        "e pressione Enter para começar a calibração."
    )

    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        print("Erro: Não foi possível acessar a webcam.")
        return

    dicionario = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_APRILTAG_36h11)
    parametros = cv2.aruco.DetectorParameters()
    detector = cv2.aruco.ArucoDetector(dicionario, parametros)

    amostras_distancia_focal = []
    print(f"Coletando {AMOSTRAS_PARA_COLETAR} amostras...")

    try:
        while len(amostras_distancia_focal) < AMOSTRAS_PARA_COLETAR:
            capturou, frame = cap.read()

            if not capturou:
                print("Erro: Falha ao capturar imagem.")
                break

            cinza = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            cantos, ids, _ = detector.detectMarkers(cinza)

            if ids is None:
                continue

            tamanho_tag_px = calcular_tamanho_tag_px(cantos[0])

            if tamanho_tag_px <= 0:
                continue

            distancia_focal_px = (tamanho_tag_px * distancia_referencia_m) / tamanho_tag_m
            amostras_distancia_focal.append(distancia_focal_px)

            print(
                f"Amostra {len(amostras_distancia_focal):02d}/{AMOSTRAS_PARA_COLETAR}: "
                f"{distancia_focal_px:.2f} px"
            )
    finally:
        cap.release()

    if not amostras_distancia_focal:
        print("Nenhuma AprilTag foi detectada. Calibração não salva.")
        return

    distancia_focal_final_px = statistics.median(amostras_distancia_focal)
    salvar_calibracao(tamanho_tag_m, distancia_focal_final_px)

    print(f"\nCalibração salva em {ARQUIVO_CALIBRACAO}:")
    print(f"tag_size_m: {tamanho_tag_m:.6f}")
    print(f"focal_length_px: {distancia_focal_final_px:.2f}")


if __name__ == "__main__":
    main()
