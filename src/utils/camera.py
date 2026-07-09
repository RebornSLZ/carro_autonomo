from typing import Any

import cv2
import numpy as np


Camera = Any


def abrir_camera(indice_camera: int = 0) -> Camera:
    """Abre a câmera pelo índice informado.

    Parâmetros:
    - indice_camera: índice da câmera usado pelo OpenCV.

    Retorna:
    - Objeto de captura de vídeo do OpenCV.
    """
    camera = cv2.VideoCapture(indice_camera)

    if not camera.isOpened():
        raise RuntimeError("Não foi possível acessar a webcam.")

    return camera


def ler_frame(camera: Camera) -> np.ndarray | None:
    """Lê um frame da câmera.

    Parâmetros:
    - camera: objeto de captura retornado por `abrir_camera`.

    Retorna:
    - Frame capturado em formato BGR, ou `None` se a captura falhar.
    """
    capturou, frame = camera.read()

    if not capturou:
        return None

    return frame


def fechar_camera(camera: Camera) -> None:
    """Libera o uso da câmera.

    Parâmetros:
    - camera: objeto de captura retornado por `abrir_camera`.
    """
    camera.release()
