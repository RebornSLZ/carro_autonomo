import json
import time
from pathlib import Path

import cv2  # Esta biblioteca é a 'opencv-contrib-python' e não a 'opencv-python'.
import numpy as np


CALIBRATION_FILE = Path("camera_calibration.json")


def get_marker_size_px(marker_corners):
    corners = marker_corners.reshape((4, 2))

    side_lengths_px = [
        np.linalg.norm(corners[0] - corners[1]),
        np.linalg.norm(corners[1] - corners[2]),
        np.linalg.norm(corners[2] - corners[3]),
        np.linalg.norm(corners[3] - corners[0]),
    ]
    return float(np.mean(side_lengths_px))


def load_calibration():
    if not CALIBRATION_FILE.exists():
        raise FileNotFoundError(
            f"Arquivo {CALIBRATION_FILE} não encontrado. "
            "Execute camera_calibration.py antes."
        )

    with CALIBRATION_FILE.open("r", encoding="utf-8") as file:
        calibration = json.load(file)

    tag_size_m = float(calibration["tag_size_m"])
    focal_length_px = float(calibration["focal_length_px"])
    return tag_size_m, focal_length_px


def estimate_distance_m(marker_corners, tag_size_m, focal_length_px):
    marker_size_px = get_marker_size_px(marker_corners)

    if marker_size_px <= 0:
        return None

    return (tag_size_m * focal_length_px) / marker_size_px


def main():
    try:
        tag_size_m, focal_length_px = load_calibration()
    except (FileNotFoundError, KeyError, ValueError, json.JSONDecodeError) as error:
        print(f"Erro ao carregar calibração: {error}")
        return

    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        print("Erro: Não foi possível acessar a webcam.")
        return

    dictionary = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_APRILTAG_36h11)
    parameters = cv2.aruco.DetectorParameters()
    detector = cv2.aruco.ArucoDetector(dictionary, parameters)

    print("Detectando AprilTags. Pressione Ctrl+C para encerrar.")

    try:
        while True:
            ret, frame = cap.read()

            if not ret:
                print("Erro: Falha ao capturar imagem.")
                break

            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            corners, ids, _ = detector.detectMarkers(gray)

            if ids is not None:
                print("-" * 30)
                for marker_corners, marker_id in zip(corners, ids.flatten()):
                    distance_m = estimate_distance_m(
                        marker_corners,
                        tag_size_m,
                        focal_length_px,
                    )

                    if distance_m is not None:
                        print(f"ID {marker_id}: {distance_m:.2f} m")

            time.sleep(0.2)
    except KeyboardInterrupt:
        print("\nDetecção encerrada.")
    finally:
        cap.release()


if __name__ == "__main__":
    main()
