# Pioneiro Pro Mobile

[![CI](https://github.com/M4rc3low/pioneiro-pro-mobile/actions/workflows/ci.yml/badge.svg)](https://github.com/M4rc3low/pioneiro-pro-mobile/actions/workflows/ci.yml)
[![Mobile Build](https://github.com/M4rc3low/pioneiro-pro-mobile/actions/workflows/build-mobile.yml/badge.svg)](https://github.com/M4rc3low/pioneiro-pro-mobile/actions/workflows/build-mobile.yml)
![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?logo=python&logoColor=white)
![Flet](https://img.shields.io/badge/Flet-Mobile-02569B)
![Version](https://img.shields.io/badge/version-0.5.1-2563EB)

Aplicativo mobile local-first para organização pessoal de atividades, horas, estudantes, revisitas, agenda, metas e relatórios. Desenvolvido em **Python + Flet**, com persistência em **SQLite**, testes automatizados e pipelines para Android e iOS.

## Destaques

- dashboard com resumo mensal, progresso visual e metas;
- cronômetro e registro manual de horas;
- edição e exclusão de atividades já salvas;
- cadastro, busca e acompanhamento de estudantes;
- agenda para estudos, revisitas, ligações e outros compromissos;
- localização opcional de estudantes e revisitas;
- alertas de proximidade com raio configurável e controle de repetição;
- registro de brochuras, folhetos e outras publicações;
- compartilhamento do relatório mensal pelo menu nativo do Android/iOS;
- backup e restauração em JSON;
- exportação em CSV e TXT;
- tema claro/escuro e onboarding;
- armazenamento local em SQLite, sem sincronização automática com servidor externo;
- testes automatizados, CI e builds mobile automatizados.

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
    ├── ui/
    └── utils/

tests/
docs/
```

Fluxo principal:

```text
UI/Flet
   ↓
Services / Repositories
   ↓
SQLite local
```

A separação entre interface, regras de negócio, acesso a dados e serviços facilita testes, manutenção e evolução do aplicativo.

## Stack

- **Python 3.10+**
- **Flet 1.0**
- **flet-geolocator**
- **SQLite**
- **Pytest**
- **Ruff**
- **GitHub Actions**
- **Flutter toolchain** para empacotamento mobile

## Qualidade e CI/CD

O workflow de CI executa:

1. instalação do projeto;
2. `pip check`;
3. validação de sintaxe com `compileall`;
4. análise estática crítica com Ruff;
5. testes automatizados com Pytest.

O projeto também possui workflows separados para:

- gerar **APK** e **AAB** Android;
- validar build para **iOS Simulator**;
- preparar releases versionadas no GitHub.

## Executar localmente

### Windows

```powershell
python -m venv .venv
.venv\Scripts\activate
pip install -e .
flet run
```

### macOS/Linux

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .
flet run
```

Para desenvolvimento com as ferramentas de teste e lint:

```bash
pip install -e .
pip install pytest ruff
pytest -q
ruff check src tests --select E9,F63,F7,F82
```

## Builds mobile

Android:

```bash
flet build apk --yes
flet build aab --yes
```

iOS Simulator:

```bash
flet build ios-simulator --yes
```

IPA:

```bash
flet build ipa --yes
```

A geração e assinatura final de um IPA distribuível exigem ambiente Apple e credenciais válidas do Apple Developer.

## Identidade do aplicativo

- Produto: **Pioneiro Pro**
- Pacote Python: `pioneiro_pro_mobile`
- Bundle/Application ID: `br.com.pioneiropro.app`
- Versão atual: **0.5.1**
- Android mínimo: **API 24**

## Privacidade

O Pioneiro Pro adota uma abordagem **local-first**. Os dados cadastrados ficam no dispositivo e a versão atual não os envia automaticamente para um servidor externo.

O recurso de localização é opcional e é usado para comparar a posição do aparelho com coordenadas salvas pelo próprio usuário.

Consulte [docs/PRIVACY.md](docs/PRIVACY.md) para os detalhes.

## Documentação

| Documento | Conteúdo |
| --- | --- |
| [CHANGELOG.md](CHANGELOG.md) | Histórico das versões |
| [ROADMAP.md](docs/ROADMAP.md) | Recursos concluídos e próximos passos |
| [TEST_PLAN.md](docs/TEST_PLAN.md) | Plano de testes manuais |
| [PUBLISHING.md](docs/PUBLISHING.md) | Publicação Android/iOS |
| [RELEASE_CHECKLIST.md](docs/RELEASE_CHECKLIST.md) | Checklist de release |
| [RELEASE_NOTES.md](docs/RELEASE_NOTES.md) | Notas da versão atual |
| [STORE_LISTING.md](docs/STORE_LISTING.md) | Textos preparados para as lojas |
| [PRIVACY.md](docs/PRIVACY.md) | Política de privacidade |
| [SUPPORT.md](docs/SUPPORT.md) | Suporte e abertura de problemas |

## Status

A versão **0.5.1** possui CI validada e pipeline de release/build mobile. A publicação definitiva em Google Play e App Store ainda depende de contas, assinaturas e credenciais das respectivas lojas.
