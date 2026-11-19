# Embeddings y similitud coseno

Un **embedding** es una lista de números (un **vector**) que representa el *significado* de un texto. Un modelo de embeddings recibe texto y devuelve siempre un vector del mismo tamaño, por ejemplo 1024 números. La gracia está en que **textos que significan algo parecido quedan cerca** en ese espacio, aunque no compartan ni una palabra.

```
"¿cómo reseteo mi contraseña?"  ──► modelo ──►  [ 0.12, -0.48,  0.33, ...,  0.07 ]  ─┐
                                                                                      ├─►  coseno = 0,86  (muy parecidos)
"olvidé la clave de mi cuenta"  ──► modelo ──►  [ 0.10, -0.51,  0.29, ...,  0.11 ]  ─┤
                                                                                      │
"receta de empanadas salteñas"  ──► modelo ──►  [-0.40,  0.22, -0.05, ..., -0.31 ]  ─┴─►  coseno = 0,08  (nada que ver)
```

Para medir qué tan cerca están dos vectores se usa casi siempre la **similitud coseno**: el coseno del ángulo entre ellos. Con eso se arma búsqueda semántica, RAG, recomendaciones, detección de duplicados, clustering y clasificación.

## Por qué no comparar palabras

| Enfoque | Qué compara | Problema |
|---|---|---|
| **Texto exacto** | Caracteres iguales | `contraseña` y `clave` no coinciden en nada |
| **Palabras en común (bag of words, TF-IDF)** | Qué palabras aparecen y cuánto | No sabe que `auto` y `coche` son lo mismo; vectores enormes y casi todos ceros |
| **Embeddings** | Posición en un espacio de significado | Captura sinónimos, paráfrasis y hasta otros idiomas. Es lo que se usa |

## Conceptos clave

| Concepto | Qué es |
|---|---|
| **Vector** | Una lista ordenada de números. Un embedding es un vector. |
| **Dimensión** | Cuántos números tiene el vector (384, 768, 1024, 1536, 3072...). Fija para cada modelo. |
| **Espacio vectorial** | El "mapa" donde viven todos los vectores. Cada dimensión es un eje. |
| **Denso / disperso** | Denso: todos los números importan (embeddings). Disperso: casi todos son cero (bag of words). |
| **Norma (magnitud)** | El "largo" del vector: raíz de la suma de los cuadrados. |
| **Normalizar** | Dividir el vector por su norma para que mida 1. Queda solo la dirección. |
| **Producto punto** | Multiplicar coordenada a coordenada y sumar. Base de casi todas las métricas. |
| **Similitud coseno** | Producto punto dividido por las dos normas. Va de −1 a 1 y solo mira el ángulo. |
| **Distancia euclidiana** | La distancia "en línea recta" entre dos puntos. |
| **Embedding estático** | Un vector fijo por palabra, sin importar el contexto (word2vec, GloVe). |
| **Embedding contextual** | El vector depende de la oración completa (modelos basados en transformers). |
| **Pooling** | Cómo se pasa de un vector por token a un único vector por texto (promedio, `[CLS]`...). |
| **Aprendizaje contrastivo** | Entrenar acercando pares que significan lo mismo y alejando los que no. |
| **Top-k** | Los k vectores más parecidos a una consulta. |
| **ANN** | *Approximate Nearest Neighbors*: búsqueda aproximada para no comparar contra todo. |
| **Base vectorial** | Base de datos que guarda vectores y los busca por similitud (pgvector, Qdrant, FAISS...). |
| **Chunk** | El pedazo de documento que se convierte en un embedding. |

## Cómo se llegó a los embeddings actuales

### 1. One-hot y bag of words

Cada palabra es una dimensión. Un texto es un vector que cuenta qué palabras tiene.
- ✅ Simple, interpretable, no hay que entrenar nada.
- ❌ Vectores del tamaño del vocabulario, casi todo ceros. `perro` y `can` son tan distintos como `perro` y `avión`.

### 2. Embeddings estáticos (word2vec, GloVe, FastText)

Se entrena una red chica para predecir qué palabras aparecen juntas. De rebote, cada palabra termina con un vector denso de 100–300 dimensiones donde los sinónimos quedan cerca. De acá sale el famoso `rey − hombre + mujer ≈ reina`.
- ✅ Densos, chicos, capturan relaciones de significado.
- ❌ Un solo vector por palabra: `banco` (para sentarse) y `banco` (de plata) son el mismo punto. No hay vector para una oración entera.

### 3. Embeddings contextuales (BERT, Sentence-BERT)

Un transformer lee la oración completa y da un vector por token que depende de sus vecinos. Para tener uno por oración se hace **pooling**. Sentence-BERT (2019) mostró que hay que **ajustar** el modelo para que esos vectores sirvan para comparar.
- ✅ Resuelve la polisemia, representa oraciones y párrafos.
- ❌ BERT "crudo" con promedio da similitudes malas: hace falta entrenamiento específico.

### 4. Modelos de embeddings modernos

Transformers entrenados con **aprendizaje contrastivo** sobre cientos de millones de pares (pregunta–respuesta, título–cuerpo, traducciones). Son lo que se usa hoy en producción.
- ✅ Multilingües, entienden código, aceptan miles de tokens, varios permiten elegir la dimensión.
- ❌ Cada modelo tiene su propio espacio: los vectores de uno no se comparan con los de otro.
- Ejemplos: Voyage, OpenAI `text-embedding-3`, Cohere Embed, Gemini Embedding y abiertos como E5, BGE, GTE, Nomic o Jina.

| | Bag of words | word2vec | BERT + pooling | Modelos modernos |
|---|---|---|---|---|
| Tipo de vector | Disperso | Denso | Denso | Denso |
| Dimensión | Tamaño del vocabulario | 100–300 | 768 | 384–4096 |
| Entiende sinónimos | No | Sí | Sí | Sí |
| Depende del contexto | No | No | Sí | Sí |
| Sirve para comparar oraciones | Poco | Poco | Poco (sin ajuste) | Sí |

## Similitud coseno

Mide el **ángulo** entre dos vectores, sin importar lo largos que sean:

```
                    a · b              suma de (aᵢ × bᵢ)
   coseno(a, b) = ─────────  =  ───────────────────────────────
                   |a| |b|       √(suma de aᵢ²) × √(suma de bᵢ²)
```

| Valor | Ángulo | Qué significa |
|---|---|---|
| **1** | 0° | Misma dirección: mismo significado |
| **0** | 90° | Sin relación |
| **−1** | 180° | Direcciones opuestas (en la práctica casi no aparece con embeddings de texto) |

Ejemplo a mano con vectores de 3 dimensiones:

```
a = (1, 2, 2)     |a| = √(1 + 4 + 4) = 3
b = (2, 1, 2)     |b| = √(4 + 1 + 4) = 3

a · b = 1×2 + 2×1 + 2×2 = 8

coseno(a, b) = 8 / (3 × 3) = 0,889
```

Y por qué se usa coseno y no distancia: `c = (2, 4, 4)` es `a` multiplicado por 2. Están a distancia 3 uno del otro, pero apuntan exactamente al mismo lado: `coseno(a, c) = 1`. En embeddings lo que lleva el significado es la **dirección**, no el largo.

Un detalle que importa en la práctica: **si los vectores están normalizados (norma 1), el coseno es igual al producto punto**, y ordenar por distancia euclidiana da el mismo ranking. Por eso muchas bases vectoriales normalizan y usan producto punto, que es más barato de calcular.

> El detalle de la fórmula, la geometría y la comparación con otras métricas está en [`05-similitud-coseno`](implementaciones/05-similitud-coseno) y [`06-metricas-de-distancia`](implementaciones/06-metricas-de-distancia).

## Costo y almacenamiento

Generar embeddings se cobra **por token de input** (no hay output), y es mucho más barato que un LLM. Lo que suele pesar es **guardar y buscar** los vectores:

```
1.000.000 de chunks × 1536 dimensiones × 4 bytes (float32)  =  6,1 GB   ← y casi siempre tiene que estar en RAM
1.000.000 de chunks × 1536 dimensiones × 1 byte  (int8)     =  1,5 GB
1.000.000 de chunks × 1536 dimensiones × 1 bit   (binario)  =  0,19 GB
```

Tres cosas que se desprenden de esto:
1. **La dimensión se paga en memoria, en cada búsqueda y para siempre**: 3072 dimensiones cuestan el doble que 1536 y no siempre rinden el doble.
2. **Cambiar de modelo obliga a re-embeddear todo**: los vectores viejos no sirven con el modelo nuevo.
3. **Los tokens importan acá también**: el límite de cada modelo se mide en tokens (ver el proyecto [`tokens`](../tokens)), y lo que se pasa se trunca o da error.

## Errores comunes

### 1. Comparar vectores de modelos distintos
Dos modelos con la misma dimensión siguen teniendo espacios distintos: el coseno entre sus vectores no significa nada. Lo mismo pasa entre versiones del mismo modelo.
→ Guardar con cada vector qué modelo y versión lo generó, y re-indexar todo al cambiar.

### 2. No normalizar
Usar producto punto con vectores que no miden 1: los textos con vectores "más largos" ganan siempre, sin ser más parecidos.
→ Normalizar al guardar y al consultar, o usar coseno directamente.

### 3. Usar un umbral fijo de similitud
"Si el coseno da más de 0,8 es lo mismo". Cada modelo tiene su propio rango: en algunos, dos textos sin relación ya dan 0,7.
→ Calibrar el umbral con ejemplos reales del modelo que usás, o trabajar con rankings en vez de números absolutos.

### 4. Embeddear la consulta igual que los documentos
Muchos modelos son asimétricos: esperan un prefijo o un `input_type` distinto para la pregunta y para el documento. Si no se lo pasás, la búsqueda empeora en silencio.
→ Leer la documentación del modelo y usar el modo de consulta y de documento que corresponde.

### 5. Cortar mal los chunks
Un chunk enorme promedia demasiados temas y no se parece a nada; uno chiquito pierde el contexto. Y si pasa el límite de tokens del modelo, se trunca.
→ Cortar por estructura (secciones, párrafos), con un tamaño que el modelo acepte y algo de solapamiento.

### 6. Confundir "parecido" con "relevante"
`el producto funciona` y `el producto no funciona` dan una similitud altísima: hablan de lo mismo. Los embeddings capturan el tema mejor que la negación o la intención.
→ Un reranker sobre los primeros resultados, o reglas para los casos que importan.

### 7. Buscar palabras exactas con embeddings
Códigos de error, SKUs, nombres propios raros, números de factura: el embedding los "suaviza" y trae cosas parecidas en vez de la exacta.
→ Búsqueda híbrida: embeddings + búsqueda por palabras clave (BM25), y combinar los rankings.

### 8. No medir
Elegir modelo, chunking, umbral o índice "a ojo", y no saber cuánto se pierde con la búsqueda aproximada.
→ Un set de consultas con sus respuestas correctas, y medir recall@k y MRR en cada cambio.

## Estructura

- [`implementaciones/`](implementaciones): cada pieza del mecanismo, explicada con diagramas y ejemplos a mano.
  1. [`01-one-hot-y-bag-of-words`](implementaciones/01-one-hot-y-bag-of-words): representar texto contando palabras, y por qué no alcanza.
  2. [`02-word2vec`](implementaciones/02-word2vec): aprender un vector por palabra a partir de sus vecinas.
  3. [`03-embeddings-contextuales`](implementaciones/03-embeddings-contextuales): transformers, un vector por token y pooling.
  4. [`04-entrenamiento-contrastivo`](implementaciones/04-entrenamiento-contrastivo): cómo se entrena un modelo de embeddings moderno.
  5. [`05-similitud-coseno`](implementaciones/05-similitud-coseno): la fórmula paso a paso y qué mide de verdad.
  6. [`06-metricas-de-distancia`](implementaciones/06-metricas-de-distancia): coseno, producto punto y euclidiana, y cuándo dan lo mismo.
  7. [`07-busqueda-semantica`](implementaciones/07-busqueda-semantica): de buscar contra todo a los índices aproximados (HNSW, IVF).
  8. [`08-dimensiones-y-cuantizacion`](implementaciones/08-dimensiones-y-cuantizacion): achicar vectores sin perder (casi) nada.
- [`errores/`](errores): cada error común, cómo se ve y cómo se arregla.
  1. [`01-mezclar-modelos`](errores/01-mezclar-modelos): vectores de modelos o versiones distintas no se comparan.
  2. [`02-no-normalizar`](errores/02-no-normalizar): el largo del vector se cuela en el ranking.
  3. [`03-umbral-fijo`](errores/03-umbral-fijo): un 0,8 no significa lo mismo en todos los modelos.
  4. [`04-query-y-documento-iguales`](errores/04-query-y-documento-iguales): modelos asimétricos usados como simétricos.
  5. [`05-chunks-mal-cortados`](errores/05-chunks-mal-cortados): muy largos, muy cortos o truncados en silencio.
  6. [`06-parecido-no-es-relevante`](errores/06-parecido-no-es-relevante): negaciones, intención y temas cercanos.
  7. [`07-palabras-exactas`](errores/07-palabras-exactas): códigos, IDs y nombres propios necesitan búsqueda por palabras.
  8. [`08-no-medir`](errores/08-no-medir): sin un set de evaluación todo es a ojo.

Este proyecto es solo explicación: no hay código. Cada carpeta tiene un `README.md` con el concepto, diagramas, ejemplos hechos a mano y los ✅ / ❌.

## Plan del proyecto

Para pasar de la teoría a ver números reales:

1. **Coseno a mano**: calcular la similitud de los vectores chicos del ejemplo y comprobar que normalizar + producto punto da lo mismo.
2. **Un modelo real**: embeddear 20 frases (sinónimos, paráfrasis, negaciones, otro idioma) y armar la matriz de similitudes.
3. **Comparar modelos**: repetir el paso 2 con dos modelos distintos y ver que los rangos de coseno no son los mismos.
4. **Búsqueda semántica**: indexar un conjunto de documentos, buscar por fuerza bruta y después con un índice ANN, y medir cuánto recall se pierde.
5. **Achicar**: truncar dimensiones y cuantizar, y medir el impacto en memoria y en recall.
6. **Romperlo a propósito**: reproducir los errores de arriba con un modelo real.
