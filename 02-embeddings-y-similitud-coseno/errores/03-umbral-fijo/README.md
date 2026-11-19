# Usar un umbral fijo de similitud

"Si el coseno da más de 0,8, son lo mismo." El problema es que **0,8 no significa lo mismo en todos los modelos**. Cada uno tiene su propio rango, que depende de cómo se entrenó (la temperatura del entrenamiento contrastivo, los datos, la dimensión).

```
                                    modelo A    modelo B
"¿cómo reseteo mi contraseña?"
   vs "olvidé la clave"               0,62        0,91
   vs "cambiar el email de la cuenta" 0,41        0,84
   vs "receta de empanadas"           0,05        0,72

umbral 0,8:   en A no encuentra nada   |   en B todo es "lo mismo"
```

*(Valores ilustrativos: lo que importa es que el orden es el mismo y los rangos no.)*

En algunos modelos los vectores ocupan un cono angosto (**anisotropía**): dos textos al azar ya dan 0,7, y toda la información útil está entre 0,7 y 1. En otros, lo que no tiene relación da cerca de 0.

Cómo aparece en la práctica:

- **Copiar un umbral de un tutorial** que usaba otro modelo.
- **Cambiar de modelo y dejar el umbral**: de golpe el RAG no trae contexto, o trae de todo.
- **Mezclar "distancia" con "similitud"**: un umbral de 0,2 de distancia coseno es 0,8 de similitud. Copiado al revés, filtra exactamente lo contrario.
- **Un único umbral para todo**: el mismo número para consultas cortas y largas, o para temas distintos, cuando la distribución cambia.

**Fix:**
- Trabajar con **rankings** (top-k) siempre que se pueda: el orden es lo confiable, no el número.
- Si hace falta un umbral (por ejemplo, "no hay respuesta" o "esto es un duplicado"), **calibrarlo** con pares etiquetados del modelo que usás: mirar la distribución de cosenos de pares que sí van juntos y de pares que no, y elegir el corte con la precisión y el recall que necesitás.
- Volver a calibrar cada vez que cambia el modelo.
- Para decidir "relevante sí / no" con más confianza, un reranker (cross-encoder) da puntajes más interpretables que el coseno.
