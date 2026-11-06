# BPE (Byte Pair Encoding)

Se arranca con el texto partido en caracteres y se repite un único paso: **buscar el par de tokens vecinos que más se repite en el corpus y fusionarlo en un token nuevo**. Cada fusión (*merge*) agrega un token al vocabulario. Se para cuando el vocabulario llega al tamaño que elegiste.

**Ejemplo real:** GPT-2 (50.257 tokens), la familia GPT y Llama 3 usan BPE (en su versión byte-level, ver [`03-byte-level-bpe`](../03-byte-level-bpe)).

```
corpus:  "los gatos"  "los perros"  "gatos comen"  ...

inicio:  ▁ l o s   ▁ g a t o s   ▁ p e r r o s
paso 1:  'o'+'s' es el par más frecuente      ->  ▁ l os   ▁ g a t os   ▁ p e r r os
paso 2:  '▁'+'l'                              ->  ▁l os    ▁ g a t os   ▁ p e r r os
paso 3:  '▁l'+'os'                            ->  ▁los     ▁ g a t os   ▁ p e r r os
...
paso N:                                           ▁los     ▁gatos       ▁perros
```

## Las dos fases

**Entrenamiento** (una sola vez, sobre un corpus enorme): sale una **lista ordenada de merges** y el **vocabulario**, donde cada token tiene un ID fijo.

**Tokenización** (cada vez que usás el modelo): se parte el texto nuevo en caracteres y se aplican los merges **en el mismo orden en que se aprendieron**. Si una palabra nunca apareció en el corpus, igual se puede armar con pedazos más chicos que sí conocés:

```
"gatitas" (nunca la vio)  ->  ▁gatit | a | s
"comiendo"                ->  ▁co | m | i | e | n | do
```

## Pre-tokenización y el `▁`

Antes de aplicar BPE, el texto se parte en "palabras" y **los merges nunca cruzan de una a otra**. Si no, aparecerían tokens como `"s▁de▁l"` que no sirven para nada.

El espacio no se descarta: pasa a ser parte del token que sigue (`▁gato`). Por eso el decode reconstruye el texto exacto. Este proyecto usa `▁`, como SentencePiece; GPT-2 usa `Ġ`. Es la misma idea.

Una consecuencia: `"los"` al principio del texto y `" los"` en el medio **son tokens distintos**.

## El tamaño del vocabulario es un trade-off

| Vocabulario | Tokens por texto | Costo |
|---|---|---|
| Chico (pocos merges) | Muchos | Secuencias largas: más cómputo, más contexto gastado, más plata |
| Grande (muchos merges) | Pocos | Tabla de embeddings más grande; tokens raros que casi no se entrenan |

Los modelos actuales usan entre 50.000 y 200.000 tokens.

## ✅ / ❌

- ✅ Ninguna palabra queda afuera mientras sus caracteres estén en el vocabulario.
- ✅ Simple, determinístico y rápido de aplicar.
- ✅ Lo frecuente queda en un token y lo raro se parte: comprime donde más conviene.
- ❌ Un carácter que nunca vio se vuelve `<unk>` y la información se pierde. Lo resuelve byte-level BPE.
- ❌ Los merges son estadísticos, no lingüísticos: `▁comiendo` queda en `▁co | m | i | e | n | do` y no en `com | iendo`.
- ❌ El vocabulario refleja el corpus: si estaba casi todo en inglés, los otros idiomas se parten en más tokens y salen más caros.

## Correr el ejemplo

```bash
python3 implementaciones/02-bpe/bpe.py
```

Muestra:

1. Los primeros 20 merges del entrenamiento, con cuántas veces apareció cada par.
2. Cómo se tokenizan palabras que vio y palabras que no.
3. Ida y vuelta completa: texto → tokens → IDs → texto.
4. Qué pasa con caracteres que no están en el vocabulario (emoji, `€`).
5. Cómo baja la cantidad de tokens a medida que hay más merges.

Para jugar: cambiá el `CORPUS` (agregá texto en otro idioma, código o números) y fijate qué merges aprende.
