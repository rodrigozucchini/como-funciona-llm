# Attention, Self-Attention y Multi-Head Attention

> Viene de [02. Embeddings](../02-embeddings-y-similitud-coseno/README.md): cada token ya es un vector. Acá se ve cómo un token **mira a los demás** para entender qué significa en esta frase.

---

## Índice

1. [El problema que resuelve attention](#1-el-problema-que-resuelve-attention)
2. [La intuición: buscar en un diccionario difuso](#2-la-intuición-buscar-en-un-diccionario-difuso)
3. [Query, Key y Value](#3-query-key-y-value)
4. [Scaled Dot-Product Attention paso a paso](#4-scaled-dot-product-attention-paso-a-paso)
5. [Ejemplo numérico a mano](#5-ejemplo-numérico-a-mano)
6. [Self-Attention vs Cross-Attention](#6-self-attention-vs-cross-attention)
7. [Máscara causal: por qué el modelo no puede ver el futuro](#7-máscara-causal-por-qué-el-modelo-no-puede-ver-el-futuro)
8. [Multi-Head Attention](#8-multi-head-attention)
9. [Código simple (Python puro)](#9-código-simple-python-puro)
10. [Implementación en NumPy](#10-implementación-en-numpy)
11. [Resumen](#11-resumen)
12. [Referencias](#12-referencias)
---

## 1. El problema que resuelve attention

Después de tokenizar y pasar por la tabla de embeddings, cada token tiene **un vector fijo**, sin importar el contexto:

```
"banco" → [0.12, -0.80, 0.33, ...]   (siempre el mismo vector)
```

Pero el significado depende del contexto:

- "Me senté en el **banco** de la plaza" → asiento
- "Saqué plata del **banco**" → entidad financiera

Necesitamos un mecanismo que **mezcle información de los otros tokens** en el vector de cada token, para que "banco" termine con una representación distinta en cada frase.

Antes de los Transformers, las RNN/LSTM procesaban la secuencia token por token y "arrastraban" un estado oculto. Problemas:

- **Secuencial** → no se paraleliza bien en GPU.
- **Memoria corta** → la información de tokens lejanos se diluye.

Attention resuelve las dos cosas: **cada token mira directamente a todos los demás, en paralelo**.

---

## 2. La intuición: buscar en un diccionario difuso

Pensá en un diccionario de Python:

```python
d = {"gato": "felino", "perro": "canino"}
d["gato"]  # → "felino"   (match exacto, devuelve UN valor)
```

Attention es una versión **difusa** de esto:

- Hacés una **pregunta** (query).
- La comparás contra **todas las claves** (keys).
- En vez de devolver un solo valor, devolvés un **promedio ponderado de todos los valores** (values), donde el peso depende de qué tan parecida es cada key a tu query.

```
resultado = Σ  peso_i · value_i      con   Σ peso_i = 1
```

---

## 3. Query, Key y Value

Para cada token con embedding `x` (dimensión `d_model`), el modelo calcula **tres vectores distintos** multiplicando por tres matrices aprendidas:

```
q = x · W_Q     → "¿Qué estoy buscando?"
k = x · W_K     → "¿Qué ofrezco / cómo me identifico?"
v = x · W_V     → "¿Qué información entrego si me eligen?"
```

| Vector | Rol | Analogía |
|--------|-----|----------|
| **Query (Q)** | Lo que el token actual quiere saber | La búsqueda que escribís en Google |
| **Key (K)** | La "etiqueta" de cada token para ser encontrado | El título de cada página |
| **Value (V)** | El contenido real que se transmite | El contenido de la página |

¿Por qué tres vectores y no usar el embedding directo? Porque **lo que un token busca no es lo mismo que lo que ofrece**. Un verbo puede "buscar" a su sujeto, pero "ofrecer" información sobre la acción. Separar los roles le da al modelo mucha más flexibilidad.

`W_Q`, `W_K`, `W_V` son **parámetros entrenables**: el modelo aprende durante el entrenamiento qué preguntas hacer y qué responder.

---

## 4. Scaled Dot-Product Attention paso a paso

La fórmula completa (del paper *Attention Is All You Need*):

$$
\text{Attention}(Q, K, V) = \text{softmax}\left(\frac{QK^\top}{\sqrt{d_k}}\right) V
$$

Desarmémosla.

### Paso 1 — Scores: `Q · Kᵀ`

Producto punto entre la query de cada token y la key de todos los tokens.

> 🔗 **Conexión con lo que ya viste:** la similitud de coseno es el producto punto **normalizado** por las normas. Acá se usa el producto punto **crudo**: mide parecido, pero la magnitud también cuenta. Es más barato y el modelo aprende a manejar las escalas.

Con `n` tokens, obtenés una matriz `n × n`: la fila `i` dice cuánto le "interesa" al token `i` cada uno de los demás.

### Paso 2 — Escalar: dividir por `√d_k`

Si `d_k` (dimensión de las keys) es grande, los productos punto crecen mucho en magnitud (su varianza escala con `d_k`). Valores muy grandes hacen que el softmax quede casi *one-hot* (un 1 y el resto ~0), y ahí los gradientes se vuelven casi cero → el modelo deja de aprender.

Dividir por `√d_k` mantiene la varianza ≈ 1.

### Paso 3 — Softmax por fila

Convierte cada fila de scores en una distribución de probabilidad:

$$
\text{softmax}(s_i) = \frac{e^{s_i}}{\sum_j e^{s_j}}
$$

Ahora cada fila suma 1. Estos son los **pesos de atención**.

### Paso 4 — Ponderar los Values

Multiplicás los pesos por `V`. El resultado para cada token es una **mezcla de los values de todos los tokens**, según cuánto atendió a cada uno.

### Diagrama de flujo

```
 X (n × d_model)
   │
   ├──── · W_Q ───► Q (n × d_k) ─┐
   ├──── · W_K ───► K (n × d_k) ─┼─► Q·Kᵀ ─► ÷√d_k ─► [máscara] ─► softmax ─► pesos (n × n)
   └──── · W_V ───► V (n × d_v) ─┼───────────────────────────────────────────────┐   │
                                 │                                               ▼   ▼
                                 │                                          pesos · V
                                 │                                               │
                                 └──────────────────────────────────►  salida (n × d_v)
```

---

## 5. Ejemplo numérico a mano

Frase: **"el gato duerme"** → 3 tokens. Usamos `d_k = 4` y miramos solo la fila de **"duerme"**.

Supongamos que los productos punto `q_duerme · k_j` dieron:

| key | el | gato | duerme |
|-----|----|------|--------|
| score crudo | 1.0 | 3.0 | 2.0 |

**Escalar** por `√4 = 2`:

| | el | gato | duerme |
|-|----|------|--------|
| score / 2 | 0.5 | 1.5 | 1.0 |

**Softmax:**

```
e^0.5 = 1.649    e^1.5 = 4.482    e^1.0 = 2.718     suma = 8.849

pesos = [1.649/8.849, 4.482/8.849, 2.718/8.849]
      = [0.186,       0.506,       0.307]
```

"duerme" presta **~51% de atención a "gato"** (su sujeto), ~31% a sí mismo y ~19% a "el".

**Mezclar values** (vectores de juguete de dim 2):

```
v_el     = [1, 0]
v_gato   = [0, 1]
v_duerme = [1, 1]

salida_duerme = 0.186·[1,0] + 0.506·[0,1] + 0.307·[1,1]
              = [0.494, 0.814]
```

Ese vector `[0.494, 0.814]` es la nueva representación de "duerme", **ahora enriquecida con información de "gato"**.

---

## 6. Self-Attention vs Cross-Attention

La diferencia es **de dónde salen** Q, K y V.

| Tipo | Q viene de | K y V vienen de | Dónde se usa |
|------|-----------|-----------------|--------------|
| **Self-attention** | la misma secuencia | la misma secuencia | GPT, Claude, Llama, BERT |
| **Cross-attention** | secuencia A (ej: texto que se genera) | secuencia B (ej: texto original, imagen) | Traductores encoder-decoder (T5), modelos texto→imagen |

**Self-attention** = la secuencia se mira a sí misma. Cada token pregunta a todos los tokens de su misma frase. Es lo que usan los LLMs modernos tipo decoder-only.

---

## 7. Máscara causal: por qué el modelo no puede ver el futuro

Un LLM genera texto **prediciendo el siguiente token**. Durante el entrenamiento procesa la frase entera en paralelo, así que si no hacemos nada, el token 3 podría "espiar" al token 4… que es justo lo que tiene que predecir. Eso es trampa.

Solución: **máscara causal**. Antes del softmax, ponemos `-∞` en los scores de tokens futuros. Como `e^(-∞) = 0`, esos pesos quedan en cero.

```
              el    gato   duerme
el        [  ✓     -∞     -∞   ]
gato      [  ✓      ✓     -∞   ]
duerme    [  ✓      ✓      ✓   ]
```

Matriz triangular inferior: cada token solo ve **a sí mismo y al pasado**.

- **Decoder-only (GPT, Claude, Llama)** → usan máscara causal.
- **Encoder-only (BERT)** → sin máscara, atención bidireccional (cada token ve todo). Sirve para entender texto, no para generarlo.

---

## 8. Multi-Head Attention

### El problema con una sola cabeza

Una sola attention produce **un único** set de pesos por token. Pero un token tiene muchos tipos de relaciones a la vez:

> "La **gata** que adopté ayer **duerme** en el sillón"

Para "duerme", importan:
- **Sintaxis:** ¿quién es el sujeto? → "gata"
- **Concordancia:** género/número → "gata" (femenino, singular)
- **Localización:** ¿dónde? → "sillón"
- **Cercanía:** tokens vecinos → "en", "el"

Un solo softmax tiene que repartir el 100% entre todo eso y termina promediando señales distintas.

### La solución: varias cabezas en paralelo

En vez de una attention con dimensión `d_model`, hacemos **`h` attentions más chicas en paralelo**, cada una con sus propias `W_Q`, `W_K`, `W_V`:

$$
\text{head}_i = \text{Attention}(X W_Q^{(i)},\ X W_K^{(i)},\ X W_V^{(i)})
$$

$$
\text{MultiHead}(X) = \text{Concat}(\text{head}_1, \dots, \text{head}_h)\ W_O
$$

Cada cabeza trabaja en dimensión `d_k = d_model / h`, así que **el costo total es similar al de una sola cabeza grande**.

```
                    X (n × d_model)
          ┌───────────┼───────────┬───────────┐
          ▼           ▼           ▼           ▼
       head 1      head 2      head 3  ...  head h      (cada una: n × d_k)
     (sintaxis)  (corefer.)  (posición)
          └───────────┴─────┬─────┴───────────┘
                            ▼
                Concat → (n × d_model)
                            ▼
                         · W_O                           (mezcla lo que encontró cada cabeza)
                            ▼
                    salida (n × d_model)
```

### ¿Qué aprenden las cabezas?

Nadie les dice qué hacer: **se especializan solas** durante el entrenamiento. Investigaciones de interpretabilidad encontraron cabezas que:

- Atienden al **token anterior**.
- Conectan **pronombres con su referente** ("ella" → "María").
- Siguen **relaciones sintácticas** (verbo → sujeto, adjetivo → sustantivo).
- **Induction heads:** detectan patrones tipo "A B … A → predecí B". Son clave para el *in-context learning* (aprender de ejemplos en el prompt).

Muchas cabezas son redundantes o difíciles de interpretar; no todas tienen un rol limpio.

---

## 9. Código simple (Python puro)

> 📄 Archivo: [`attention_simple.py`](attention_simple.py) — correr con `python3 attention_simple.py`

El mismo ejemplo de la sección 5, pero en código y sin librerías. Las keys están elegidas para que los scores den igual que en el ejemplo a mano.

```python
import math

# Frase: "el gato duerme" — miramos qué atiende "duerme"
tokens = ["el", "gato", "duerme"]

q_duerme = [1.0, 0.5, 0.0, 1.0]          # lo que "duerme" busca
keys = {
    "el":     [0.5, 0.0, 0.5, 0.5],
    "gato":   [1.5, 1.0, 0.0, 1.0],
    "duerme": [1.0, 0.0, 1.0, 1.0],
}
values = {
    "el":     [1, 0],
    "gato":   [0, 1],
    "duerme": [1, 1],
}

def dot(a, b):
    return sum(x * y for x, y in zip(a, b))

def softmax(xs):
    exps = [math.exp(x) for x in xs]
    total = sum(exps)
    return [e / total for e in exps]

d_k = len(q_duerme)

# 1. Scores: producto punto query · key, escalado por √d_k
scores = [dot(q_duerme, keys[t]) / math.sqrt(d_k) for t in tokens]

# 2. Softmax → pesos de atención
pesos = softmax(scores)

# 3. Promedio ponderado de los values
salida = [sum(p * values[t][i] for p, t in zip(pesos, tokens)) for i in range(2)]

for t, s, p in zip(tokens, scores, pesos):
    print(f"{t:>7} | score {s:.2f} | peso {p:.3f}")
print("salida de 'duerme':", [round(x, 3) for x in salida])
```

Salida:

```
     el | score 0.50 | peso 0.186
   gato | score 1.50 | peso 0.506
 duerme | score 1.00 | peso 0.307
salida de 'duerme': [0.494, 0.814]
```

Son tres pasos: **producto punto → softmax → promedio ponderado**. Eso es attention. La versión con NumPy de abajo hace lo mismo para todos los tokens a la vez y le suma la máscara causal y las múltiples cabezas.

---

## 10. Implementación en NumPy

> 📄 Archivo: [`attention_numpy.py`](attention_numpy.py) — requiere `pip install numpy`, después `python3 attention_numpy.py`

Hace lo mismo que el ejemplo anterior pero con matrices: todos los tokens a la vez, con máscara causal y 4 cabezas (`d_model = 16`, 6 tokens).

Fijate en la salida:

- La forma de salida es **igual a la de entrada** `(n, d_model)` → por eso se pueden apilar bloques.
- Los pesos de cada cabeza son **triangulares inferiores** (máscara causal).
- Cada fila suma 1.

Con pesos aleatorios los patrones no significan nada; en un modelo entrenado, las `W` están ajustadas para que esos pesos capturen relaciones útiles.

---

## 11. Resumen

| Concepto | En una línea |
|----------|-------------|
| **Attention** | Promedio ponderado de values, donde los pesos salen de comparar una query con keys |
| **Q / K / V** | Proyecciones aprendidas del embedding: qué busco / cómo me encuentran / qué entrego |
| **`√d_k`** | Escala los scores para que el softmax no se sature |
| **Softmax** | Convierte scores en pesos que suman 1 |
| **Self-attention** | Q, K y V salen de la misma secuencia: la frase se mira a sí misma |
| **Máscara causal** | Bloquea el futuro; necesaria para generar texto |
| **Multi-head** | Varias attentions chicas en paralelo, cada una aprende un tipo de relación distinto |
| **W_O** | Mezcla los resultados de todas las cabezas |

**La idea central:** attention convierte embeddings *estáticos* (un vector por palabra del vocabulario) en representaciones *contextuales* (un vector por palabra **en esta frase**).

---

**Siguiente:** attention es una pieza; apilada con otras forma el modelo completo → [04. Arquitectura Transformer](../04-arquitectura-transformer-decoder-only/README.md).

---

## 12. Referencias

- Vaswani et al., 2017 — [*Attention Is All You Need*](https://arxiv.org/abs/1706.03762) (el paper original del Transformer)
- Jay Alammar — [*The Illustrated Transformer*](https://jalammar.github.io/illustrated-transformer/)
- 3Blue1Brown — [*Attention in transformers, visually explained*](https://www.youtube.com/watch?v=eMlx5fFNoYc)
- Andrej Karpathy — [*Let's build GPT: from scratch, in code, spelled out*](https://www.youtube.com/watch?v=kCc8FmEb1nY)
- Olsson et al., 2022 — [*In-context Learning and Induction Heads*](https://transformer-circuits.pub/2022/in-context-learning-and-induction-heads/index.html)
