import os

from dotenv import load_dotenv
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError
from playwright.sync_api import sync_playwright


LOGIN_URL = "https://orcamento.90compor.com.br/Login"


def main() -> None:
	try:
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

			try:
				print("[1/5] Abrindo página de login...")
				page.goto(LOGIN_URL, wait_until="domcontentloaded")
				page.wait_for_timeout(2_000)

				print("[2/5] Aguardando formulário de login...")
				login = page.locator("input#Login:visible")
				senha_input = page.locator("input#Senha:visible")
				entrar = page.locator("a#entrar")
				login.wait_for(state="visible")
				senha_input.wait_for(state="visible")
				entrar.wait_for(state="visible")

				print("[3/5] Preenchendo credenciais e enviando login...")
				login.fill(usuario)
				senha_input.fill(senha)
				entrar.click()

				print("[4/6] Verificando confirmação de sessão...")
				confirmar = page.get_by_role("button", name="Confirmar", exact=True)
				try:
					confirmar.wait_for(state="visible", timeout=2_000)
					print("[4/6] Confirmação exibida. Confirmando...")
					confirmar.click()
				except PlaywrightTimeoutError:
					print("[4/6] Nenhuma confirmação de sessão exibida.")

				print("[5/6] Aguardando tela inicial...")
				orcamento = page.locator("a[href='/Orcamento']:visible")
				orcamento.wait_for(state="visible")

				print("[6/6] Abrindo Orçamento...")
				orcamento.click()
				print("Orçamento aberto.")
			except Exception as error:
				print(f"Erro durante o login: {error}")
			finally:
				input("Pressione Enter para finalizar...")
				browser.close()
	except Exception as error:
		print(f"Erro durante o login: {error}")
		input("Pressione Enter para finalizar...")


if __name__ == "__main__":
	main()
