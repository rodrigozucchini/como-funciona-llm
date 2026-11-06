# Espacios y mayúsculas

Para el tokenizer, `"gato"`, `" gato"`, `"Gato"` y `" GATO"` son secuencias de tokens distintas. El espacio de adelante es parte del token (`▁gato`), y las mayúsculas suelen partirse en más pedazos porque aparecen menos.

Dónde molesta:

- **Prompts que terminan con espacio**: el último token queda como un `▁` suelto, algo que el modelo casi nunca vio, porque el espacio va pegado a la palabra que sigue. La continuación puede salir peor.
- **Few-shot con formato inconsistente**: `Animal: gato`, `animal:perro` y `ANIMAL : pez` son tres patrones distintos, y el modelo no sabe cuál imitar.
- **Stop sequences y comparaciones**: buscar `"Fin"` cuando el modelo genera `" fin"`.

**Fix:** formato idéntico en todos los ejemplos, sin espacios al final del prompt, y normalizar (`strip`, mismas mayúsculas) antes de comparar.

```bash
python3 errores/02-espacios-y-mayusculas/main.py
```
