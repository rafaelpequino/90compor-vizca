# Exportador 90 Compor

Automação que acessa o 90 Compor, seleciona a base personalizada VIZCA PRÓPRIO, exporta todas as bases principais e descompacta os arquivos ZIP baixados.

## Execução local

Requisitos: Python 3.10 ou superior.

```powershell
py -m pip install playwright python-dotenv
py -m playwright install chromium
```

Crie o arquivo `.env` a partir de `.env.example` e informe as credenciais:

```env
COMPOR_USUARIO=seu_usuario
COMPOR_SENHA=sua_senha
```

Execute:

```powershell
py export.py
```

O programa solicita a pasta de destino. Bases com ZIP já existente nessa pasta são ignoradas, permitindo retomar uma execução interrompida. Ao final, os ZIPs são descompactados em pastas com o mesmo nome.

## Gerar o executável

Instale o PyInstaller:

```powershell
py -m pip install pyinstaller
```

Gere um executável único com o Chromium do Playwright incluído:

```powershell
py -m PyInstaller --onefile --console --clean --noconfirm --name "90compor-export" --add-data "C:\Users\rafae\AppData\Local\ms-playwright;ms-playwright" export.py
```

O executável é criado em `dist\90compor-export.exe`.

Em outro computador, basta executar o arquivo `.exe`. Ele solicita usuário, senha e a pasta de destino; não requer Python, Playwright ou navegador instalados.
