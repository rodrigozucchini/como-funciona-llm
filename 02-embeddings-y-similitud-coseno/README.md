# Embeddings y similitud coseno en LLM

Cómo los modelos convierten texto en números y cómo comparamos esos números para saber si dos textos "significan lo mismo".

---

## 1. ¿Qué es un embedding?

Un **embedding** es una lista de números (un vector) que representa el **significado** de un texto.

```
"perro"        → [0.21, -0.43, 0.88, ..., 0.05]   (ej. 768 números)
"cachorro"     → [0.19, -0.40, 0.85, ..., 0.07]   ← muy parecido
"impuesto"     → [-0.62, 0.11, -0.05, ..., 0.93]  ← muy distinto
```

Idea clave: **textos con significado parecido quedan cerca en el espacio vectorial**. No importa si usan las mismas palabras: "auto" y "vehículo" quedan cerca.

Dimensiones típicas: 384, 768, 1024, 1536, 3072 (depende del modelo).

### Tipos que vas a ver

| Tipo | Qué representa | Uso típico |
|---|---|---|
| Embedding de token | Una palabra/fragmento dentro del LLM | Primera capa del modelo |
| Embedding de oración/documento | Un texto completo | Búsqueda semántica, RAG |

Este repo se enfoca en el segundo: el que se usa para **buscar y comparar textos**.

---

## 2. ¿Por qué hace falta "comparar" vectores?

Una vez que tenés textos como vectores, la pregunta es: **¿qué tan parecidos son dos vectores?** Con eso podés:

- Buscar documentos relevantes para una pregunta (RAG).
- Detectar duplicados o textos casi iguales.
- Recomendar contenido similar.
- Clasificar o agrupar (clustering) textos.

---

## 3. Similitud coseno

Mide el **ángulo** entre dos vectores, ignorando su largo.

```
				  A · B
cos(A, B) = ───────────────
			 ‖A‖ × ‖B‖
```

- `A · B` = producto punto (multiplicás componente a componente y sumás).
- `‖A‖` = norma o largo del vector (`√(a₁² + a₂² + ...)`).

### Cómo se lee el resultado

```
 1.0  → misma dirección   (significado muy parecido)
 0.0  → perpendiculares   (sin relación)
-1.0  → direcciones opuestas
```

En la práctica, con embeddings de texto casi todos los valores caen entre **0 y 1**.

### Ejemplo a mano

```
A = [1, 0]
B = [1, 1]

A · B   = 1×1 + 0×1 = 1
‖A‖     = 1
‖B‖     = √2 ≈ 1.414

cos     = 1 / (1 × 1.414) ≈ 0.707   (ángulo de 45°)
```

### ¿Por qué coseno y no distancia común?

Porque nos importa la **dirección** (el significado), no el **largo** del vector. Un texto largo y uno corto sobre el mismo tema pueden tener vectores de distinto largo pero la misma dirección. El coseno los ve como iguales.

---

## 4. Código mínimo (Python)

```python
import numpy as np

def cosine_similarity(a, b):
	a, b = np.array(a), np.array(b)
	return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

print(cosine_similarity([1, 0], [1, 1]))   # 0.7071...
print(cosine_similarity([1, 2, 3], [2, 4, 6]))  # 1.0 (misma dirección)
```

Con un modelo real:

```python
from sentence_transformers import SentenceTransformer

model = SentenceTransformer("all-MiniLM-L6-v2")
textos = ["Tengo un perro", "Mi mascota es un cachorro", "Cómo pagar impuestos"]
emb = model.encode(textos, normalize_embeddings=True)

# Con vectores normalizados, coseno == producto punto
print(emb[0] @ emb[1])   # alto
print(emb[0] @ emb[2])   # bajo
```

---

## 5. Normalización: el truco que acelera todo

Si normalizás los vectores (largo = 1), entonces:

```
cos(A, B) = A · B
```

Se evita dividir por las normas y la búsqueda es más rápida. Por eso muchos modelos y bases vectoriales trabajan con vectores normalizados.

---

## 6. Dónde se usa en un sistema real (RAG)

```
Documentos ──► embeddings ──► base vectorial (índice)
									▲
Pregunta ───► embedding ──► similitud coseno ──► top-k fragmentos
													  │
													  ▼
										   se los pasás al LLM
										   como contexto
```

En PostgreSQL con **pgvector**, el operador `<=>` devuelve la **distancia coseno** (`1 - similitud`), así que ordenás de menor a mayor:

```sql
SELECT contenido
FROM documentos
ORDER BY embedding <=> '[0.12, -0.4, ...]'
LIMIT 5;
```

---

## 7. Errores comunes

1. **Comparar embeddings de modelos distintos.** Cada modelo tiene su propio "espacio"; los números no son comparables entre modelos.
2. **Cambiar de modelo y no reindexar.** Si cambiás el modelo, hay que recalcular todos los embeddings guardados.
3. **Creer que 0.8 es "80% parecido".** No es un porcentaje. Es un ángulo; la escala depende del modelo.
4. **Usar un umbral fijo universal.** Un corte de 0.75 puede ir bien en un modelo y mal en otro. Se calibra con tus propios datos.
5. **Mezclar producto punto y coseno sin normalizar.** Si los vectores no están normalizados, dan resultados distintos.
6. **Fragmentos (chunks) mal armados.** Muy largos diluyen el significado; muy cortos pierden contexto.
7. **Ignorar los prefijos del modelo.** Algunos modelos (ej. familia E5) piden `query:` y `passage:` según el texto.
8. **Confundir similar con relevante.** Dos textos pueden ser parecidos en tema y aun así no responder la pregunta.
9. **Negaciones y matices.** "Me gusta" y "no me gusta" suelen quedar cerca. Para casos finos, sumá un reranker.
10. **No truncar bien.** Cada modelo tiene un máximo de tokens; lo que lo excede se corta en silencio.

---

## 8. Límites y mejoras

- Con millones de vectores, comparar uno por uno es lento → se usan índices aproximados (**ANN**, como HNSW o IVF).
- La búsqueda por embeddings se puede combinar con búsqueda por palabras clave (**búsqueda híbrida**).
- Un **reranker** reordena los mejores resultados con más precisión.

---

## 9. Resumen rápido

| Concepto | En una línea |
|---|---|
| Embedding | Vector que representa el significado de un texto |
| Similitud coseno | Ángulo entre dos vectores (1 = igual, 0 = sin relación) |
| Normalizar | Dejar el largo en 1; coseno pasa a ser producto punto |
| Distancia coseno | `1 - similitud coseno` |
| Regla de oro | Mismo modelo para indexar y para consultar |