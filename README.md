# Pioneiro Pro Mobile

Aplicativo mobile do Pioneiro Pro desenvolvido em Python com Flet, com arquitetura preparada para Android e iOS.

## Versão atual

**0.3.0**

## O que já funciona

- dashboard com resumo mensal;
- cronômetro de atividade;
- registro manual de horas;
- edição e exclusão de atividades;
- metas mensais e anuais;
- progresso mês a mês;
- cadastro e perfil completo de estudantes;
- busca e filtros de estudantes;
- histórico de estudos e revisitas;
- agenda com estudos, revisitas, ligações e outros compromissos;
- conclusão, edição e exclusão de compromissos;
- lembrete de compromissos ao abrir/retomar o aplicativo;
- tema claro e escuro;
- onboarding inicial;
- backup e restauração em JSON;
- exportação de relatório em CSV;
- exportação de resumo em TXT;
- banco SQLite local;
- testes automatizados;
- builds automatizados para Android e validação de iOS.

## Arquitetura

```text
src/
├── assets/
│   ├── icon.png
│   └── splash.png
├── main.py
└── pioneiro_pro/
    ├── app.py
    ├── database/
    ├── pages/
    ├── repositories/
    ├── services/
    └── utils/
tests/
docs/
```

Fluxo principal de dados:

```text
Tela → Repository/Service → SQLite
```

## Stack

- Python 3.10+
- Flet
- SQLite
- Pytest
- GitHub Actions

## Executar localmente

Windows:

```powershell
python -m venv .venv
.venv\Scripts\activate
pip install -e .
flet run
```

macOS/Linux:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .
flet run
```

## Gerar builds

Android APK:

```bash
flet build apk --yes
```

Android App Bundle:

```bash
flet build aab --yes
```

Simulador iOS:

```bash
flet build ios-simulator --yes
```

IPA para distribuição:

```bash
flet build ipa --yes
```

A geração e assinatura final de IPA para distribuição exigem ambiente Apple e credenciais válidas do Apple Developer.

## Identidade

- Produto: Pioneiro Pro
- Projeto: `pioneiro_pro_mobile`
- Bundle ID atual: `br.com.pioneiropro.app`

Confirme o bundle ID antes da primeira publicação definitiva nas lojas.

## Privacidade

A versão atual trabalha de forma local-first. Consulte [docs/PRIVACIDADE.md](docs/PRIVACIDADE.md).

## Publicação

Consulte [docs/PUBLICACAO.md](docs/PUBLICACAO.md) para os passos de Google Play e App Store.
