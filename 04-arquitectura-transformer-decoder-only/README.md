# Arquitectura Transformer decoder-only

> Viene de [03. Atención](../03-atencion-self-attention-multi-head/README.md). Acá se juntan las piezas (tokens, embeddings y attention) en un LLM completo: GPT, Claude, Llama.

---

## 1. La idea en una línea

Un LLM decoder-only es una **pila de bloques iguales** que transforma una secuencia de tokens en una **probabilidad para el próximo token**.

```
"el gato"  →  tokens  →  embeddings + posición  →  [Bloque] × N  →  LayerNorm  →  logits  →  softmax  →  "duerme" (p=0.41)
```

Se llama *decoder-only* porque el Transformer original (2017, traducción) tenía **encoder + decoder**. Los LLM se quedaron solo con la mitad del decoder: no hay texto de "entrada" separado, todo es una única secuencia que se continúa.

| Variante | Ejemplo | Ve el futuro | Para qué |
|---|---|---|---|
| Encoder-only | BERT | Sí (bidireccional) | Clasificar, embeddings |
| Encoder-decoder | T5, Transformer original | Encoder sí, decoder no | Traducir, resumir |
| **Decoder-only** | **GPT, Claude, Llama** | **No (causal)** | **Generar texto** |

---

## 2. Entrada: tokens → vectores

1. El texto se tokeniza → `[0, 1, 2]` (ver [tema 01](../01-tokens-y-tokenizacion/README.md)).
2. Cada id se busca en la **tabla de embeddings** → un vector de `d_model` números (ver [tema 02](../02-embeddings-y-similitud-coseno/README.md)).
3. Se le suma información de **posición**, porque attention por sí sola no sabe el orden (GPT-2 usa posiciones aprendidas; los modelos modernos usan RoPE).

Resultado: una matriz `x` de forma `(T, d_model)`, un vector por token. Esa matriz es el **residual stream**: viaja por todos los bloques y cada uno le *suma* algo.

---

## 3. El bloque Transformer

Cada bloque tiene dos subcapas, cada una con su **LayerNorm** antes y su **conexión residual** después:

```
x ──┬──► LayerNorm ──► Self-Attention causal ──►(+)──┬──► LayerNorm ──► MLP ──►(+)──► x'
    └──────────────────────────────────────────────┘ └───────────────────────────┘
                 residual                                     residual
```

```python
x = x + attention(layer_norm(x))   # los tokens se comunican entre sí
x = x + mlp(layer_norm(x))         # cada token "piensa" por separado
```

| Pieza | Qué hace | Intuición |
|---|---|---|
| **Self-attention causal** | Mezcla información entre tokens, solo mirando hacia atrás (ver [tema 03](../03-atencion-self-attention-multi-head/README.md)) | Comunicación |
| **MLP / feed-forward** | Dos capas lineales con activación en el medio (`d → 4d → d`), token por token | Cómputo y "memoria" de hechos |
| **Residual (`x + …`)** | Cada subcapa suma un ajuste en vez de reemplazar | Permite apilar 100+ capas sin que el gradiente se pierda |
| **LayerNorm** | Normaliza cada vector (media 0, varianza 1) | Mantiene los números estables |

Detalles modernos que vas a ver: **pre-norm** (LayerNorm antes, no después), **RMSNorm** en lugar de LayerNorm, y **SwiGLU** en lugar de GELU en el MLP. La estructura es la misma.

---

## 4. Por qué importa la máscara causal

La attention de cada bloque usa la **máscara causal** del [tema 03](../03-atencion-self-attention-multi-head/README.md#7-máscara-causal-por-qué-el-modelo-no-puede-ver-el-futuro): cada token solo ve a sí mismo y a los anteriores. Consecuencia: **cambiar un token futuro no altera lo calculado para los anteriores**. Eso habilita dos cosas:

- **Entrenamiento en paralelo:** con una frase de T tokens se entrenan T predicciones a la vez (la posición *i* predice el token *i+1*).
- **KV cache al generar:** lo calculado para los tokens viejos no cambia, así que se reutiliza (ver [tema 07](../07-kv-cache-prefill-decode-prompt-caching/README.md)).

---

## 5. Salida: vectores → próximo token

Después del último bloque:

1. **LayerNorm final.**
2. **Unembedding:** se multiplica por una matriz `(d_model, vocab)` → un **logit** por cada token del vocabulario. Muchos modelos reutilizan la tabla de embeddings transpuesta (*weight tying*).
3. **Softmax** → probabilidades.

Se calcula para todas las posiciones, pero al generar **solo importa la última**. Elegir qué token sacar de esa distribución es el [tema 05](../05-siguiente-token-y-sampling/README.md).

---

## 6. Generar texto: un loop

El modelo predice **un token por vez** y lo agrega a la entrada (*autoregresivo*):

```
"el gato"         → modelo → "duerme"
"el gato duerme"  → modelo → "en"
"el gato duerme en" → modelo → "la"   … hasta un token de fin o un límite
```

```python
ids = tokenizar(prompt)
while not terminado:
    probs = softmax(forward(ids)[-1])
    ids.append(elegir(probs))
```

---

## 7. Tamaños reales

| Modelo | Capas (N) | `d_model` | Cabezas | `d_k` por cabeza | Contexto | Parámetros |
|---|---|---|---|---|---|---|
| Transformer original (2017) | 6 + 6 | 512 | 8 | 64 | — | 65 M |
| GPT-2 small | 12 | 768 | 12 | 64 | 1 024 | 124 M |
| GPT-3 | 96 | 12 288 | 96 | 128 | 2 048 | 175 B |
| Llama 3 8B | 32 | 4 096 | 32 | 128 | 8 192 | 8 B |

Regla rápida para un GPT clásico: cada bloque tiene ~**12 · d_model²** parámetros (4·d² en attention + 8·d² en el MLP). Para GPT-3: `96 × 12 × 12288² ≈ 174 B`. El resto son los embeddings.

Escalar un LLM es básicamente **más capas, vectores más anchos y más datos**; la arquitectura casi no cambia.

---

## 8. Código: forward pass completo en NumPy

> 📄 Archivo: [`transformer_numpy.py`](transformer_numpy.py) — `pip install numpy`, después `python3 transformer_numpy.py`

Un mini-GPT de 2 bloques con pesos aleatorios (~80 líneas): embeddings + posición, attention multi-head causal, MLP, residuales, LayerNorm y logits. Además verifica que la máscara causal funcione.

```
entrada: <bos> el gato
shape logits: (3, 10) (una distribución por posición)

probabilidades del próximo token (pesos aleatorios, sin entrenar):
     casa  0.212
       el  0.126
     come  0.119
     ...

¿cambiar el token 3 alteró las posiciones 1-2? False
```

Las predicciones no tienen sentido porque nadie lo entrenó.

---

## 9. Resumen

- Un LLM decoder-only es **embeddings → N bloques idénticos → logits**.
- Cada bloque = **attention causal** (los tokens se comunican) + **MLP** (cada token procesa), con **residual** y **LayerNorm**.
- La **máscara causal** impide mirar el futuro: permite entrenar en paralelo y usar KV cache.
- Genera **un token por vez**, en loop.
- Los modelos grandes son la misma receta, escalada.

**Siguiente:** cómo se elige el próximo token a partir de esas probabilidades → [05. Siguiente token y sampling](../05-siguiente-token-y-sampling/README.md).

## Referencias

- Vaswani et al., [*Attention Is All You Need*](https://arxiv.org/abs/1706.03762) (2017).
- Radford et al., [*Language Models are Unsupervised Multitask Learners*](https://cdn.openai.com/better-language-models/language_models_are_unsupervised_multitask_learners.pdf) (GPT-2, 2019).
- Jay Alammar, [*The Illustrated GPT-2*](https://jalammar.github.io/illustrated-gpt2/).
- Andrej Karpathy, [nanoGPT](https://github.com/karpathy/nanoGPT).
