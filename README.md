# Cómo funciona un LLM

Guía por temas para entender cómo funcionan los modelos de lenguaje. Cada tema tiene su propia carpeta con explicación, ejemplos y código cuando corresponda.

## Temas

### Esenciales

- [x] [01. Tokens y tokenización](01-tokens-y-tokenizacion/README.md) (BPE, SentencePiece y costo por token)
- [x] [02. Embeddings y similitud coseno](02-embeddings-y-similitud-coseno/README.md)
- [x] [03. Atención y self-attention](03-atencion-self-attention-multi-head/README.md) (multi-head)
- [ ] [04. Arquitectura Transformer](04-arquitectura-transformer-decoder-only/README.md) (decoder-only)
- [ ] [05. Predicción del siguiente token y sampling](05-siguiente-token-y-sampling/README.md) (temperature, top-p, top-k)
- [ ] [06. Ventana de contexto y context rot](06-ventana-de-contexto-y-context-rot/README.md)
- [ ] [07. KV cache, prefill y decode](07-kv-cache-prefill-decode-prompt-caching/README.md) (prompt caching)
- [ ] [08. Modelos de razonamiento y test-time compute](08-razonamiento-test-time-compute/README.md) (parámetro effort)
- [ ] [09. Alucinaciones y límites](09-alucinaciones-y-limites/README.md)

### Recomendados

- [ ] [10. Mixture of Experts](10-mixture-of-experts/README.md) (parámetros totales vs. activos)
- [ ] [11. Positional encoding y GQA](11-positional-encoding-y-gqa/README.md) (RoPE)
- [ ] [12. Cómo se hace un modelo](12-pretraining-sft-rlhf-dpo/README.md) (Pretraining, SFT, RLHF y DPO)

### Opcionales

- [ ] [13. Implementar un mini-GPT desde cero](13-implementar-mini-gpt/README.md)
- [ ] [14. Matemática para entender los LLM](14-matematica-para-llm/README.md) (álgebra lineal, gradientes y backprop)

## Añadir un tema

1. Crea una carpeta numerada siguiendo el orden de la lista, por ejemplo `15-nombre-del-tema/`.
2. Añade un `README.md` con la explicación y los enlaces a los ejemplos.
3. Agrega el tema a la lista de arriba con su nivel: esencial, recomendado u opcional.

Cada tema completo trae su código: implementaciones y errores comunes en [01](01-tokens-y-tokenizacion/README.md) y [02](02-embeddings-y-similitud-coseno/README.md), y scripts de atención en [03](03-atencion-self-attention-multi-head/README.md).