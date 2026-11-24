# Embeddings y similitud coseno

> Viene de [01. Tokens](../01-tokens-y-tokenizacion/README.md): el texto ya es una lista de números (IDs). Pero un ID es solo una etiqueta: `9081` no está "más cerca" de `9082` en ningún sentido. Este tema explica cómo cada token pasa a tener un **significado** que se puede medir.

---

## 1. Qué es un embedding

Un **embedding** es una lista de números (un **vector**) que representa el significado de algo: un token, una palabra o un texto entero.

```
"perro"    →  [ 0.21, -0.43,  0.88, …,  0.05 ]
"can"      →  [ 0.19, -0.40,  0.85, …,  0.07 ]   ← muy parecido
"impuesto" →  [-0.62,  0.11, -0.05, …,  0.93 ]   ← muy distinto
```

Cada número es una coordenada. Con 2 números, cada palabra sería un punto en un plano; un embedding usa cientos o miles de números, pero la idea es la misma: **un mapa del significado, donde lo parecido queda cerca**. Nadie decide qué significa cada coordenada: sale del entrenamiento.

---

## 2. Dentro del LLM: la tabla de embeddings

Lo primero que hace un LLM con cada ID es buscarlo en una tabla: una fila por token del vocabulario.

```
tabla de embeddings (GPT-2: 50.257 filas × 768 números)

ID 412   ("▁los")    →  fila 412   →  [ 0.12, -0.48,  0.33, …,  0.07 ]
ID 9081  ("▁gatit")  →  fila 9081  →  [-0.40,  0.22, -0.05, …, -0.31 ]
```

Al principio esa tabla tiene números al azar. Durante el entrenamiento se ajusta junto con el resto del modelo, y los tokens que se usan de forma parecida terminan con vectores parecidos.

---

## 3. Por qué no alcanza con una lista de palabras

La forma más simple de convertir palabras en vectores es **one-hot**: un vector tan largo como el vocabulario, con un único `1` en la posición de la palabra.

```
perro → [1, 0, 0, …]
can   → [0, 1, 0, …]
avión → [0, 0, 1, …]
```

Problema: todos quedan **a la misma distancia de todos**. Para este sistema, `perro` y `can` son tan distintos como `perro` y `avión`. Contar qué palabras tiene un texto (*bag of words*) tiene el mismo defecto: no sabe que `auto` y `coche` son lo mismo.

Un embedding resuelve eso: usa pocos números (no miles de ceros) y ubica a `perro` cerca de `can`.

---

## 4. Cómo se mide "cerca": similitud coseno

Cada vector es una flecha. La **similitud coseno** mide el **ángulo** entre dos flechas, sin importar lo largas que sean:

- Apuntan al mismo lado → **1** (mismo significado)
- Forman un ángulo recto → **0** (sin relación)
- Apuntan a lados opuestos → **−1** (con texto casi no pasa)

La cuenta:

```
                    a · b         a · b  →  multiplicar coordenada a coordenada y sumar
   coseno(a, b) = ─────────       |a|    →  largo de la flecha: √(suma de los cuadrados)
                   |a| |b|

a = (1, 2, 2)    b = (2, 1, 2)

a · b = 1×2 + 2×1 + 2×2 = 8
|a| = |b| = √(1 + 4 + 4) = 3

coseno = 8 / (3 × 3) = 0,889   → muy parecidos
```

**Por qué el ángulo y no la distancia:** `(2, 4, 4)` es `a` multiplicado por 2. Es una flecha más larga, pero apunta exactamente al mismo lado: coseno = 1. En embeddings, **la dirección es lo que lleva el significado**; el largo suele depender de detalles sin importancia.

**El truco práctico:** si todos los vectores se ajustan para medir 1 (se **normalizan**), el coseno es simplemente `a · b`, que es lo más barato de calcular. Por eso casi todos los sistemas normalizan.

Ojo: cada modelo tiene su propia escala. En uno, dos textos sin relación dan 0,1; en otro, 0,7. **Lo confiable es el orden** (cuál es más parecido), no el número.

---

## 5. Cómo un vector aprende a "significar" algo

**Una palabra se conoce por las palabras que la acompañan.** `perro` y `can` aparecen rodeadas de `ladra`, `correa`, `paseo`. Si se entrena un sistema para adivinar las palabras vecinas, las que tienen vecinas parecidas terminan con vectores parecidos. Así funcionó **word2vec** (2013), y salieron relaciones como direcciones en el mapa:

```
rey − hombre + mujer  ≈  reina
París − Francia + Italia  ≈  Roma
```

Límite: **un solo vector por palabra**. `banco` (para sentarse) y `banco` (de plata) quedan en el mismo punto.

**Vectores según el contexto.** Los modelos modernos leen la oración entera, y el vector de cada token cambia según lo que lo rodea: `banco` en "me senté en el banco de la plaza" y en "saqué plata del banco" termina en lugares distintos. El mecanismo que hace eso es la **atención** ([tema 03](../03-atencion-self-attention-multi-head/README.md)).

**Modelos de embeddings.** Para buscar o comparar textos se usan modelos aparte (Voyage, OpenAI `text-embedding-3`, E5, BGE…) que devuelven **un vector por texto completo**. Se entrenan con millones de **pares** que significan lo mismo (pregunta ↔ respuesta, título ↔ artículo, frase ↔ traducción): se acercan los pares correctos y se alejan los demás.

Cada modelo arma **su propio mapa**: los vectores de un modelo no se pueden comparar con los de otro.

---

## 6. Para qué se usan: buscar por significado

Con un vector por texto se puede encontrar lo parecido aunque no comparta ninguna palabra:

```
guardar:  documentos → partir en pedazos → modelo de embeddings → vectores → base de datos
buscar:   pregunta   → mismo modelo      → vector → los más parecidos
```

```
"¿cómo reseteo mi contraseña?"  vs  "olvidé la clave de mi cuenta"   →  0,86  ✓ lo encuentra
"¿cómo reseteo mi contraseña?"  vs  "receta de empanadas"            →  0,08
```

Es la base de RAG (darle al LLM documentos relevantes antes de responder), buscadores internos, recomendaciones y detección de duplicados. Con millones de documentos no se compara contra todos: se usan índices que encuentran los más cercanos sin revisar cada uno.

**Lo que no hace bien:**
- **Parecido no es lo mismo que relevante.** "El producto funciona" y "el producto no funciona" quedan muy cerca: hablan de lo mismo, aunque digan lo contrario.
- **Códigos y nombres exactos.** `ERR-4012` y `ERR-4021` son casi iguales para un embedding. Para eso se combina con la búsqueda por palabras de siempre (búsqueda **híbrida**).
- **Ocupan memoria.** 1 millón de vectores de 1.536 números ocupan unos 6 GB. Se pueden achicar guardando cada número con menos precisión, perdiendo muy poca calidad.

---

## Resumen

- Un **embedding** es una lista de números que ubica algo en un mapa del significado: lo parecido queda cerca.
- Dentro del LLM, cada token arranca con un vector sacado de una **tabla que se aprende** al entrenar.
- La cercanía se mide con la **similitud coseno**: el ángulo entre dos vectores.
- Los vectores aprenden significado por el **contexto**: qué palabras aparecen cerca.
- Fuera del LLM, sirven para **buscar por significado** (RAG), con sus límites: negaciones y palabras exactas.

**Siguiente:** cada token tiene su vector, pero todavía no sabe nada de los tokens que lo rodean → [03. Atención](../03-atencion-self-attention-multi-head/README.md).
