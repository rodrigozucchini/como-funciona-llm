# Cortar texto por caracteres o bytes

Para que un documento "entre" en el contexto (o en un campo de la DB), se lo corta por cantidad de caracteres o de bytes. Hay tres formas de romperlo:

- **Por bytes**: un carácter UTF-8 ocupa de 1 a 4 bytes. Si el corte cae en el medio de una `ñ` o de un emoji, el `decode` tira `UnicodeDecodeError` o deja un `�`.
- **Por caracteres, con un "4 caracteres ≈ 1 token"**: la cantidad de caracteres por token cambia con cada texto. Te pasás del límite igual, o desperdiciás espacio.
- **Por tokens, sin mirar dónde**: entra justo, pero queda cortado a mitad de una oración (o de un carácter, con byte-level BPE).

**Fix:** contar en tokens y cortar en un límite natural (fin de oración o de párrafo). Y antes de truncar, preguntate si conviene más resumir, partir el documento (chunking) o recuperar solo lo relevante.

```bash
python3 errores/06-cortar-por-caracteres/main.py
```
