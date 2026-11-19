# Entrenamiento contrastivo

Es como se entrena un modelo de embeddings moderno. La idea es la misma que el negative sampling de word2vec, pero con textos enteros: **acercar los pares que significan lo mismo y alejar los que no**.

**Ejemplo real:** Sentence-BERT, E5, BGE, GTE, y los modelos de embeddings comerciales. Todos se entrenan así, con distintas recetas de datos.

## Los datos: pares

Lo que se necesita son pares **(ancla, positivo)**: dos textos que deberían quedar cerca.

| Ancla | Positivo | De dónde sale |
|---|---|---|
| Pregunta de un foro | La respuesta aceptada | Stack Exchange, Reddit |
| Título de un artículo | El primer párrafo | Wikipedia, noticias |
| Consulta de búsqueda | La página que se clickeó | Logs de buscadores |
| Oración en inglés | Su traducción | Corpus paralelos |
| Docstring | La función | Repositorios de código |

Los modelos actuales se pre-entrenan con **cientos de millones** de pares "de la web" (ruidosos pero abundantes) y después se ajustan con pares curados a mano o generados con LLMs.

## In-batch negatives

¿De dónde salen los negativos? El truco: **los positivos de los demás son tus negativos**.

```
batch de 4 pares:

            pos₁     pos₂     pos₃     pos₄
ancla₁  [   ✔        ✘        ✘        ✘   ]
ancla₂  [   ✘        ✔        ✘        ✘   ]
ancla₃  [   ✘        ✘        ✔        ✘   ]
ancla₄  [   ✘        ✘        ✘        ✔   ]

✔ = similitud que tiene que subir
✘ = similitud que tiene que bajar
```

Se calcula el coseno de cada ancla contra cada positivo del batch. El modelo tiene que lograr que en cada fila **gane la diagonal**. Con un batch de 4 cada ancla tiene 3 negativos; con un batch de 32.000, tiene 31.999 gratis. Por eso estos modelos se entrenan con batches enormes.

## La función de pérdida (InfoNCE)

En palabras, sin código: para cada fila de la tabla de arriba,

1. Se toman los cosenos y se dividen por una **temperatura** (un número chico, por ejemplo 0,05). Esto agranda las diferencias.
2. Se pasan por un softmax: quedan como probabilidades que suman 1.
3. La pérdida es qué tan baja quedó la probabilidad del positivo correcto.

Es literalmente un problema de **clasificación**: "de todos estos textos, ¿cuál es el que va con esta ancla?".

La temperatura importa: muy alta y el modelo no distingue bien; muy baja y se obsesiona con los negativos más difíciles. Un efecto de esto es que **el rango de cosenos que da cada modelo depende de cómo se entrenó** (ver [`errores/03-umbral-fijo`](../../errores/03-umbral-fijo)).

## Hard negatives

Los negativos al azar son fáciles: distinguir "¿cómo reseteo mi contraseña?" de "receta de empanadas" no enseña nada. Lo que enseña son los **negativos difíciles**: textos que se parecen pero no son la respuesta.

```
ancla:          "¿cómo cambio la contraseña de mi cuenta?"
positivo:       "Para cambiar tu contraseña, entrá en Configuración > Seguridad..."
hard negative:  "Para cambiar tu email, entrá en Configuración > Perfil..."
```

Se buscan con un modelo anterior (lo que ese modelo cree parecido pero está etiquetado como incorrecto). Ojo con los **falsos negativos**: textos que en realidad sí eran respuesta válida y se marcaron como negativos; confunden al modelo.

## Simétrico y asimétrico

| | Simétrico | Asimétrico |
|---|---|---|
| Pares | Dos textos del mismo tipo (paráfrasis, duplicados) | Pregunta corta ↔ documento largo |
| Cómo se usa | Igual para los dos lados | Prefijo o modo distinto para consulta y para documento |
| Para qué | Detección de duplicados, clustering | Búsqueda, RAG |

Muchos modelos se entrenan con prefijos (`query: ` / `passage: `) o con un parámetro de tipo de input. Si al usarlos no se respeta, rinden peor (ver [`errores/04-query-y-documento-iguales`](../../errores/04-query-y-documento-iguales)).

## Qué define a un buen modelo de embeddings

1. **Los datos**: variedad (idiomas, dominios, código) y calidad de los pares.
2. **Los negativos**: batches grandes y hard negatives bien elegidos.
3. **Para qué se ajustó**: un modelo tuneado para búsqueda puede ser mediocre para clustering, y al revés.

Por eso ningún modelo es el mejor en todo. Benchmarks como MTEB miden por tarea, pero lo que vale es medir sobre tus datos (ver [`errores/08-no-medir`](../../errores/08-no-medir)).

## ✅ / ❌

- ✅ Alcanza con pares: no hace falta etiquetar "qué tan parecidos" son del 1 al 10.
- ✅ Los negativos salen gratis del propio batch.
- ✅ Se puede ajustar un modelo existente a tu dominio con unos miles de pares propios.
- ❌ Necesita batches enormes (mucha memoria) para rendir bien.
- ❌ Los falsos negativos y los pares ruidosos degradan el modelo.
- ❌ El modelo aprende lo que los pares le enseñan: si los pares son "mismo tema", no va a distinguir afirmación de negación.
