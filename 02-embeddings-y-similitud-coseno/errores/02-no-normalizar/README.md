# No normalizar

Si el índice usa **producto punto** y los vectores no miden 1, el largo del vector se mete en el ranking. Gana el vector más largo, no el más parecido.

```
consulta q = (0,6, 0,8)          |q| = 1

doc A = (0,6, 0,8)               |A| = 1     coseno = 1,00   producto punto = 1,00
doc B = (1,5, 0,5)               |B| = 1,58  coseno = 0,82   producto punto = 1,30   ◄ gana B

Por coseno, A es idéntico a la consulta. Por producto punto, gana B, solo por ser más largo.
```

Cómo aparece en la práctica:

- **El modelo no devuelve vectores normalizados** y se usa un índice de producto punto "porque es más rápido". Algunas APIs normalizan siempre; muchas librerías locales no lo hacen salvo que se lo pidas.
- **Se recortaron dimensiones** (Matryoshka) y no se volvió a normalizar: el vector recortado mide menos de 1, y cuánto menos depende de cada texto.
- **Se normalizaron los documentos pero no la consulta** (o al revés). Con una sola consulta no cambia el orden, pero los puntajes dejan de ser cosenos y un umbral deja de tener sentido.
- **Se promediaron vectores** (por ejemplo, varios chunks para tener "un vector por documento"): el promedio de vectores normalizados ya no mide 1.
- **La métrica del índice no coincide con la del modelo**: un índice euclidiano con vectores sin normalizar ordena distinto que el coseno (ver [`implementaciones/06-metricas-de-distancia`](../../implementaciones/06-metricas-de-distancia)).

Los síntomas: ciertos documentos (muy largos, o con muchas palabras frecuentes) aparecen en el top de casi cualquier búsqueda.

**Fix:**
- Normalizar **siempre** al guardar y al consultar, también después de recortar o promediar. Hacerlo dos veces no rompe nada: un vector normalizado normalizado sigue igual.
- O usar coseno como métrica del índice y dejar que lo calcule la base.
- Excepción: si el modelo está entrenado para producto punto sin normalizar, respetarlo. Lo dice su documentación.
- Chequeo rápido: calcular la norma de algunos vectores guardados. Tiene que dar 1 (con error de redondeo).
