# Plataforma (SQLite) — Inventário (Tema Light) — v3

- Inventário com importador **XLSX** adaptado à planilha "Tech Stack Equipment Inventory.xlsx".
- **Split inteligente** do campo Owner (ex.: "Renato Abreu / João Obregon").
- **Criação automática** de **Users** e **Clients** ausentes.
- Cadastros: Clientes, Concessionários, Projetos, Status.
- Tema **claro** (sem dark mode), Tailwind + daisyUI.

## Rodar localmente
```bash
python -m venv .venv
.venv\Scripts\activate  # Windows | source .venv/bin/activate  # Linux/macOS
pip install -r requirements.txt
copy .env.example .env       # Windows | cp .env.example .env
set FLASK_APP=manage.py      # PowerShell: $Env:FLASK_APP="manage.py"
flask db init
flask db migrate -m "Initial tables"
flask db upgrade
flask run
```

## Importar Status (XLSX)
- Rota: **/status-equipamentos/importar**
- Lê a aba **Sum** com a coluna **Status**.

## Importar Inventário (XLSX)
- Rota: **/equipamentos/importar**
- Colunas aceitas (case-insensitive): `Item`, `PN`, `Model Number`/`Model`, `SN`/`Serial Number`, `Location`, `Machine Installed`, `Status`, `Project`, `Owner`, `Current Responsible`/`Current Reponsible`, `Obs`, `Imagem de Referência`.
- **Password é ignorada**.
- **Owner split**: se múltiplos nomes em Owner e Responsible vazio, usa o 1º como Owner e o 2º como Responsible.
- **Auto-criação**: Users (placeholder `@autogen.local`) e Clients (tipo PJ, endereço padrão) quando não existirem.
- **Deduplicação**: prioriza `SN`; senão, `PN + Item`.
