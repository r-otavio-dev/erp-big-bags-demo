# ERP Demo – Controle de Big Bags

Prova de conceito totalmente local e fictícia para demonstrar estornos manuais, importação em lote e automação por navegador. Não acessa nem representa qualquer ERP real.

## Contexto de aprendizado

O projeto nasceu da observação de um tipo de processo industrial com o qual tive
contato no trabalho. A implementação foi feita com bastante apoio de ferramentas
de IA e funciona como laboratório de estudo, não como demonstração de domínio
avançado de Flask, SQLAlchemy ou Playwright.

Estou usando o repositório para estudar como uma regra de negócio pode ser
representada em uma aplicação local, como registrar histórico e como automatizar
um fluxo de navegador de forma controlada. Antes de apresentar o projeto em uma
entrevista, minha meta é conseguir explicar e modificar os principais caminhos
sem depender de código gerado.

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

## Roteiro de estudo do projeto

1. Explicar o modelo de dados de big bags, estornos e auditoria.
2. Percorrer a regra `processar_estorno` e justificar cada validação.
3. Executar manualmente casos de sucesso, item inexistente e item bloqueado.
4. Explicar como a planilha é validada antes da automação.
5. Acompanhar uma execução do Playwright e localizar logs e relatórios.
6. Alterar uma regra simples e adicionar um teste correspondente.
7. Reforçar que qualquer integração real exigiria autorização, análise técnica e validação da equipe responsável pelo ERP.

## Limites de segurança

O projeto não contém conexão, credenciais, identidade visual, engenharia reversa ou código de sistemas reais. Opera apenas no servidor Flask local em `127.0.0.1:5000`; Bootstrap é carregado por CDN apenas para estilo e pode ser substituído por arquivo local em ambientes sem internet.

