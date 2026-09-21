# Publicação Mobile — Pioneiro Pro

## Identidade atual

- Produto: **Pioneiro Pro**
- Pacote Python: `pioneiro_pro_mobile`
- Bundle/Application ID: `br.com.pioneiropro.app`
- Android mínimo: API 24
- Interface: Flet
- Dados locais: SQLite

> O bundle ID deve ser tratado como definitivo antes da primeira publicação nas lojas.

## Builds de teste

O workflow **Mobile Build** gera automaticamente:

- APK Android;
- AAB Android;
- aplicativo para iOS Simulator.

Os arquivos ficam disponíveis como artifacts na execução do GitHub Actions.

## Android — distribuição interna

O APK gerado pode ser instalado diretamente em um aparelho Android para testes.

## Google Play

Para publicação em produção:

1. Criar a conta no Google Play Console.
2. Criar uma chave de assinatura de produção.
3. Guardar a chave e senhas fora do repositório.
4. Configurar os segredos no GitHub Actions ou realizar o build local assinado.
5. Gerar o AAB assinado.
6. Criar a ficha do aplicativo, política de privacidade e classificação indicativa.
7. Enviar primeiro para teste interno.
8. Validar e promover para produção.

Nunca versionar arquivos de keystore ou senhas no Git.

## iOS

O código está preparado para iOS e o pipeline valida o build de simulador.

Para gerar um IPA distribuível:

1. Ter uma conta ativa no Apple Developer Program.
2. Registrar o Bundle ID `br.com.pioneiropro.app`.
3. Criar certificados e perfis de provisionamento.
4. Configurar assinatura no ambiente macOS/Xcode.
5. Executar o build IPA.
6. Enviar para App Store Connect.
7. Testar via TestFlight.
8. Submeter para revisão.

Um IPA assinado não pode ser produzido apenas com o código-fonte: a Apple exige credenciais e assinatura vinculadas à conta do desenvolvedor.

## Builds locais

Android:

```bash
flet build apk
flet build aab
```

iOS Simulator:

```bash
flet build ios-simulator
```

IPA, em macOS devidamente configurado:

```bash
flet build ipa
```

## Checklist antes da loja

- [ ] Nome definitivo do aplicativo
- [ ] Bundle ID confirmado
- [ ] Ícone revisado
- [ ] Splash revisado
- [ ] Política de privacidade com contato
- [ ] Teste em aparelhos Android físicos
- [ ] Teste em iPhone/iPad
- [ ] Teste de backup e restauração
- [ ] Teste de migração de banco
- [ ] Conta Google Play
- [ ] Conta Apple Developer
- [ ] Chaves/certificados de produção
