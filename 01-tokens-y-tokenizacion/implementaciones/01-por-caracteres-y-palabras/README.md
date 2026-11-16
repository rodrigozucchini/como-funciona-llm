# Por caracteres y por palabras

Las dos formas más obvias de partir un texto, y por qué ningún LLM las usa.

**Por caracteres**: cada letra, espacio y signo es un token.
**Por palabras**: cada palabra y cada signo de puntuación es un token.

```
"los gatitos comen pescado."

caracteres (26):  l | o | s | ␣ | g | a | t | i | t | o | s | ␣ | c | o | m | e | n | ...
palabras    (5):  los | gatitos | comen | pescado | .
```

## Por caracteres

- ✅ Vocabulario chico y cerrado: con unos cientos de símbolos se cubre casi todo.
- ✅ Nunca aparece una "palabra desconocida".
- ❌ Las secuencias son ~5 veces más largas. Cada token es un paso del modelo, ocupa lugar en la ventana de contexto, y la atención crece con el **cuadrado** del largo.
- ❌ El modelo tiene que aprender desde cero que `g-a-t-o` forma una unidad con significado.

## Por palabras

- ✅ Secuencias cortas, y cada token ya es una unidad con significado.
- ❌ El vocabulario **no tiene techo**: conjugaciones, plurales, diminutivos, nombres propios, typos, URLs, código. Cada variante es una entrada nueva.
- ❌ Una palabra que no estaba al entrenar (*out of vocabulary*) se vuelve `<unk>` y se pierde.
- ❌ `gato`, `gatos` y `gatito` son IDs sin relación: el modelo no puede aprovechar que comparten la raíz.

```
"las gatitas comieron pescado."
por palabras:  <unk> | <unk> | <unk> | pescado | .
```

## El punto medio: subwords

| | Caracteres | Palabras | Subwords (BPE, Unigram) |
|---|---|---|---|
| Tamaño del vocabulario | ~100–300 | Millones (y sigue creciendo) | 50k–200k, fijo |
| Largo de la secuencia | Muy largo | Corto | Casi tan corto como por palabras |
| Palabras nuevas | Sí | `<unk>` | Se arman con pedazos |
| Comparte raíces | No hace falta | No | Sí: `▁gat` + `itos` |

Eso es lo que hacen [`02-bpe`](../02-bpe) y [`04-unigram-sentencepiece`](../04-unigram-sentencepiece).

## Correr el ejemplo

```bash
python3 implementaciones/01-por-caracteres-y-palabras/por_caracteres_y_palabras.py
```

Muestra:

1. La misma frase con los dos tokenizers y el tamaño de cada vocabulario.
2. Qué pasa con palabras que no estaban en el corpus.
3. Cómo crece el vocabulario por palabras con cada oración nueva, mientras el de caracteres se estabiliza.
4. Cuántos tokens hacen falta para todo el corpus con cada uno.
