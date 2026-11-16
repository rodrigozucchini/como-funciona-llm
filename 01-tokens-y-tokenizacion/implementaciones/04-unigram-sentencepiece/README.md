# Unigram (SentencePiece)

El camino inverso a BPE. En vez de arrancar chico y **fusionar**, arranca con un vocabulario **enorme** (todos los substrings frecuentes del corpus) y lo va **podando**, sacando en cada ronda los tokens que menos aportan, hasta llegar al tamaño buscado.

Cada token tiene una **probabilidad**. Para tokenizar se busca la partición cuya probabilidad total (el producto de las probabilidades de sus tokens) sea la más alta.

**Ejemplo real:** T5, ALBERT, XLNet y mBART usan Unigram con la librería SentencePiece. Ojo: SentencePiece también implementa BPE, y Llama 1/2 y Gemma usan SentencePiece en **modo BPE**. "SentencePiece" es la herramienta, no el algoritmo.

```
BPE:      a  b  c  d  ...         ──fusionar──►   vocabulario de N tokens
Unigram:  todos los substrings    ──podar────►   vocabulario de N tokens
          (326 candidatos)                       (50 tokens)
```

## Entrenamiento

1. **Vocabulario inicial**: todos los substrings que aparecen al menos 2 veces, más todos los caracteres sueltos.
2. **EM**: tokenizar el corpus con el vocabulario actual y recalcular las probabilidades. Cada palabra reparte su conteo entre **todas** sus particiones posibles, según lo probable que sea cada una.
3. **Poda**: para cada token, calcular cuánto empeoraría la pérdida (*log-likelihood* negativa) del corpus si no existiera. Se saca el 25% que menos aporta.
4. Repetir 2 y 3 hasta llegar al tamaño buscado. Los caracteres sueltos nunca se podan, así cualquier palabra (con caracteres conocidos) se puede partir.

```
ronda  vocab  pérdida
    0    326    453.9    ← substrings como 'atos' (sin la 'g') no aportan nada
    7     65    450.2    ← la pérdida casi no se movió
    8     55    475.1    ← acá empieza a sacar tokens útiles
    9     50    494.2
```

## Tokenizar: Viterbi

Con las probabilidades aprendidas, la mejor partición se encuentra con **programación dinámica** (Viterbi): para cada posición de la palabra se guarda la mejor forma de llegar hasta ahí.

```
"▁comemos" tiene 6 particiones posibles:
   99.9%   ▁come | mos          ← Viterbi elige esta
    0.1%   ▁come | m | o | s
    0.0%   ▁ | co | m | e | mos
   ...
```

## Lo que Unigram tiene y BPE no

**Probabilidades por partición.** BPE da una única tokenización, la que resulta de aplicar los merges. Unigram sabe cuánto vale cada partición posible.

**Subword regularization.** Al **entrenar un modelo** (no al usarlo), en vez de usar siempre la mejor partición se sortea una. El parámetro `alpha` aplana las probabilidades para que haya más variedad. El modelo ve la misma palabra partida de varias formas y se vuelve más robusto a typos y variantes:

```
1.000 sorteos de "▁comemos" con alpha = 0.2:
   765   ▁come | mos
   174   ▁come | m | o | s
    48   ▁ | co | m | e | mos
```

## SentencePiece: texto crudo y `▁`

SentencePiece no pre-tokeniza con reglas de cada idioma: trata el texto como una secuencia de caracteres y reemplaza el espacio por `▁`. Por eso:

- Sirve igual para idiomas sin espacios (japonés, chino, tailandés).
- El decode es trivial: juntar los tokens y cambiar `▁` por espacio.
- La puntuación es un carácter más y podría quedar pegada a una palabra (`▁pescado.`).

Como en BPE por caracteres, un carácter que no está en el vocabulario es `<unk>`. SentencePiece tiene la opción `byte_fallback=True` para partirlo en bytes, como hace [`03-byte-level-bpe`](../03-byte-level-bpe).

## ✅ / ❌

- ✅ Independiente del idioma: no necesita reglas de pre-tokenización.
- ✅ Tiene un modelo probabilístico: sabe cuánto vale cada partición y permite subword regularization.
- ✅ Criterio de poda claro: saca lo que menos empeora la pérdida.
- ❌ El entrenamiento es más caro que el de BPE (muchas rondas de EM sobre un vocabulario grande).
- ❌ Sin `byte_fallback`, los caracteres desconocidos son `<unk>`.
- ❌ En los LLMs generativos actuales se usa menos que el byte-level BPE.

## Simplificación de este ejemplo

Para repartir los conteos entre todas las particiones, el SentencePiece real usa el algoritmo **forward-backward**, que no necesita enumerarlas. Acá las palabras son cortas, así que se enumeran todas directamente: el resultado es el mismo y el código se entiende mejor.

## Correr el ejemplo

```bash
python3 implementaciones/04-unigram-sentencepiece/unigram.py
```

Muestra:

1. El entrenamiento ronda por ronda (vocabulario y pérdida), y los tokens más probables.
2. La partición que elige Viterbi para palabras vistas y nuevas.
3. Todas las particiones de `▁comemos` con su probabilidad, y 1.000 sorteos de subword regularization.
4. Encode/decode de una frase y qué pasa con un emoji.

Para jugar: cambiá `tamano_vocab` en `main()` (probá 40 o 70) y fijate cómo cambian las particiones.
