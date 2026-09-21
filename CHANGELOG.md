# Changelog

## 0.5.1 — 2026-09-21

### Identidade visual
- novo ícone oficial do aplicativo com relógio, sol, nuvem e chuva;
- correção do nome do arquivo de ícone para `src/assets/icon.png`;
- preparação de nova release para Android e iOS com o novo ícone.


## 0.5.0 — 2026-09-21

### Interface
- novo design system centralizado;
- cards com borda suave, profundidade e melhor contraste;
- gradientes discretos na identidade principal;
- dashboard redesenhado;
- cronômetro com visual de destaque;
- onboarding renovado;
- navegação inferior refinada;
- cabeçalhos e seções padronizados;
- chips de status e estados vazios mais claros;
- melhorias específicas para tema escuro;
- perfil de estudante, agenda, relatórios e configurações unificados visualmente.

### Qualidade
- smoke tests das oito telas principais;
- análise estática com Ruff;
- validação de dependências;
- testes de migração e backup da versão atual;
- suíte automatizada completa antes do build mobile.


## 0.4.0 — 2026-09-21

### Proximidade
- localização opcional salva por estudante;
- localização específica opcional por revisita;
- raio de proximidade configurável;
- monitoramento via GPS;
- suporte às permissões de localização do Android e iOS;
- controle global de avisos por proximidade;
- limite de repetição de alertas para evitar notificações excessivas.

### Registros
- quantidade de brochuras;
- quantidade de folhetos;
- outras publicações;
- edição posterior do tempo e das quantidades no histórico;
- totais mensais de publicações.

### Relatório mensal
- resumo mensal com tempo, registros e publicações;
- botão de compartilhamento usando a folha nativa do sistema;
- compatível com WhatsApp, e-mail, Mensagens e demais destinos oferecidos pelo aparelho.

### Privacidade
- localização permanece armazenada localmente;
- política de privacidade atualizada com o uso opcional de GPS.


## 0.3.0 — 2026-09-21

### Aplicativo
- dashboard com progresso mensal;
- cronômetro;
- registro, edição e exclusão de atividades;
- metas mensais e anuais;
- perfil completo de estudantes;
- busca e filtros;
- agenda de estudos, revisitas e ligações;
- histórico de visitas;
- onboarding;
- tema claro e escuro;
- lembretes ao abrir ou retomar o aplicativo.

### Dados
- banco SQLite local;
- backup em JSON;
- restauração de backup;
- exportação CSV;
- exportação de resumo em TXT.

### Mobile
- identidade visual própria;
- ícone e splash;
- configuração Android/iOS;
- CI e pipeline de build mobile.

### Qualidade
- testes de banco;
- testes de repositórios;
- testes de cronômetro;
- testes de backup/restauração;
- testes de exportação;
- teste de importação do aplicativo.
