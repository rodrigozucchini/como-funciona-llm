# Mezclar modelos

Cada modelo de embeddings arma **su propio espacio**. Que dos modelos devuelvan vectores de 1024 dimensiones no quiere decir que la dimensión 17 signifique lo mismo en los dos: es como comparar coordenadas de dos mapas con orígenes y ejes distintos.

```
modelo A:  "perro"  ->  [ 0,31, -0,12,  0,08, ... ]
modelo B:  "perro"  ->  [-0,05,  0,44, -0,27, ... ]

coseno(A("perro"), B("perro")) ≈ 0   ← el mismo texto, "sin relación"
```

Cómo aparece en la práctica:

- **Cambio de modelo a medias**: se indexan los documentos nuevos con el modelo nuevo y los viejos quedan como estaban. La base mezcla dos espacios y la búsqueda devuelve resultados raros solo para una parte de los documentos.
- **Consulta y documentos con modelos distintos**: los documentos se embeddearon con un modelo caro y las consultas con uno barato "porque tiene la misma dimensión".
- **Cambio de versión**: el proveedor publica `v2` del mismo modelo. Para la API es otro modelo; los vectores de `v1` no son compatibles.
- **Cambio de configuración**: otra cantidad de dimensiones (Matryoshka), otro pooling, otra cuantización. También cambia el espacio, o al menos lo degrada.

Lo peor es que **no hay ningún error**: el coseno se calcula igual, la base devuelve k resultados igual. Solo son malos.

**Fix:**
- Guardar junto a cada vector **qué modelo, versión y configuración** lo generó.
- Al cambiar cualquiera de esas cosas, **re-embeddear toda la colección** en un índice nuevo y cambiar de golpe cuando esté completo (no ir migrando de a partes sobre el mismo índice).
- Validar al consultar que el modelo de la consulta coincide con el del índice.
- Antes de migrar, comparar los dos modelos con un set de evaluación (ver [`08-no-medir`](../08-no-medir)).
