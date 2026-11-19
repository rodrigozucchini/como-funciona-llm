# Embeddings contextuales y pooling

Un transformer (BERT y sucesores) no le da a cada palabra un vector fijo: lee **la oración entera** y cada token sale con un vector que depende de todos los demás. `banco` en "me senté en el banco" y en "pedí un préstamo en el banco" sale con vectores distintos.

**Ejemplo real:** BERT (Google, 2018), Sentence-BERT (2019) y todos los modelos de embeddings actuales, que son transformers de este tipo.

## De texto a un vector por token

```
"pedí un préstamo en el banco"
        │  tokenizer
        ▼
[CLS]  pedí  un  préstamo  en  el  banco  [SEP]
  │     │    │      │      │   │     │      │
  ▼     ▼    ▼      ▼      ▼   ▼     ▼      ▼
┌───────────────────────────────────────────────┐
│     transformer (capas de atención)            │   cada token "mira" a todos los demás
└───────────────────────────────────────────────┘
  │     │    │      │      │   │     │      │
  ▼     ▼    ▼      ▼      ▼   ▼     ▼      ▼
 v₀    v₁   v₂     v₃     v₄  v₅    v₆     v₇      8 vectores de 768 números cada uno
```

En cada capa, la **atención** deja que cada token tome información de los demás. Al final, el vector de `banco` ya "sabe" que cerca había un `préstamo`.

## Pooling: de muchos vectores a uno

Para comparar textos necesitamos **un solo vector por texto**. Hay que resumir los vectores de los tokens:

| Pooling | Cómo | Comentario |
|---|---|---|
| **`[CLS]`** | Quedarse con el vector del token especial del principio | Lo que usaba BERT para clasificar. Sin entrenamiento específico, no sirve para similitud. |
| **Promedio (mean pooling)** | Promediar los vectores de todos los tokens (sin contar el padding) | El más usado en modelos abiertos. Estable y simple. |
| **Último token** | Quedarse con el vector del último token | Lo usan los modelos de embeddings construidos sobre LLMs (decoder), porque el último token es el único que vio todo el texto. |
| **Máximo** | Para cada dimensión, el valor más alto entre todos los tokens | Poco usado hoy. |

El pooling no se elige libremente: **es parte del modelo**. Hay que usar el que se usó al entrenarlo.

## Por qué BERT "crudo" no alcanza

BERT se entrenó para adivinar palabras tapadas, no para comparar oraciones. Si se promedian sus vectores y se calcula el coseno, los resultados son malos: casi todo da parecido a todo. Sentence-BERT (Reimers y Gurevych, 2019) mostró que hace falta **ajustar** el modelo con pares de oraciones para que el coseno tenga sentido.

```
          BERT crudo + promedio             Sentence-BERT
"el gato duerme" vs "el felino descansa"     0,91         0,84
"el gato duerme" vs "la bolsa cotiza"        0,83         0,06   ← acá está la diferencia
```

*(Valores ilustrativos: lo que importa es que en el modelo crudo todo queda en un rango alto y apretado.)*

Ese ajuste es el [entrenamiento contrastivo](../04-entrenamiento-contrastivo).

## Bi-encoder vs cross-encoder

Hay dos formas de usar un transformer para comparar textos:

```
Bi-encoder (embeddings)                    Cross-encoder (reranker)

 texto A ──► modelo ──► vector A ─┐         texto A + texto B ──► modelo ──► puntaje
                                  ├─► coseno
 texto B ──► modelo ──► vector B ─┘
```

| | Bi-encoder | Cross-encoder |
|---|---|---|
| Qué hace | Cada texto por separado, después se comparan vectores | Lee los dos textos juntos |
| Precisión | Buena | Mejor: ve las dos cosas a la vez |
| Se puede precalcular | Sí: embeddeás los documentos una vez | No: hay que correrlo por cada par |
| Para buscar en 1 millón | Viable | Imposible |

Lo normal es combinarlos: el bi-encoder trae los 50–100 candidatos y el cross-encoder los reordena (ver [`errores/06-parecido-no-es-relevante`](../../errores/06-parecido-no-es-relevante)).

## El límite de tokens

Cada modelo acepta un máximo de tokens: 512 en los más viejos o chicos, 8.000 a 32.000 en los más nuevos. Lo que se pasa se trunca o da error según el proveedor. Y aunque entre, un texto muy largo termina "promediado" (ver [`errores/05-chunks-mal-cortados`](../../errores/05-chunks-mal-cortados)).

## ✅ / ❌

- ✅ El vector de cada palabra depende del contexto: resuelve la polisemia.
- ✅ Representa oraciones, párrafos y documentos enteros con un solo vector.
- ✅ Los modelos multilingües ubican `dog` y `perro` en el mismo lugar.
- ❌ Mucho más caro de calcular que word2vec: un transformer por cada texto.
- ❌ Sin entrenamiento específico para similitud, los vectores no sirven para comparar.
- ❌ Comprimir un texto entero en un vector pierde detalle: un bi-encoder nunca es tan preciso como leer los dos textos juntos.
