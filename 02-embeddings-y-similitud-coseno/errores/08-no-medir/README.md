# No medir

Casi todas las decisiones de un sistema con embeddings se toman "a ojo": qué modelo, qué tamaño de chunk, qué umbral, qué índice, cuántas dimensiones. Se prueban tres consultas, los resultados "se ven bien", y se pasa a producción. Lo que no se ve:

- **El índice aproximado pierde resultados** y no avisa: un HNSW mal configurado puede tener 80% de recall y devolver siempre k resultados igual.
- **El modelo nuevo es peor en tus datos**, aunque sea mejor en un benchmark público.
- **La cuantización o el recorte de dimensiones** costaron más calidad de la esperada.
- **Un cambio de chunking** mejoró unas consultas y rompió otras.

## Qué medir

**1. Calidad de la búsqueda** (¿trae lo correcto?). Hace falta un **set de evaluación**: consultas reales con los documentos que deberían aparecer. Cien consultas bien elegidas ya dicen mucho.

| Métrica | Qué responde |
|---|---|
| **Recall@k** | De los documentos correctos, ¿cuántos aparecieron en los primeros k? |
| **Precisión@k** | De los k que aparecieron, ¿cuántos eran correctos? |
| **MRR** | ¿En qué posición apareció el primero correcto? (1 si fue primero, 1/2 si fue segundo, 1/3...) promediado. |
| **nDCG@k** | Como el recall, pero premia que los más relevantes estén más arriba. |

```
consulta: "¿cómo roto la API key?"     correcto: doc_17

resultados: [doc_03, doc_17, doc_42, doc_08, doc_11]

recall@1 = 0    recall@5 = 1    MRR = 1/2
```

**2. Recall del índice** (¿el ANN encuentra lo mismo que la fuerza bruta?). Para un grupo de consultas, comparar el top-k del índice contra el top-k exacto. Esto no necesita etiquetas: la fuerza bruta es la referencia.

**3. Operación**: latencia (sobre todo el percentil 99, no el promedio), memoria del índice, costo de embeddear y de re-indexar.

## Qué poner en el set de evaluación

- Consultas **reales** de usuarios, no solo las que se le ocurren al equipo.
- **Paráfrasis** y consultas en otro idioma, si aplica.
- **Exactas**: códigos, IDs, nombres propios (ver [`07-palabras-exactas`](../07-palabras-exactas)).
- **Trampas**: negaciones, opuestos, fechas y versiones (ver [`06-parecido-no-es-relevante`](../06-parecido-no-es-relevante)).
- Consultas **sin respuesta**, para ver si el sistema sabe decir que no hay nada.

**Fix:**
- Armar el set de evaluación **antes** de elegir modelo.
- Correrlo en cada cambio (modelo, chunking, índice, cuantización) y comparar contra la versión anterior.
- Medir el recall del índice ANN contra la fuerza bruta al configurarlo, y de nuevo cuando la colección crece mucho.
- Loguear en producción las consultas, los resultados y si el usuario encontró lo que buscaba: de ahí salen nuevas consultas para el set.
