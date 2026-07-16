from playwright.sync_api import sync_playwright


class ERPBrowserClient:
    def __init__(self, url, headless=True, timeout=15000):
        self.url, self.headless, self.timeout = url, headless, timeout

    def __enter__(self):
        self.pw = sync_playwright().start(); self.browser = self.pw.chromium.launch(headless=self.headless)
        self.page = self.browser.new_page(); self.page.set_default_timeout(self.timeout)
        self.page.goto(f"{self.url}/login"); self.page.locator("#login-usuario").fill("admin")
        self.page.locator("#login-senha").fill("admin123"); self.page.locator("#btn-login").click()
        self.page.wait_for_url(f"{self.url}/"); return self

    def __exit__(self, *_):
        self.browser.close(); self.pw.stop()

    def estornar(self, row):
        self.page.goto(f"{self.url}/estornos/novo")
        self.page.locator("#codigo-big-bag").fill(row["codigo"]); self.page.locator("#btn-consultar").click()
        self.page.wait_for_load_state("domcontentloaded")
        if self.page.locator("#dados-big-bag").count() == 0:
            return "NAO_ENCONTRADO", "Big bag não encontrado."
        if not row["motivo"]:
            return "DADOS_INVALIDOS", "Motivo obrigatório ou inválido."
        self.page.locator("#motivo-estorno").select_option(label=row["motivo"])
        self.page.locator("#observacao-estorno").fill(row["observacao"])
        self.page.locator("#responsavel-estorno").fill(row["responsavel"])
        self.page.get_by_role("button", name="Prosseguir").click()
        self.page.locator("#confirmModal").wait_for(state="visible")
        self.page.locator("#btn-confirmar-estorno").click()
        msg = self.page.locator("#mensagem-resultado"); msg.wait_for(state="visible")
        return msg.get_attribute("data-status") or "ERRO_INESPERADO", msg.inner_text().strip()

