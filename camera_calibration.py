import json
import statistics
from pathlib import Path

import cv2  # Esta biblioteca é a 'opencv-contrib-python' e não a 'opencv-python'.
import numpy as np


CALIBRATION_FILE = Path("camera_calibration.json")
DEFAULT_TAG_SIZE_M = 0.025      # 25 Centímetros
DEFAULT_TAG_DISTANCE_M = 0.3    # 30 Centímetros
SAMPLES_TO_COLLECT = 30


def get_marker_size_px(marker_corners):
    corners = marker_corners.reshape((4, 2))

    side_lengths_px = [
        np.linalg.norm(corners[0] - corners[1]),
        np.linalg.norm(corners[1] - corners[2]),
        np.linalg.norm(corners[2] - corners[3]),
        np.linalg.norm(corners[3] - corners[0]),
    ]
    return float(np.mean(side_lengths_px))


def ask_float(prompt, default=None):
    while True:
        value = input(prompt).strip().replace(",", ".")

        if not value and default is not None:
            return default

        try:
            parsed_value = float(value)
        except ValueError:
            print("Digite um número válido.")
            continue

        if parsed_value <= 0:
            print("Digite um valor maior que zero.")
            continue

        return parsed_value


def save_calibration(tag_size_m, focal_length_px):
    calibration = {
        "tag_size_m": round(tag_size_m, 6),
        "focal_length_px": round(focal_length_px, 2),
    }

    with CALIBRATION_FILE.open("w", encoding="utf-8") as file:
        json.dump(calibration, file, indent=2)
        file.write("\n")


def main():
    print("Calibração da câmera com AprilTag")
    print("Use a mesma tag e a mesma resolução da câmera depois no apriltag.py.\n")

    tag_size_m = ask_float(
        f"Medida com comprimento da tag em metros [{DEFAULT_TAG_SIZE_M}]: ",
        DEFAULT_TAG_SIZE_M,
    )
    reference_distance_m = ask_float(
        f"Distância da câmera até a tag, em metros [{DEFAULT_TAG_DISTANCE_M}]: ",
        DEFAULT_TAG_DISTANCE_M,
    )

    input(
        "\nPosicione a tag nessa distância, deixe-a visível para a câmera "
        "e pressione Enter para começar a calibração."
    )

    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        print("Erro: Não foi possível acessar a webcam.")
        return

    dictionary = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_APRILTAG_36h11)
    parameters = cv2.aruco.DetectorParameters()
    detector = cv2.aruco.ArucoDetector(dictionary, parameters)

    focal_length_samples = []
    print(f"Coletando {SAMPLES_TO_COLLECT} amostras...")

    try:
        while len(focal_length_samples) < SAMPLES_TO_COLLECT:
            ret, frame = cap.read()

            if not ret:
                print("Erro: Falha ao capturar imagem.")
                break

            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            corners, ids, _ = detector.detectMarkers(gray)

            if ids is None:
                continue

            marker_size_px = get_marker_size_px(corners[0])

            if marker_size_px <= 0:
                continue

            focal_length_px = (marker_size_px * reference_distance_m) / tag_size_m
            focal_length_samples.append(focal_length_px)

            print(
                f"Amostra {len(focal_length_samples):02d}/{SAMPLES_TO_COLLECT}: "
                f"{focal_length_px:.2f} px"
            )
    finally:
        cap.release()

    if not focal_length_samples:
        print("Nenhuma AprilTag foi detectada. Calibração não salva.")
        return

    focal_length_px = statistics.median(focal_length_samples)
    save_calibration(tag_size_m, focal_length_px)

    print(f"\nCalibração salva em {CALIBRATION_FILE}:")
    print(f"tag_size_m: {tag_size_m:.6f}")
    print(f"focal_length_px: {focal_length_px:.2f}")


if __name__ == "__main__":
    main()
