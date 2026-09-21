# Publicação — Pioneiro Pro

## Identidade atual

- Nome: Pioneiro Pro
- Versão: 0.3.0
- Bundle/Application ID: `br.com.pioneiropro.app`
- Plataforma: Android e iOS
- Tecnologia: Python + Flet

## Android

### Builds
- APK: para testes e instalação direta.
- AAB: formato para distribuição pela Google Play.

### Antes de publicar
- Confirmar o bundle ID definitivo.
- Criar/guardar a chave de assinatura de produção.
- Criar conta no Google Play Console.
- Criar ficha da loja: nome, descrição, categoria, capturas e ícone.
- Informar URL da política de privacidade.
- Preencher a seção de segurança de dados com base no comportamento real do aplicativo.
- Fazer teste interno/fechado antes da produção.

## iOS

### Builds
- iOS Simulator: validação técnica sem assinatura.
- IPA/App Store: exige assinatura Apple.

### Antes de publicar
- Ter acesso a macOS/Xcode para assinatura final.
- Criar/usar conta Apple Developer.
- Registrar o bundle ID.
- Configurar certificados e provisioning profiles.
- Criar o aplicativo no App Store Connect.
- Preparar screenshots, descrição e política de privacidade.
- Validar via TestFlight antes da publicação.

## GitHub Actions

O repositório possui:

- `CI`: valida sintaxe, instalação e testes Python.
- `Mobile Build`: constrói APK, AAB e uma versão de simulador iOS.

Os artefatos gerados ficam disponíveis na execução do workflow no GitHub Actions.

## Observação sobre notificações

A versão 0.3.0 possui lembretes dentro do aplicativo ao abrir ou retomar o app. Notificações locais agendadas no sistema operacional exigem uma integração nativa específica e devem ser tratadas como uma etapa separada antes de marcar notificações de segundo plano como concluídas.
