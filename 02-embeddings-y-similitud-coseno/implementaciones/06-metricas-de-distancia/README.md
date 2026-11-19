# Métricas: coseno, producto punto y euclidiana

Las bases vectoriales piden elegir una métrica al crear el índice. Hay tres principales, y la buena noticia es que **con vectores normalizados las tres ordenan igual**.

## Las tres

| Métrica | Qué mide | Fórmula en palabras | Mejor resultado |
|---|---|---|---|
| **Coseno** | El ángulo | Producto punto dividido por las dos normas | Mayor (1) |
| **Producto punto** | Ángulo y largo a la vez | Multiplicar coordenada a coordenada y sumar | Mayor |
| **Euclidiana (L2)** | Distancia en línea recta entre las puntas | Raíz de la suma de las diferencias al cuadrado | Menor (0) |

```
        ▲
        │   ● c
        │  ╱
        │ ╱    ● b
        │╱   ╱
        ● a ╱          coseno:     mira el ángulo entre las flechas
        │  ╱           euclidiana: mira la distancia entre los puntos
        │ ╱            producto punto: ángulo × largo de cada una
        └──────────►
```

## El mismo ejemplo con las tres

```
a = (1, 2, 2)     b = (2, 1, 2)     c = (2, 4, 4)  ← a × 2

                 coseno     producto punto    euclidiana
a vs b           0,889            8              1,41
a vs c           1               18              3,00
```

Las métricas **no están de acuerdo**:
- Por **coseno**, `c` es el más parecido a `a` (misma dirección).
- Por **producto punto**, también `c`, y por mucho (es más largo).
- Por **euclidiana**, `b` está más cerca (las puntas están más próximas).

Con vectores sin normalizar, elegir la métrica cambia el resultado.

## Con vectores normalizados, dan lo mismo

Si todos los vectores miden 1:

```
producto punto  =  coseno
euclidiana²     =  2 − 2 × coseno
```

La segunda igualdad dice que la distancia euclidiana **baja exactamente cuando el coseno sube**. Se ordenan igual, solo que en sentido inverso:

| Coseno | Distancia euclidiana |
|---|---|
| 1 | 0 |
| 0,9 | 0,45 |
| 0,5 | 1 |
| 0 | 1,41 |
| −1 | 2 |

Por eso lo habitual es: **normalizar todo y usar producto punto**, que es la operación más barata. El ranking es el mismo que con coseno.

## Cuándo el largo sí importa

Hay modelos entrenados con producto punto **sin** normalizar, donde el largo del vector lleva información (por ejemplo, qué tan "confiado" o qué tan informativo es un documento). En esos casos normalizar empeora los resultados.

La regla es simple: **usar la métrica con la que se entrenó el modelo.** Está en su documentación o en su ficha (*model card*). Si dice coseno, normalizá y usá producto punto o coseno. Si dice producto punto, no normalices.

## Otras que aparecen

| Métrica | Dónde aparece |
|---|---|
| **Manhattan (L1)** | Suma de las diferencias en valor absoluto. Poco usada con embeddings de texto. |
| **Hamming** | Cuántos bits difieren. Para vectores binarios (ver [`08-dimensiones-y-cuantizacion`](../08-dimensiones-y-cuantizacion)). |
| **Jaccard** | Proporción de elementos en común. Para conjuntos y vectores dispersos, no para embeddings densos. |

## ✅ / ❌

- ✅ Con vectores normalizados, la elección de métrica no cambia el ranking: elegí la más barata.
- ✅ El producto punto es la operación que más rápido corre en CPU y GPU.
- ❌ Con vectores sin normalizar, cada métrica da un ranking distinto.
- ❌ Si la base vectorial usa una métrica y el modelo se entrenó con otra, la búsqueda empeora sin ningún error visible.
- ❌ "Distancia" y "similitud" van en sentidos opuestos: un umbral copiado de una a la otra filtra justo al revés.
