# Contar con el tokenizer equivocado

Cada familia de modelos tiene su propio tokenizer, entrenado sobre su propio corpus. El mismo texto da **cantidades de tokens distintas** y **IDs distintos** en cada uno.

- Usar `tiktoken` (de OpenAI) para estimar tokens de Claude, o al revés.
- Usar el tokenizer de un modelo viejo para uno nuevo del mismo proveedor. El tokenizer de Claude que llegó con Opus 4.7 genera entre 1× y 1,35× los tokens del anterior para el mismo texto.
- Guardar IDs de tokens de un modelo y usarlos con otro: un ID no significa lo mismo en dos vocabularios.

El error no es una constante que puedas corregir multiplicando: cambia según el idioma y el tipo de texto.

**Fix:** contar con el tokenizer del modelo exacto que vas a usar (`count_tokens` en la API de Claude) y volver a medir cada vez que cambiás de modelo.

```bash
python3 errores/05-tokenizer-equivocado/main.py
```
