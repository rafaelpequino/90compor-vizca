import os

from dotenv import load_dotenv
from playwright.sync_api import sync_playwright


LOGIN_URL = "https://orcamento.90compor.com.br/Login"


def main() -> None:
	load_dotenv()
	usuario = os.getenv("COMPOR_USUARIO", "").strip()
	senha = os.getenv("COMPOR_SENHA", "").strip()

	if not usuario or not senha:
		raise ValueError(
			"Defina COMPOR_USUARIO e COMPOR_SENHA no arquivo .env antes de executar."
		)

	with sync_playwright() as playwright:
		browser = playwright.chromium.launch(headless=False)
		page = browser.new_page(viewport={"width": 1400, "height": 900})

		page.goto(LOGIN_URL, wait_until="domcontentloaded")
		page.locator("input#Login").fill(usuario)
		page.locator("input#Senha").fill(senha)
		page.locator("a#entrar").click()

		input("Login enviado. Pressione Enter para fechar o navegador...")
		browser.close()


if __name__ == "__main__":
	main()
