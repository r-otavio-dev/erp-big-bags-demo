# ERP Demo – Controle de Big Bags

Prova de conceito totalmente local e fictícia para demonstrar estornos manuais, importação em lote e automação por navegador. Não acessa nem representa qualquer ERP real.

## Requisitos e instalação (Windows PowerShell)

- Python 3.12 (compatível com versões recentes do Python 3)
- Microsoft Edge/Chromium instalado pelo Playwright

```powershell
cd erp-big-bags-demo
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
playwright install chromium
python scripts\criar_dados_exemplo.py
```

Se o PowerShell bloquear a ativação, execute apenas na sessão atual: `Set-ExecutionPolicy -Scope Process Bypass`.

## Execução

Terminal 1:

```powershell
.venv\Scripts\Activate.ps1
python app.py
```

Acesse `http://127.0.0.1:5000` e use `admin` / `admin123`. Também é possível executar `run_app.bat`.

Terminal 2, com o navegador visível:

```powershell
.venv\Scripts\Activate.ps1
python -m automation.executar_automacao --arquivo dados\estornos_exemplo.xlsx --url http://127.0.0.1:5000 --visivel --tentativas 2
```

Em segundo plano:

```powershell
python -m automation.executar_automacao --arquivo dados\estornos_exemplo.xlsx --headless --timeout 15000 --tentativas 2
```

`run_automation.bat` executa a demonstração visível. O relatório vai para `resultados/`, o log para `logs/` e capturas de erros inesperados para `screenshots/`. A automação recusa qualquer host diferente de `localhost`/`127.0.0.1` e qualquer porta explícita diferente de 5000.

## Componentes

- `app/models.py`: entidades SQLite/SQLAlchemy de big bags, estornos e auditoria.
- `app/services.py`: regras transacionais. A atualização condicional `DISPONIVEL → ESTORNADO` impede duas confirmações concorrentes.
- `app/routes/`: login, dashboard, consulta, estorno, histórico/exportação e importação.
- `automation/`: validação de URL local, leitura Excel, operação Playwright e relatório.
- `dados/estornos_exemplo.xlsx`: casos válidos, inexistente, estornado, bloqueado, motivo vazio e duplicado.
- `tests/`: regras de negócio, auditoria, planilha, relatório e proteção de URL.

O banco `instance/erp_demo.db` e os 30 big bags fictícios são criados automaticamente na primeira inicialização.

## Testes

```powershell
.venv\Scripts\Activate.ps1
pytest
```

Os testes usam um banco SQLite temporário e não alteram o banco de demonstração.

## Importação manual

No menu **Importação Excel**, envie um `.xlsx` com `codigo`, `motivo`, `observacao` e `responsavel`. O sistema valida as colunas, mostra a prévia, processa cada linha independentemente e oferece o relatório final.

## Como apresentar esta prova de conceito

1. Explique e simule o processo manual atual.
2. Abra `dados/estornos_exemplo.xlsx` e destaque os casos de teste.
3. Entre no ERP simulado e apresente o dashboard e a consulta.
4. Faça um estorno manual e mostre confirmação, histórico e auditoria.
5. Inicie a automação em outro terminal com `--visivel`.
6. Mostre os estornos acontecendo no navegador e a continuidade após erros esperados.
7. Abra o relatório gerado em `resultados/`.
8. Mostre o log em `logs/`, o histórico exportável e os registros de auditoria no banco.
9. Compare o fluxo manual e o automatizado.
10. Reforce que qualquer integração real exige autorização, análise técnica, segurança e validação formal da equipe responsável pelo ERP.

| Critério | Processo manual | Processo automatizado (estimado) |
|---|---|---|
| Tempo por item | 30–90 segundos | 3–10 segundos |
| Erro de digitação | Médio | Baixo, conforme a planilha |
| Rastreabilidade | Anotações dispersas | Log, relatório e auditoria |
| Lote | Repetição manual | Processamento sequencial automático |

Os valores são estimativas ilustrativas. Devem ser ajustados após medição real, em ambiente autorizado e controlado.

## Limites de segurança

O projeto não contém conexão, credenciais, identidade visual, engenharia reversa ou código de sistemas reais. Opera apenas no servidor Flask local em `127.0.0.1:5000`; Bootstrap é carregado por CDN apenas para estilo e pode ser substituído por arquivo local em ambientes sem internet.

