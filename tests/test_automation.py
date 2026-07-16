import pandas as pd
import pytest
from automation.excel_reader import ler_planilha
from automation.report_generator import gerar_relatorio
from automation.settings import validar_url_local

def test_excel_e_colunas(tmp_path):
    p=tmp_path/'ok.xlsx'; pd.DataFrame([{"codigo":"BB-1","motivo":"Outro","observacao":"","responsavel":"A"}]).to_excel(p,index=False)
    assert ler_planilha(p)[0]["codigo"]=="BB-1"
    bad=tmp_path/'bad.xlsx'; pd.DataFrame([{"codigo":"x"}]).to_excel(bad,index=False)
    with pytest.raises(ValueError, match="ausentes"): ler_planilha(bad)

def test_relatorio(tmp_path):
    p=gerar_relatorio([{"codigo":"BB-1","estornado":"SIM","status_processamento":"SUCESSO"}],tmp_path)
    df = pd.read_excel(p)
    assert p.exists() and df.iloc[0]["codigo"]=="BB-1" and df.iloc[0]["estornado"]=="SIM"

@pytest.mark.parametrize("url",["https://empresa.local","http://192.168.1.2:5000","http://127.0.0.1:8000"])
def test_bloqueia_url_externa(url):
    with pytest.raises(ValueError): validar_url_local(url)

def test_aceita_localhost(): assert validar_url_local("http://127.0.0.1:5000")=="http://127.0.0.1:5000"
