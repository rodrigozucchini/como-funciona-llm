# Estimar tokens por palabras

"1 palabra ≈ 1 token" o "4 caracteres ≈ 1 token" se acerca bastante en prosa en inglés y falla en todo lo demás:

- **Código, JSON, URLs**: llaves, comillas, barras e identificadores se parten en muchos tokens. Una URL es 1 "palabra" y decenas de tokens.
- **Números**: cada tokenizer los parte a su manera, muchas veces de a 1 a 3 dígitos.
- **Otros idiomas**: lo que tuvo poca presencia en el entrenamiento del tokenizer se parte más. El mismo contenido en español, hindi o japonés puede costar bastante más que en inglés.
- **Formato**: indentación, saltos de línea y espacios repetidos también son tokens.

La consecuencia: presupuestos de costo que se quedan cortos, prompts que "entraban" en el contexto y no entran, y `max_tokens` que corta la respuesta.

**Fix:** contar con el tokenizer del modelo que vas a usar. Antes de mandar, con `count_tokens`; después, con el `usage` de la respuesta.

```bash
python3 errores/01-estimar-por-palabras/main.py
```
