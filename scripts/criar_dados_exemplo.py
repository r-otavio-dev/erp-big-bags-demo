from pathlib import Path
import pandas as pd

rows = [
 {"codigo":"BB-2026-0001","motivo":"Material danificado","observacao":"Encontrado rasgo na lateral","responsavel":"Rodrigo"},
 {"codigo":"BB-2026-0002","motivo":"Problema de qualidade","observacao":"Material fora do padrão","responsavel":"Rodrigo"},
 {"codigo":"BB-2026-9999","motivo":"Outro","observacao":"Código usado para testar erro","responsavel":"Rodrigo"},
 {"codigo":"BB-2026-0005","motivo":"Outro","observacao":"Teste já estornado","responsavel":"Rodrigo"},
 {"codigo":"BB-2026-0008","motivo":"Contaminado","observacao":"Teste bloqueado","responsavel":"Rodrigo"},
 {"codigo":"BB-2026-0003","motivo":"","observacao":"Teste motivo vazio","responsavel":"Rodrigo"},
 {"codigo":"BB-2026-0001","motivo":"Rasgado","observacao":"Teste duplicado","responsavel":"Rodrigo"},
]
dest = Path(__file__).resolve().parents[1] / "dados" / "estornos_exemplo.xlsx"
dest.parent.mkdir(exist_ok=True); pd.DataFrame(rows).to_excel(dest, index=False); print(dest)

