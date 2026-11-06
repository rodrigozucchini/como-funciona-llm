# Byte-level BPE

El mismo algoritmo que [`02-bpe`](../02-bpe), con un cambio en el punto de partida: el vocabulario inicial **no son los caracteres del corpus sino los 256 valores posibles de un byte**. Todo texto, en cualquier idioma o con emojis, es una secuencia de bytes en UTF-8, así que siempre se puede tokenizar. En el peor caso, byte por byte.

**Ejemplo real:** GPT-2 en adelante, `tiktoken` (`cl100k_base`, `o200k_base`) y Llama 3. Es el estándar de los LLMs actuales.

```
UTF-8:   'a' -> 61            (1 byte)
         'ñ' -> c3 b1         (2 bytes)
         '€' -> e2 82 ac      (3 bytes)
         '🐟' -> f0 9f 90 9f   (4 bytes)

vocab inicial:  256 tokens, uno por byte (IDs 0–255)
merges:         IDs 256, 257, ...  ('o'+'s' -> 'os', 'c3'+'a1' -> 'á', ...)
```

## Qué cambia respecto de BPE por caracteres

| | BPE por caracteres | Byte-level BPE |
|---|---|---|
| Vocabulario inicial | Los caracteres que aparecieron en el corpus | Siempre 256 bytes |
| Carácter que nunca vio | `<unk>`, se pierde | Se parte en sus bytes, no se pierde |
| Un token es... | Uno o más caracteres completos | Una secuencia de bytes, **que puede ser medio carácter** |

```
"el gato come 🐟 y paga 5€"

BPE por caracteres:  ... ▁come | ▁ | <unk> | ▁y | ... | ▁ | <unk> | <unk>
Byte-level BPE:      ... ▁come | ▁ | <f0> | <9f> | <90> | <9f> | ▁y | ... | 5 | <e2> | <82> | <ac>
```

## Consecuencias

**Lo que el tokenizer no vio, cuesta más.** Lo frecuente en el corpus de entrenamiento tiene merges y queda en pocos tokens. Lo raro cae a bytes: un carácter japonés son 3 tokens y un emoji son 4. Los tokenizers reales tienen el mismo sesgo, en menor escala: **el mismo contenido en otro idioma puede costar varias veces más** (ver [`errores/01-estimar-por-palabras`](../../errores/01-estimar-por-palabras)).

**Un token no siempre es texto válido.** Si decodificás los tokens de a uno, los pedazos de un carácter multibyte salen como `�`. Hay que acumular los bytes y decodificar cuando el carácter está completo. Las SDKs ya lo hacen al hacer streaming, pero importa si procesás tokens a mano. Lo mismo vale al truncar: cortar por cantidad de tokens o de bytes puede partir un carácter (ver [`errores/06-cortar-por-caracteres`](../../errores/06-cortar-por-caracteres)).

**GPT-2 y el truco de los bytes "imprimibles".** Los tokenizers reales mapean cada byte a un carácter visible (el espacio se ve como `Ġ`), para poder guardar el vocabulario como texto. Es solo una forma de mostrarlo; por debajo son bytes.

## ✅ / ❌

- ✅ Nunca hay `<unk>`: cualquier entrada se puede representar y reconstruir exacta.
- ✅ Vocabulario inicial chico y fijo, igual para todos los idiomas.
- ❌ Lo que no se vio al entrenar se parte en muchos tokens: más caro y más contexto gastado.
- ❌ Los tokens pueden cortar caracteres a la mitad: cuidado al decodificar, hacer streaming o truncar.

## Correr el ejemplo

```bash
python3 implementaciones/03-byte-level-bpe/byte_level_bpe.py
```

Muestra:

1. Cuántos bytes ocupa cada carácter en UTF-8.
2. El entrenamiento, con los merges que reconstruyen letras acentuadas (`c3` + `a1` → `á`).
3. La frase que en `02-bpe` perdía el emoji y el `€`, ahora sin `<unk>`.
4. Cuántos tokens por carácter cuestan el mismo contenido en español, inglés, japonés y emojis.
5. Qué pasa al decodificar un emoji token por token.
