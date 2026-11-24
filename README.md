# Cómo funciona un LLM

Guía por temas para entender cómo funcionan los modelos de lenguaje. Cada tema tiene su propia carpeta con explicación, ejemplos y código cuando corresponda.

## Temas

- [x] [01. Tokens y tokenización](01-tokens-y-tokenizacion/README.md) (BPE, SentencePiece y costo por token)
- [x] [02. Embeddings y similitud coseno](02-embeddings-y-similitud-coseno/README.md)
- [x] [03. Atención y self-attention](03-atencion-self-attention-multi-head/README.md) (multi-head)
- [x] [04. Arquitectura Transformer](04-arquitectura-transformer-decoder-only/README.md) (decoder-only)
- [x] [05. Predicción del siguiente token y sampling](05-siguiente-token-y-sampling/README.md) (temperature, top-p, top-k)
- [x] [06. Ventana de contexto y context rot](06-ventana-de-contexto-y-context-rot/README.md)
- [x] [07. KV cache, prefill y decode](07-kv-cache-prefill-decode-prompt-caching/README.md) (prompt caching)
- [x] [08. Modelos de razonamiento y test-time compute](08-razonamiento-test-time-compute/README.md) (parámetro effort)
- [x] [09. Alucinaciones y límites](09-alucinaciones-y-limites/README.md)

## Añadir un tema

1. Crea una carpeta numerada siguiendo el orden de la lista, por ejemplo `10-nombre-del-tema/`.
2. Añade un `README.md` con la explicación y los enlaces a los ejemplos.
3. Agrega el tema a la lista de arriba.

Cada tema arranca donde termina el anterior. Los temas 03 y 04 traen además un script en Python para quien quiera ver el código.