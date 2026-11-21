# Radar Inteligente de Ofertas — Android

Projeto inicial nativo para Android (Kotlin), com:
- tela inicial simples;
- agendamento de pesquisa diária com WorkManager;
- solicitação de permissão de notificações no Android 13+;
- botão para testar notificações;
- botão para disparar uma pesquisa manual;
- regra de não notificar quando não houver oferta elegível.

## Importante: o que já funciona e o que falta

O aplicativo já implementa o agendamento local e as notificações. **Ele ainda não pesquisa lojas sozinho**, porque isso exige um serviço de backend conectado a fontes de preços autorizadas (APIs de afiliados/marketplaces ou provedores de dados). Não é seguro nem confiável embutir raspagem indiscriminada de lojas no app.

O worker espera um endpoint HTTPS que retorne JSON neste formato:

```json
{
  "deals": [
    {
      "title": "Tablet exemplo 256 GB / 8 GB RAM",
      "price": "R$ 1.499,00",
      "store": "Loja Exemplo",
      "verified": true,
      "good_deal": true,
      "url": "https://loja.example/produto"
    }
  ]
}
```

O app só notifica quando `verified` e `good_deal` forem `true`. Uma lista vazia significa nenhuma notificação.

## Configurar o endpoint

A preferência `deals_endpoint` é lida de SharedPreferences (`radar`). Para um protótipo, configure-a no código ou adicione uma tela de configuração antes de distribuir. Use somente endpoint HTTPS controlado por você.

## Abrir no Android Studio

1. Extraia o ZIP.
2. Abra a pasta `RadarInteligenteOfertas` no Android Studio.
3. Aguarde a sincronização do Gradle.
4. Conecte um Android e pressione Run.
5. Conceda permissão para notificações.
6. Toque em **Testar notificação**.

## Limitações

- WorkManager executa tarefas periódicas em janela flexível; Android pode atrasar a execução por economia de bateria. Não garante horário exato.
- O usuário precisa permitir notificações.
- O backend de pesquisa e a lógica de validação do histórico de preços ainda precisam ser implementados.
- Antes de publicar, configure ícone, política de privacidade, endpoint seguro e testes em aparelhos reais.
