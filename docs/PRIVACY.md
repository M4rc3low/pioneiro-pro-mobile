# Política de Privacidade — Pioneiro Pro

Última atualização: 21 de setembro de 2026.

## Visão geral

O Pioneiro Pro foi projetado para organizar registros pessoais de atividades, estudantes, agenda, metas e configurações com uma abordagem local-first.

## Dados armazenados

A versão atual pode armazenar localmente no dispositivo informações que o próprio usuário registra, como:

- nome e congregação configurados pelo usuário;
- registros de atividades e tempo;
- nomes, telefones, endereços e observações de estudantes;
- compromissos de agenda e revisitas;
- metas e preferências do aplicativo;
- quantidades de publicações registradas;
- coordenadas salvas voluntariamente para alertas de proximidade.

## Armazenamento e transmissão

Os dados ficam no banco SQLite privado do aplicativo. A versão atual não sincroniza automaticamente esses dados com um servidor do Pioneiro Pro, não possui publicidade e não usa rastreamento de terceiros para fins publicitários.

## Localização

O recurso de proximidade é opcional e começa desativado em novas instalações. Antes de ativá-lo, o aplicativo explica o uso da localização e solicita a decisão do usuário.

Quando ativado, o Pioneiro Pro compara a localização do aparelho com coordenadas de estudantes ou revisitas que o próprio usuário cadastrou. Essa comparação é feita no dispositivo.

No Android, o usuário pode permitir localização em segundo plano. Quando o processo do aplicativo continua ativo em segundo plano, um alerta de proximidade pode ser apresentado como notificação nativa. No iOS, o sistema aplica suas próprias regras para atualizações de localização em segundo plano.

O sistema operacional pode suspender ou encerrar completamente o aplicativo. Por isso, o Pioneiro Pro não garante monitoramento contínuo depois que o processo é totalmente encerrado.

As coordenadas salvas e a posição usada para comparação não são enviadas automaticamente a um servidor do Pioneiro Pro.

## Proteção do aplicativo

O usuário pode ativar um bloqueio local opcional. Quando habilitado, o Pioneiro Pro utiliza a autenticação fornecida pelo próprio sistema operacional, como biometria, PIN, senha ou padrão do aparelho.

O Pioneiro Pro não armazena a senha, PIN ou dados biométricos usados pelo sistema operacional.

## Backup e exportação

O aplicativo oferece:

- backup protegido por senha no formato `.ppbackup`;
- restauração de backups protegidos;
- compatibilidade com backup JSON antigo sem senha;
- relatório em CSV;
- resumo em TXT.

O backup protegido deriva uma chave a partir da senha escolhida pelo usuário e usa criptografia autenticada. A senha não é armazenada nem pode ser recuperada pelo Pioneiro Pro.

O backup JSON sem senha e as exportações CSV/TXT podem conter informações legíveis. O usuário deve protegê-los depois que forem salvos ou compartilhados fora do aplicativo.

## Permissões

O aplicativo solicita permissões conforme os recursos habilitados, incluindo localização, localização em segundo plano quando escolhida pelo usuário, notificações no Android e autenticação local quando o bloqueio é ativado.

## Exclusão dos dados

Os registros podem ser excluídos dentro do aplicativo. A remoção do aplicativo também remove os dados locais conforme o comportamento do sistema operacional, salvo arquivos que o próprio usuário exportou para outro local.

## Sincronização em nuvem

A versão atual não possui sincronização automática em nuvem. Caso esse comportamento mude, esta política deverá ser atualizada antes da ativação pública do novo recurso.

## Contato

Para suporte e questões de privacidade, consulte [SUPPORT.md](SUPPORT.md). Não publique nomes, telefones, endereços, coordenadas ou arquivos de backup em chamados públicos.
