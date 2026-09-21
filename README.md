# Pioneiro Pro Mobile

Aplicativo mobile do Pioneiro Pro desenvolvido em Python com Flet, com arquitetura preparada para Android e iOS.

## Objetivo

Centralizar o acompanhamento pessoal de atividades, horas, estudantes, visitas, agenda, metas e relatórios em um aplicativo simples, rápido e com funcionamento local.

## Stack

- Python 3.10+
- Flet
- SQLite
- Pytest
- Ruff

## Estrutura

```text
src/
├── main.py
└── pioneiro_pro/
    ├── app.py
    ├── database/
    ├── models/
    ├── pages/
    ├── repositories/
    ├── services/
    └── utils/
tests/
```

## Executar localmente

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -e .
flet run
```

No macOS/Linux:

```bash
source .venv/bin/activate
pip install -e .
flet run
```

## Testar no celular

Android:

```bash
flet run --android
```

iOS:

```bash
flet run --ios
```

## Gerar builds

Android APK:

```bash
flet build apk
```

Android App Bundle para Google Play:

```bash
flet build aab
```

iOS:

```bash
flet build ipa
```

> A compilação final para iOS exige macOS/Xcode e as credenciais Apple apropriadas.

## Identidade do aplicativo

- Produto: Pioneiro Pro
- Projeto: pioneiro_pro_mobile
- Bundle ID atual: `br.com.pioneiropro.app`

O bundle ID deve ser confirmado antes da publicação definitiva nas lojas.
