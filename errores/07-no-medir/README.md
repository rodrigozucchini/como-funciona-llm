# No medir

Cada respuesta de la API trae el `usage`: `input_tokens`, `output_tokens`, `cache_creation_input_tokens` y `cache_read_input_tokens`. Si no lo guardás, el costo lo ves recién en la factura, y aunque el total te dé parecido a lo que estimaste, no sabés de dónde sale.

Lo que se esconde detrás de un promedio:

- **Un caché que no funciona**: se escribe en cada request (a 1,25×) y no se lee nunca, porque algo cambia en el prefijo (la fecha en el system prompt, el orden de las tools, un JSON sin ordenar). Sin errores ni avisos: solo `cache_read_input_tokens` en 0.
- **La cola larga**: un 2% de requests con documentos enormes que se llevan un tercio del costo. El p50 no los muestra.
- **Qué función del producto gasta**: una sola puede ser el 77% de la factura.

**Fix:** guardar el `usage` de cada respuesta junto con el modelo y la función del producto que hizo el request. Mirar el costo y el cache hit por función, el p50 y el máximo (no solo el promedio), y poner una alerta si el costo diario se dispara.

```bash
python3 errores/07-no-medir/main.py
```
