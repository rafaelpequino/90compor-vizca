import os
import sys
from getpass import getpass
from pathlib import Path
from zipfile import ZipFile

from dotenv import load_dotenv
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError
from playwright.sync_api import sync_playwright


LOGIN_URL = "https://orcamento.90compor.com.br/Login"
BASE_PERSONALIZADA = "3899392"


def main() -> None:
	try:
		if getattr(sys, "frozen", False):
			os.environ["PLAYWRIGHT_BROWSERS_PATH"] = str(
				Path(sys._MEIPASS) / "ms-playwright"
			)

		load_dotenv()
		usuario = os.getenv("COMPOR_USUARIO", "").strip()
		senha = os.getenv("COMPOR_SENHA", "").strip()

		if not usuario:
			usuario = input("Usuário 90 Compor: ").strip()
		if not senha:
			senha = getpass("Senha 90 Compor: ")
		if not usuario or not senha:
			raise ValueError("Usuário e senha são obrigatórios.")

		caminho_destino = input("Cole o caminho onde os arquivos serão salvos: ").strip()
		if not caminho_destino:
			raise ValueError("Informe um caminho válido para salvar os arquivos.")
		pasta_exportacoes = Path(caminho_destino).expanduser()
		pasta_exportacoes.mkdir(parents=True, exist_ok=True)
		print(f"Arquivos serão salvos em: {pasta_exportacoes.resolve()}")

		with sync_playwright() as playwright:
			browser = playwright.chromium.launch(headless=False)
			page = browser.new_page(viewport={"width": 1400, "height": 900})
			arquivos_baixados = []

			try:
				print("[1/12] Abrindo página de login...")
				page.goto(LOGIN_URL, wait_until="domcontentloaded")
				page.wait_for_timeout(2_000)

				print("[2/12] Aguardando formulário de login...")
				login = page.locator("input#Login:visible")
				senha_input = page.locator("input#Senha:visible")
				entrar = page.locator("a#entrar")
				login.wait_for(state="visible")
				senha_input.wait_for(state="visible")
				entrar.wait_for(state="visible")

				print("[3/12] Preenchendo credenciais e enviando login...")
				login.fill(usuario)
				senha_input.fill(senha)
				entrar.click()

				print("[4/12] Verificando confirmação de sessão...")
				confirmar = page.get_by_role("button", name="Confirmar", exact=True)
				try:
					confirmar.wait_for(state="visible", timeout=2_000)
					print("[4/12] Confirmação exibida. Confirmando...")
					confirmar.click()
				except PlaywrightTimeoutError:
					print("[4/12] Nenhuma confirmação de sessão exibida.")

				print("[5/12] Aguardando tela inicial...")
				orcamento = page.locator("a[href='/Orcamento']:visible")
				orcamento.wait_for(state="visible")

				print("[6/12] Abrindo Orçamento...")
				with page.expect_navigation():
					orcamento.click()

				print("[7/12] Expandindo o menu Acessar...")
				acessar = page.locator(
					"a.hrefMenu:has(span.title:text-is('Acessar'))"
				)
				acessar.wait_for(state="visible")
				acessar.click()
				submenu = acessar.locator(
					"xpath=following-sibling::ul[contains(@class, 'sub-menu')]"
				)
				submenu.wait_for(state="visible")

				print("[8/12] Abrindo Base de dados personalizada...")
				base_personalizada = page.locator(
					"a[href='/Orcamento/SelecaoBasePersonalizada/Sair']:visible"
				)
				base_personalizada.wait_for(state="visible")
				with page.expect_navigation():
					base_personalizada.click()

				print("[9/12] Selecionando VIZCA PRÓPRIO...")
				seletor_base = page.locator("select#IdBaseDados:visible")
				seletor_base.wait_for(state="visible")
				seletor_base.select_option(BASE_PERSONALIZADA)
				print("VIZCA PRÓPRIO selecionada.")
				page.wait_for_timeout(1_000)

				print("[10/12] Abrindo o sidebar...")
				menu_toggler = page.locator("a.menu-toggler.sidebar-toggler:visible")
				menu_toggler.wait_for(state="visible")
				menu_toggler.click()
				page.wait_for_timeout(500)

				print("[11/12] Expandindo Importar / Exportar...")
				importar_exportar = page.locator("a.hrefMenu").filter(
					has_text="Importar / Exportar"
				)
				importar_exportar.wait_for(state="visible")
				importar_exportar.click()
				importar_exportar.locator(
					"xpath=following-sibling::ul[contains(@class, 'sub-menu')]"
				).wait_for(state="visible")

				print("[12/12] Abrindo Base de Dados Órgão...")
				base_orgao = page.locator(
					"a[href='/Orcamento/BaseDeDados/Exportar']:visible"
				)
				base_orgao.wait_for(state="visible")
				with page.expect_navigation():
					base_orgao.click()
				print("Base de Dados Órgão aberta.")

				principal = page.locator("select#OrgaoPrincipal:visible")
				data_base = page.locator("select#MesAnoOrgaoPrincipal:visible")
				uf = page.locator("select#IdEstadoOrgaoPrincipal:visible")
				botao_exportar = page.locator("#btnExportar:visible")
				principal.wait_for(state="visible")

				bases = principal.locator("option").evaluate_all(
					"options => options.filter(option => option.value).map(option => ({"
					"value: option.value, text: option.textContent.trim()}))"
				)
				print(f"{len(bases)} bases principais encontradas.")

				for indice, base in enumerate(bases, start=1):
					arquivos_existentes = list(
						pasta_exportacoes.glob(f"{base['value']}_*.zip")
					)
					if arquivos_existentes:
						print(
							f"[{indice}/{len(bases)}] {base['text']} já foi baixada como "
							f"'{arquivos_existentes[0].stem}'. Pulando."
						)
						continue

					print(
						f"[{indice}/{len(bases)}] Selecionando base principal: {base['text']}..."
					)
					while True:
						try:
							principal.select_option(base["value"])

							data_base.wait_for(state="visible")
							uf.wait_for(state="visible")
							uf.locator("option[value]:not([value=''])").first.wait_for(
								state="attached", timeout=10_000
							)
							data_selecionada = data_base.input_value()
							opcoes_uf = uf.locator("option").evaluate_all(
								"options => options.filter(option => option.value).map(option => ({"
								"value: option.value, text: option.textContent.trim()}))"
							)
							if not opcoes_uf:
								raise ValueError(f"Nenhuma UF disponível para {base['text']}.")

							uf_escolhida = next(
								(opcao for opcao in opcoes_uf if opcao["text"] == "São Paulo"),
								opcoes_uf[0],
							)
							uf.select_option(uf_escolhida["value"])
							print(
								f"    Data Base: {data_selecionada}; UF: {uf_escolhida['text']}."
							)

							botao_exportar.wait_for(state="visible")
							print("    Exportando arquivo ZIP...")
							with page.expect_download(timeout=0) as download_info:
								botao_exportar.click()
							download = download_info.value
							caminho_arquivo = pasta_exportacoes / download.suggested_filename
							download.save_as(caminho_arquivo)
							arquivos_baixados.append(caminho_arquivo)
							print(f"    Arquivo salvo: {caminho_arquivo}")
							break
						except Exception as error:
							print(f"    Erro em {base['text']}: {error}")
							input("    Corrija o necessário e pressione Enter para tentar novamente... ")

				print("Descompactando os arquivos baixados...")
				for arquivo_zip in pasta_exportacoes.glob("*.zip"):
					pasta_destino = pasta_exportacoes / arquivo_zip.stem
					pasta_destino.mkdir(exist_ok=True)
					with ZipFile(arquivo_zip) as arquivo_compactado:
						arquivo_compactado.extractall(pasta_destino)
					arquivo_zip.unlink()
					print(f"    Descompactado: {pasta_destino}")
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
