# Checklist de Release — Pioneiro Pro

## Código
- [x] CI automatizado
- [x] testes automatizados
- [x] banco local e migrações
- [x] backup e restauração
- [x] exportação
- [x] assets mobile
- [x] APK validado
- [x] AAB validado
- [x] iOS Simulator validado
- [x] workflow de release

## Antes de cada versão
- [ ] atualizar `version` no `pyproject.toml`
- [ ] atualizar `CHANGELOG.md`
- [ ] atualizar `docs/RELEASE_NOTES.md`
- [ ] aguardar CI verde
- [ ] executar o workflow **Release**
- [ ] instalar o APK em aparelho físico
- [ ] testar backup e restauração
- [ ] testar cronômetro
- [ ] testar agenda
- [ ] testar edição/exclusão
- [ ] testar tema claro/escuro

## Google Play
- [ ] conta Google Play Console
- [ ] aplicativo criado no console
- [ ] chave de assinatura de produção
- [ ] política de privacidade publicada
- [ ] ficha da loja preenchida
- [ ] screenshots
- [ ] questionário de segurança dos dados
- [ ] classificação indicativa
- [ ] AAB de produção assinado
- [ ] teste interno concluído

## Apple
- [ ] conta Apple Developer
- [ ] Bundle ID registrado
- [ ] certificados de distribuição
- [ ] provisioning profile
- [ ] App Store Connect configurado
- [ ] política de privacidade
- [ ] ficha da loja preenchida
- [ ] screenshots
- [ ] declaração App Privacy
- [ ] IPA assinado
- [ ] TestFlight concluído

## Dependências externas ainda necessárias para publicação

O código não pode criar por conta própria:

1. conta Google Play Console;
2. conta Apple Developer;
3. certificados e chaves privadas do proprietário;
4. assinaturas de distribuição das lojas.

Esses itens pertencem às contas do publicador e nunca devem ser gravados diretamente no repositório.
