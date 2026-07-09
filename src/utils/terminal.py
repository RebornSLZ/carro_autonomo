from utils.signs import DeteccaoPlaca


CABECALHO_TABELA_PLACAS = f"{'ID':<6}{'PLACA':<16}{'DISTÂNCIA (METROS)':>18}"


def imprimir_tabela_placas(deteccoes: list[DeteccaoPlaca]) -> None:
    """Imprime no terminal uma tabela com as placas detectadas.

    Parâmetros:
    - deteccoes: lista de placas detectadas, com ID, nome da placa e distância.
    """
    print(CABECALHO_TABELA_PLACAS)
    print("-" * len(CABECALHO_TABELA_PLACAS))

    for deteccao in deteccoes:
        print(f"{deteccao.id:<6}{deteccao.placa:<16}{deteccao.distancia_m:>18.2f}")
