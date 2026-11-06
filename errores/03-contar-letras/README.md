# Esperar que el modelo vea letras (y dígitos)

El modelo no recibe `perritos`: recibe un ID, por ejemplo `[339]`. Cuántas `r` tiene ese token, cómo se deletrea o con qué rima lo tuvo que aprender de memoria a partir de los datos, porque no lo puede "mirar". Por eso los LLMs fallan en cosas que a una persona le parecen triviales:

- Contar letras (el clásico de cuántas "r" tiene *strawberry*).
- Invertir una palabra o un texto, o buscar anagramas.
- Contar palabras o caracteres para respetar un límite exacto.

Con los **números** pasa algo parecido: se parten según lo que era frecuente en el corpus, no según su valor. `2024` puede ser `202 | 4` y `2042` ser `20 | 4 | 2`, con unidades y decenas que no quedan alineadas. Algunos tokenizers modernos fuerzan grupos de hasta 3 dígitos o dígitos sueltos justamente para mejorar esto, pero hacer aritmética larga "de cabeza" sigue siendo poco confiable.

**Fix:** para contar, deletrear o calcular, darle al modelo una herramienta (ejecutar código) o hacerlo en tu propio código. El modelo es bueno decidiendo *qué* calcular, no haciendo la cuenta token por token.

```bash
python3 errores/03-contar-letras/main.py
```
