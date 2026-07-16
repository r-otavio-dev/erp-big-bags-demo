from pathlib import Path
import pandas as pd

COLUNAS = ["codigo", "motivo", "observacao", "responsavel"]


def ler_planilha(caminho):
    path = Path(caminho)
    if path.suffix.lower() != ".xlsx" or not path.is_file():
        raise ValueError("Informe um arquivo .xlsx existente.")
    df = pd.read_excel(path, dtype=str).fillna("")
    faltantes = [c for c in COLUNAS if c not in df.columns]
    if faltantes:
        raise ValueError(f"Colunas obrigatórias ausentes: {', '.join(faltantes)}")
    return df[COLUNAS].apply(lambda col: col.str.strip()).to_dict("records")

