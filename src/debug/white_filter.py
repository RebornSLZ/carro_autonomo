"""

Controles:
  Q          — sair
  S          — salvar frame atual
  trackbars  — ajustar range do branco em tempo real

  *Adicionar mais comandos pra controle do carro*
"""

from pathlib import Path
import sys

import cv2
import numpy as np
import time

sys.path.append(str(Path(__file__).resolve().parents[1]))

from utils import motores


def criar_trackbars(janela: str) -> None:
    cv2.createTrackbar("S max",  janela,  40,  255, lambda x: None)
    cv2.createTrackbar("V min",  janela, 180,  255, lambda x: None)


def ler_trackbars(janela: str) -> tuple[int, int]:
    s_max = cv2.getTrackbarPos("S max", janela)
    v_min = cv2.getTrackbarPos("V min", janela)
    return s_max, v_min


def filtrar_branco(frame: np.ndarray, s_max: int, v_min: int) -> np.ndarray:
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)


    lower = np.array([0,   0,     v_min], dtype=np.uint8)
    upper = np.array([180, s_max, 255],   dtype=np.uint8)

    mask = cv2.inRange(hsv, lower, upper)

    # Limpar ruído pequeno
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN,  kernel)
    mask = cv2.morphologyEx(mask, cv2.MORPH_DILATE, kernel)

    resultado = cv2.bitwise_and(frame, frame, mask=mask)

    h, w = resultado.shape[:2]
    x1, x2, xm = int(w * 0.30), int(w * 0.70), w // 2

    # Overlay colorido com 40% de opacidade nas metades do meio
    overlay = frame.copy()
    cv2.rectangle(overlay, (x1, 0), (xm, h), (0, 0, 255), -1)   # vermelho — esquerda
    cv2.rectangle(overlay, (xm, 0), (x2, h), (255, 0, 0), -1)   # azul    — direito
    cv2.addWeighted(overlay, 0.4, frame, 0.6, 0, frame)

    # Linhas divisórias
    cor_linha = (0, 255, 0)
    espessura = 2
    for img in (resultado, frame):
        cv2.line(img, (x1, 0), (x1, h), cor_linha, espessura)
        cv2.line(img, (x2, 0), (x2, h), cor_linha, espessura)
        cv2.line(img, (xm, 0), (xm, h), cor_linha, espessura)

    # Verifica se tem branco nas divisões coloridas
    toca_vermelho = cv2.countNonZero(mask[:, x1:xm]) > 0
    toca_azul     = cv2.countNonZero(mask[:, xm:x2]) > 0

    return mask, resultado, toca_vermelho, toca_azul


def main() -> None:
    motores.iniciar()

    cap = cv2.VideoCapture(0, cv2.CAP_MSMF)
    if not cap.isOpened():
        cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        motores.encerrar()
        raise RuntimeError("Não foi possível abrir a câmera.")

    janela = "Filtro Branco"
    cv2.namedWindow(janela)
    criar_trackbars(janela)

    print(" Q  para sair  |  S  para salvar")

    while True:
        ok, frame = cap.read()
        if not ok:
            print("Falha ao capturar frame.")
            break

        s_max, v_min = ler_trackbars(janela)
        mask, resultado, toca_vermelho, toca_azul = filtrar_branco(frame, s_max, v_min)

        agora = time.time()

        if toca_vermelho:
            motores.servo_direita()
        elif toca_azul:
            motores.servo_esquerda()
        else:
            motores.servo_centro()

        # Empilha original | máscara | resultado lado a lado
        mask_bgr = cv2.cvtColor(mask, cv2.COLOR_GRAY2BGR)
        exibir = np.hstack([frame, mask_bgr, resultado])
        exibir = cv2.resize(exibir, (0, 0), fx=0.6, fy=0.6)

        cv2.imshow(janela, exibir)

        tecla = cv2.waitKey(1) & 0xFF
        if tecla == ord("q"):
            break
        elif tecla == ord("s"):
            cv2.imwrite("white_filter.png", resultado)
            print("Frame salvo: white_filter.png")

    cap.release()
    cv2.destroyAllWindows()
    motores.encerrar()


if __name__ == "__main__":
    main()
