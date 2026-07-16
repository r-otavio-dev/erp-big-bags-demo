from pathlib import Path
from datetime import datetime
from copy import copy
import pandas as pd


def gerar_relatorio(resultados, pasta="resultados"):
    destino = Path(pasta); destino.mkdir(parents=True, exist_ok=True)
    arquivo = destino / f"relatorio_estornos_{datetime.now():%Y%m%d_%H%M%S}.xlsx"
    df = pd.DataFrame(resultados)
    with pd.ExcelWriter(arquivo, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="Resultados")
        ws = writer.book["Resultados"]
        ws.freeze_panes = "A2"
        ws.auto_filter.ref = ws.dimensions
        for cell in ws[1]:
            font = copy(cell.font); font.bold = True; font.color = "FFFFFF"; cell.font = font
            cell.fill = __import__("openpyxl").styles.PatternFill("solid", fgColor="17395C")
        widths = {"A": 16, "B": 20, "C": 28, "D": 38, "E": 20, "F": 12,
                  "G": 24, "H": 48, "I": 22, "J": 22, "K": 18, "L": 12}
        for col, width in widths.items():
            ws.column_dimensions[col].width = width
        headers = {cell.value: cell.column for cell in ws[1]}
        estornado_col = headers.get("estornado")
        if estornado_col:
            for row in range(2, ws.max_row + 1):
                cell = ws.cell(row, estornado_col)
                cor = "C6EFCE" if cell.value == "SIM" else "FFC7CE"
                cell.fill = __import__("openpyxl").styles.PatternFill("solid", fgColor=cor)
                font = copy(cell.font); font.bold = True; cell.font = font
    return arquivo
