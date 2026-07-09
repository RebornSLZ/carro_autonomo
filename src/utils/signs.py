from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import cv2
import numpy as np


PASTA_CONFIG = Path(__file__).resolve().parents[2] / "config"
ARQUIVO_CALIBRACAO = PASTA_CONFIG / "camera_calibration.json"
ARQUIVO_IDS_PLACAS = PASTA_CONFIG / "signs_id.json"
DetectorAprilTag = Any


@dataclass(frozen=True)
class CalibracaoCamera:
    tag_size_m: float
    focal_length_px: float


@dataclass(frozen=True)
class DeteccaoPlaca:
    id: int
    placa: str
    distancia_m: float


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


def carregar_calibracao(
    arquivo_calibracao: Path = ARQUIVO_CALIBRACAO,
) -> CalibracaoCamera:
    """Carrega os dados de calibração da câmera a partir do JSON.

    Parâmetros:
    - arquivo_calibracao: caminho do arquivo JSON com `tag_size_m` e `focal_length_px`.

    Retorna:
    - Objeto `CalibracaoCamera` com tamanho real da tag e distância focal em pixels.
    """
    if not arquivo_calibracao.exists():
        raise FileNotFoundError(
            f"Arquivo {arquivo_calibracao} não encontrado. "
            "Execute src/debug/camera_calibration.py antes."
        )

    with arquivo_calibracao.open("r", encoding="utf-8") as arquivo:
        calibracao = json.load(arquivo)

    return CalibracaoCamera(
        tag_size_m=float(calibracao["tag_size_m"]),
        focal_length_px=float(calibracao["focal_length_px"]),
    )


def carregar_placas(arquivo_ids_placas: Path = ARQUIVO_IDS_PLACAS) -> dict[int, str]:
    """Carrega a relação entre IDs das AprilTags e nomes das placas.

    Parâmetros:
    - arquivo_ids_placas: caminho do arquivo JSON com o mapeamento ID -> placa.

    Retorna:
    - Dicionário em que a chave é o ID da AprilTag e o valor é o nome da placa.
    """
    if not arquivo_ids_placas.exists():
        raise FileNotFoundError(f"Arquivo {arquivo_ids_placas} não encontrado.")

    with arquivo_ids_placas.open("r", encoding="utf-8") as arquivo:
        placas = json.load(arquivo)

    return {int(id_placa): placa for id_placa, placa in placas.items()}


def criar_detector_apriltag() -> DetectorAprilTag:
    """Cria o detector de AprilTags usando a família 36h11.

    Retorna:
    - Detector ArUco/AprilTag configurado para identificar tags 36h11.
    """
    dicionario = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_APRILTAG_36h11)
    parametros = cv2.aruco.DetectorParameters()
    return cv2.aruco.ArucoDetector(dicionario, parametros)


def estimar_distancia_m(
    cantos_tag: np.ndarray,
    calibracao: CalibracaoCamera,
) -> float | None:
    """Estima a distância da AprilTag até a câmera em metros.

    Parâmetros:
    - cantos_tag: matriz com os quatro cantos detectados da AprilTag.
    - calibracao: dados de calibração da câmera.

    Retorna:
    - Distância estimada em metros, ou `None` se o tamanho detectado for inválido.
    """
    tamanho_tag_px = calcular_tamanho_tag_px(cantos_tag)

    if tamanho_tag_px <= 0:
        return None

    return (calibracao.tag_size_m * calibracao.focal_length_px) / tamanho_tag_px


def detectar_tags(
    frame: np.ndarray,
    detector: DetectorAprilTag,
    calibracao: CalibracaoCamera,
    placas: dict[int, str],
) -> list[DeteccaoPlaca]:
    """Detecta AprilTags no frame e retorna as placas identificadas.

    Parâmetros:
    - frame: imagem capturada pela câmera no formato BGR do OpenCV.
    - detector: detector AprilTag criado por `criar_detector_apriltag`.
    - calibracao: dados de calibração usados para calcular distância.
    - placas: dicionário com a relação entre ID da tag e nome da placa.

    Retorna:
    - Lista de detecções ordenada pela menor distância até a câmera.
    """
    cinza = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    cantos, ids, _ = detector.detectMarkers(cinza)

    if ids is None:
        return []

    deteccoes = []

    for cantos_tag, id_tag in zip(cantos, ids.flatten()):
        id_tag_int = int(id_tag)
        distancia_m = estimar_distancia_m(cantos_tag, calibracao)

        if distancia_m is None:
            continue

        deteccoes.append(
            DeteccaoPlaca(
                id=id_tag_int,
                placa=placas.get(id_tag_int, "Desconhecida"),
                distancia_m=distancia_m,
            )
        )

    deteccoes_ordenadas = sorted(
        deteccoes,
        key=lambda deteccao: deteccao.distancia_m,
    )
    return deteccoes_ordenadas
