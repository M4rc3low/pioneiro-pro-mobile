# Roadmap — Pioneiro Pro Mobile

## Fundação
- [x] Projeto Python/Flet
- [x] Estrutura para Android e iOS
- [x] Banco SQLite local
- [x] Navegação mobile
- [x] Dashboard
- [x] Registro de atividades
- [x] Testes automatizados

## Gestão pessoal
- [x] Cronômetro em tempo real
- [x] Edição e exclusão de atividades
- [x] Perfil completo de estudantes
- [x] Histórico de estudos e revisitas
- [x] Agenda funcional
- [x] Marcar compromissos como concluídos
- [x] Metas mensais e anuais
- [x] Progresso mensal
- [x] Tema claro e escuro
- [x] Busca e filtros

## Dados e segurança
- [x] Backup JSON compatível com versões anteriores
- [x] Backup protegido por senha
- [x] Restauração de backup protegido
- [x] Validação de esquema durante restauração
- [x] Exportação CSV
- [x] Exportação de resumo TXT
- [x] Política de privacidade
- [x] Bloqueio opcional por biometria/PIN/credencial do aparelho
- [ ] Migrações numeradas com `schema_version`
- [ ] Criptografia do banco SQLite em repouso

## Proximidade
- [x] GPS Android/iOS
- [x] localização por estudante
- [x] localização por revisita
- [x] raio configurável
- [x] controle de repetição
- [x] proximidade opt-in em novas instalações
- [x] tratamento de localização desligada/permissão negada
- [x] orientação para permissão de localização em segundo plano
- [x] notificação nativa Android quando o processo continua ativo em segundo plano
- [ ] geofencing/notificação confiável com o processo totalmente encerrado
- [ ] equivalente de notificação nativa de proximidade no iOS

## Experiência mobile
- [x] Onboarding
- [x] Ícone
- [x] Splash
- [x] Lembretes dentro do aplicativo com antecedência configurável
- [x] Ação **Como chegar** via Google Maps
- [x] Bloqueio automático após retorno do segundo plano
- [ ] testes de consumo de bateria em uso prolongado de localização

## Distribuição
- [x] Pipeline de CI
- [x] Pipeline de build mobile
- [x] APK validado em pipeline anterior
- [x] AAB validado em pipeline anterior
- [x] Build de simulador iOS validado em pipeline anterior
- [ ] validar build mobile com a nova camada de notificação/criptografia
- [ ] assinatura Android de produção
- [ ] Google Play Console
- [ ] Apple Developer
- [ ] IPA assinado
- [ ] App Store Connect
- [ ] TestFlight
- [ ] publicação nas lojas

## Futuro opcional
- [ ] Sincronização em nuvem
- [ ] Autenticação de conta
- [ ] Exportação/importação seletiva
