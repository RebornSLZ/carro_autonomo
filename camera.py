"""
Camera capture - abre a câmera do celular (ou webcam) para visão computacional.

Como conectar o celular via USB (Android):
  1. Instale o app "DroidCam" no celular (Play Store) e no PC (droidcam.app)
  2. Habilite "Depuração USB" nas opções de desenvolvedor do celular
  3. Conecte via USB e abra o DroidCam - ele aparece como câmera virtual (índice 1 ou 2)

  Alternativa sem app extra: use "scrcpy" + obs-virtual-cam, ou conecte via Wi-Fi
  com o app "IP Webcam" e passe a URL do stream no lugar do índice da câmera.
"""

import cv2
import sys


def encontrar_cameras(max_idx: int = 5) -> list[int]:
    """Detecta quais índices de câmera estão disponíveis (testa DSHOW e padrão)."""
    disponiveis = []
    for i in range(max_idx):
        # tenta DSHOW primeiro (necessário para DroidCam no Windows)
        cap = cv2.VideoCapture(i, cv2.CAP_DSHOW)
        if not cap.isOpened():
            cap = cv2.VideoCapture(i)
        if cap.isOpened():
            disponiveis.append(i)
            cap.release()
    return disponiveis


def abrir_camera(indice: int = 0) -> cv2.VideoCapture:
    nomes = {cv2.CAP_DSHOW: "DSHOW", cv2.CAP_MSMF: "MSMF", cv2.CAP_ANY: "ANY"}
    for backend in (cv2.CAP_DSHOW, cv2.CAP_MSMF, cv2.CAP_ANY):
        cap = cv2.VideoCapture(indice, backend)
        if cap.isOpened():
            ok, _ = cap.read()
            if ok:
                print(f"Backend: {nomes[backend]}")
                break
            cap.release()
    else:
        raise RuntimeError(f"Não foi possível abrir a câmera de índice {indice}.")

    w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = cap.get(cv2.CAP_PROP_FPS) or 30
    print(f"Câmera {indice} aberta  |  {w}x{h}  |  {fps:.0f} fps")
    return cap


def loop_captura(cap: cv2.VideoCapture) -> None:
    """Loop principal de captura e exibição."""
    print("Pressione  Q  para sair  |  S  para salvar um frame")

    while True:
        ok, frame = cap.read()
        if not ok:
            print("Falha ao capturar frame.")
            break

        # ── coloque aqui o seu processamento de visão computacional ──
        # ex.: frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        cv2.imshow("Camera", frame)

        tecla = cv2.waitKey(1) & 0xFF
        if tecla == ord("q"):
            break
        elif tecla == ord("s"):
            nome = "frame_capturado.png"
            cv2.imwrite(nome, frame)
            print(f"Frame salvo em {nome}")


def main() -> None:
    cameras = encontrar_cameras()
    if not cameras:
        print("Nenhuma câmera encontrada.")
        sys.exit(1)

    print(f"Câmeras disponíveis: {cameras}")

    # Usa a câmera especificada na linha de comando, ou o celular (índice 1 via DroidCam Wi-Fi)
    indice = int(sys.argv[1]) if len(sys.argv) > 1 else (1 if 1 in cameras else cameras[0])

    cap = abrir_camera(indice)
    try:
        loop_captura(cap)
    finally:
        cap.release()
        cv2.destroyAllWindows()
        print("Câmera liberada.")


if __name__ == "__main__":
    main()
