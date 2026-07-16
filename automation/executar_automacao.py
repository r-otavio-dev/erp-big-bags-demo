import argparse
import logging
from datetime import datetime
from pathlib import Path
from .settings import validar_url_local
from .excel_reader import ler_planilha
from .browser_client import ERPBrowserClient
from .report_generator import gerar_relatorio


def parser():
    p = argparse.ArgumentParser(description="Automação exclusivamente local do ERP Demo")
    p.add_argument("--arquivo", required=True); p.add_argument("--url", default="http://127.0.0.1:5000")
    mode = p.add_mutually_exclusive_group(); mode.add_argument("--visivel", action="store_true"); mode.add_argument("--headless", action="store_true")
    p.add_argument("--timeout", type=int, default=15000); p.add_argument("--tentativas", type=int, default=1)
    return p


def main(argv=None):
    args = parser().parse_args(argv); url = validar_url_local(args.url); rows = ler_planilha(args.arquivo)
    Path("logs").mkdir(exist_ok=True); Path("screenshots").mkdir(exist_ok=True)
    log_file = Path("logs") / f"automacao_{datetime.now():%Y%m%d_%H%M%S}.log"
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s", handlers=[logging.FileHandler(log_file, encoding="utf-8"), logging.StreamHandler()])
    resultados = []
    with ERPBrowserClient(url, headless=not args.visivel, timeout=args.timeout) as client:
        for n, row in enumerate(rows, start=2):
            inicio = datetime.now(); status = "ERRO_INESPERADO"; mensagem = ""; tentativa = 0
            for tentativa in range(1, max(1, args.tentativas) + 1):
                try:
                    status, mensagem = client.estornar(row); break
                except Exception as exc:
                    mensagem = str(exc); logging.exception("Erro na linha %s", n)
                    client.page.screenshot(path=str(Path("screenshots") / f"erro_linha_{n}_{tentativa}.png"), full_page=True)
            fim = datetime.now(); logging.info("Linha %s %s: %s", n, row["codigo"], status)
            resultados.append({"linha_planilha": n, "codigo": row["codigo"], "motivo": row["motivo"],
                "observacao": row["observacao"], "responsavel": row["responsavel"],
                "estornado": "SIM" if status == "SUCESSO" else "NÃO",
                "status_processamento": status, "mensagem": mensagem,
                "data_hora_inicio": inicio, "data_hora_fim": fim,
                "duracao_segundos": round((fim-inicio).total_seconds(), 3), "tentativa": tentativa})
    arquivo = gerar_relatorio(resultados); print(f"Relatório: {arquivo.resolve()}"); print(f"Log: {log_file.resolve()}")


if __name__ == "__main__": main()
