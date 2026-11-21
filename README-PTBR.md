# Radar Inteligente de Ofertas — servidor

Este é o backend inicial para o aplicativo Android. Ele consulta resultados do Google Shopping via SerpAPI e mantém um histórico simples de preços.

## Importante
- Não coloque a chave SerpAPI neste repositório.
- Cadastre `SERPAPI_KEY` como variável secreta no Render.
- O histórico começa a ser construído depois da publicação. Na primeira consulta, o preço é apenas uma referência, não um desconto comprovado.
- O plano gratuito do Render pode dormir após inatividade e o disco local pode não ser persistente. Para histórico duradouro, será necessário configurar banco de dados persistente (por exemplo PostgreSQL) e armazenamento adequado.
- A busca depende da disponibilidade, dos termos e dos limites da SerpAPI e dos sites exibidos pelo Google Shopping.
- Este backend ainda precisa ser ligado ao app Android e testado com uma implantação real.

## Como publicar pelo celular usando GitHub + Render

1. No GitHub, crie um repositório novo chamado `radar-inteligente-ofertas-api`.
2. Deixe-o **Private** e não adicione README, licença ou `.gitignore` (os arquivos já estão neste pacote).
3. Extraia este ZIP no computador ou use o GitHub pelo navegador para enviar os arquivos e pastas mantendo a estrutura.
4. No Render, escolha **New + → Blueprint** e conecte o repositório.
5. Quando o Render pedir `SERPAPI_KEY`, cole a chave nova diretamente no campo secreto do Render — nunca no GitHub nem no chat.
6. Conclua o deploy. O endereço do serviço será parecido com `https://nome-do-servico.onrender.com`.
7. Teste abrindo `https://SEU-ENDERECO/health`. Deve aparecer `{"ok":true,...}`.
8. Para testar uma pesquisa, abra `https://SEU-ENDERECO/api/deals?q=tablet%20256gb`.

## Endpoints
- `GET /health` — saúde do servidor.
- `GET /api/deals?q=termo` — pesquisa produtos e grava preços observados.
- `GET /api/history?q=termo` — consulta observações anteriores.

## Variáveis
- `SERPAPI_KEY` (obrigatória, secreta)
- `MIN_DROP_PERCENT` (opcional; padrão 15)
- `DB_PATH` (opcional; padrão `/tmp/radar_prices.db`)
