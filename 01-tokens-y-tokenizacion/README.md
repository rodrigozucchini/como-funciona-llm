# Tokens y tokenización

Un LLM no lee letras ni palabras: lee **números**. Antes de que el modelo vea tu texto, un **tokenizer** lo parte en pedazos (**tokens**) y le asigna a cada uno un ID de un vocabulario fijo. El modelo recibe IDs, predice IDs, y el tokenizer los vuelve a convertir en texto.

```
"los gatitos comen"
        │  tokenizer (encode)
        ▼
 ["▁los", "▁gatit", "os", "▁comen"]
        │
        ▼
 [  412,    9081,   278,    3305  ]  ──►  modelo  ──►  [ 1534, ... ]
                                                            │  tokenizer (decode)
                                                            ▼
                                                        " pescado"
```

Todo lo que pasa con un LLM se mide en tokens: cuánto entra en el contexto, cuánto tarda en responder y **cuánto pagás**.

## Por qué no por caracteres ni por palabras

| Unidad | Vocabulario | Largo de la secuencia | Problema |
|---|---|---|---|
| **Caracteres** | ~100–300 | Larguísima | Cada letra es un paso de cómputo; se gasta el contexto enseguida |
| **Palabras** | Infinito | Corta | `gato`, `gatos`, `gatito` son tres entradas sin relación; una palabra nueva no tiene ID |
| **Subwords** | 50k–200k | Intermedia | Lo frecuente es un token; lo raro se arma con pedazos. Es lo que se usa |

## Conceptos clave

| Concepto | Qué es |
|---|---|
| **Token** | La unidad que ve el modelo: puede ser una palabra, un pedazo, un carácter o un byte. |
| **Vocabulario** | La lista fija de todos los tokens posibles. Cada uno tiene un ID. |
| **Token ID** | El número que representa a un token. Es lo único que entra al modelo. |
| **Encode / Decode** | Texto → IDs y IDs → texto. |
| **Merges** | (BPE) Lista ordenada de pares que se fusionaron al entrenar el tokenizer. |
| **Pre-tokenización** | Partir el texto en "palabras" antes de tokenizar, para que los tokens no crucen de una a otra. |
| **Normalización** | Limpiar el texto antes: Unicode (NFKC), a veces minúsculas o acentos. |
| **Byte-level** | Tokenizer que arranca desde los 256 bytes en vez de caracteres: puede representar cualquier texto. |
| **`<unk>`** | Token "desconocido". Aparece cuando el tokenizer no puede representar algo, y se pierde información. |
| **Tokens especiales** | Marcas que no son texto: inicio/fin de secuencia, roles del chat, separadores. |
| **Fertilidad / compresión** | Cuántos tokens por palabra (o caracteres por token) da un tokenizer sobre un texto. |

## Tipos de tokenizer

### 1. BPE (Byte Pair Encoding)

Arranca de caracteres y **fusiona** una y otra vez el par de vecinos más frecuente hasta llegar al tamaño de vocabulario buscado.
- ✅ Simple, determinístico, comprime bien lo frecuente.
- ❌ Un carácter que nunca vio queda como `<unk>`.
- Lo usaban: GPT-1 y los modelos de traducción donde apareció (Sennrich et al., 2016).

### 2. Byte-level BPE

El mismo algoritmo, pero el vocabulario inicial son los **256 bytes** en vez de caracteres. Cualquier texto (emojis, chino, binario) se puede representar: en el peor caso, byte por byte.
- ✅ Nunca hay `<unk>`.
- ❌ Un carácter raro puede costar 3 o 4 tokens, y un token puede cortar un carácter UTF-8 a la mitad.
- Lo usan: GPT-2 en adelante, Llama 3 y la mayoría de los LLMs actuales.

### 3. WordPiece

Parecido a BPE, pero elige el merge que más aumenta la **probabilidad** del corpus, no el más frecuente. Marca la continuación de una palabra con `##` (`gat`, `##itos`).
- Lo usan: BERT y sus derivados. Casi no aparece en LLMs generativos.

### 4. Unigram (SentencePiece)

Al revés que BPE: arranca con un vocabulario **enorme** y lo **poda**, sacando los tokens que menos aportan. Para tokenizar elige la partición más probable (algoritmo de Viterbi). SentencePiece es la librería que lo implementa: trabaja sobre el texto crudo, sin pre-tokenizar, y codifica el espacio como `▁`.
- ✅ Independiente del idioma (sirve para japonés o chino, que no tienen espacios). Puede dar varias particiones posibles, lo que sirve como regularización al entrenar.
- Lo usan: T5, ALBERT, XLNet, mBART. *(Ojo: SentencePiece también implementa BPE, y así lo usan Llama 1 y 2 o Gemma. "SentencePiece" es la herramienta, no el algoritmo.)*

| | BPE | Byte-level BPE | WordPiece | Unigram |
|---|---|---|---|---|
| Arranca de | Caracteres | 256 bytes | Caracteres | Vocabulario grande |
| Cómo crece | Fusiona el par más frecuente | Igual | Fusiona el más probable | Poda el que menos aporta |
| `<unk>` | Sí | No | Sí | Sí (salvo con byte fallback) |

## Costo por token

Las APIs cobran **por millón de tokens (MTok)**, con precios distintos para cada tipo de token:

| Tipo | Qué es | Precio relativo |
|---|---|---|
| **Input** | Todo lo que mandás: system prompt, historial, documentos, definición de tools | 1× |
| **Output** | Lo que genera el modelo | ~5× el input |
| **Razonamiento** | Tokens que el modelo "piensa" antes de responder (aunque no los veas) | Se cobran como output |
| **Cache write** | Guardar un prefijo del prompt en caché | 1,25× (TTL 5 min) o 2× (TTL 1 h) |
| **Cache read** | Reusar un prefijo ya cacheado | ~0,1× o menos |
| **Batch** | Requests asíncronos, sin apuro | 50% de descuento |

Ejemplo con Claude Opus 5.5 ($4 input / $20 output por MTok, precios de octubre 2026):

```
Un request:   2.000 tokens de input  ×  $4  / 1.000.000  =  $0,008
                500 tokens de output ×  $20 / 1.000.000  =  $0,010
                                                           ───────
                                                            $0,018   ← el output es 1/5 de los tokens y más de la mitad del costo

× 1.000.000 requests por mes                             =  $18.000
```

Tres cosas que se desprenden de esto:
1. **El output pesa más**: pedir respuestas cortas o estructuradas ahorra más que recortar el prompt.
2. **El historial se paga en cada turno**: en un chat, el turno 20 vuelve a mandar los 19 anteriores como input. El prompt caching existe para esto.
3. **El mismo texto cuesta distinto según el modelo**: cada familia tiene su propio tokenizer. Por ejemplo, el tokenizer de Claude que llegó con Opus 4.7 genera entre 1× y 1,35× los tokens del anterior para el mismo texto.

> Los precios cambian seguido. La tabla actualizada está en [`implementaciones/06-contar-y-estimar-costo`](implementaciones/06-contar-y-estimar-costo).

## Errores comunes

### 1. Estimar tokens por cantidad de palabras
"1 palabra ≈ 1 token" (o "4 caracteres ≈ 1 token") más o menos sirve para prosa en inglés, y falla con código, JSON, números, URLs y otros idiomas. Un mismo texto en español, japonés o hindi puede costar varias veces más que en inglés.
→ Contar con el tokenizer real del modelo que vas a usar.

### 2. Ignorar espacios y mayúsculas
`"hola"`, `" hola"` y `"Hola"` son tokens distintos. Afecta los stop sequences, los few-shot mal formateados y los prompts que terminan con un espacio.

### 3. Esperar que el modelo vea letras
El modelo no ve las "r" de `strawberry`: ve 2 o 3 tokens opacos. Lo mismo pasa con los números: `12345` se parte de forma arbitraria. Por eso cuesta contar letras, invertir palabras o hacer aritmética "de cabeza".
→ Para eso, una herramienta (código) en vez del modelo.

### 4. Optimizar solo el input
Recortar el prompt un 20% y dejar que el modelo responda con párrafos de relleno. El output es el token más caro.
→ Limitar `max_tokens`, pedir formato estructurado, bajar el effort cuando la tarea es simple.

### 5. Contar con el tokenizer equivocado
Usar `tiktoken` (de OpenAI) para estimar tokens de Claude, o el de un modelo viejo para uno nuevo. Las diferencias pueden ser grandes.
→ El endpoint de conteo de cada proveedor (`count_tokens` en la API de Claude).

### 6. Cortar texto por caracteres o bytes
Truncar un documento por cantidad de caracteres para "que entre": podés pasarte igual o romper un carácter UTF-8 a la mitad.
→ Truncar por tokens, y en un límite natural (párrafo, oración).

### 7. No medir
Cada respuesta de la API trae el `usage` (tokens de input, output y cache). Si no lo guardás, te enterás del costo con la factura.

## Cómo inspeccionar tokens

Esto requiere instalar paquetes (el resto del proyecto no):

```bash
pip install tiktoken sentencepiece anthropic
```

```python
# Tokenizer de OpenAI (byte-level BPE)
import tiktoken
enc = tiktoken.get_encoding("o200k_base")
ids = enc.encode("los gatitos comen")
print(ids, [enc.decode([i]) for i in ids])

# Tokens de Claude: el tokenizer no es público, se cuenta con la API
import anthropic
client = anthropic.Anthropic()
r = client.messages.count_tokens(
    model="claude-opus-5-5",
    messages=[{"role": "user", "content": "los gatitos comen"}],
)
print(r.input_tokens)
```

Para ver tokenizers en el navegador: [tiktokenizer.vercel.app](https://tiktokenizer.vercel.app).

## Estructura

- [`implementaciones/`](implementaciones): cada tipo de tokenizer y cómo calcular el costo, con un diagrama y código mínimo.
  1. [`01-por-caracteres-y-palabras`](implementaciones/01-por-caracteres-y-palabras): los dos extremos y por qué no sirven.
  2. [`02-bpe`](implementaciones/02-bpe): BPE desde cero, merge por merge.
  3. [`03-byte-level-bpe`](implementaciones/03-byte-level-bpe): arrancar de bytes para que nunca haya `<unk>`.
  4. [`04-unigram-sentencepiece`](implementaciones/04-unigram-sentencepiece): podar un vocabulario grande y tokenizar con Viterbi.
  5. [`05-tokens-especiales`](implementaciones/05-tokens-especiales): cómo se ve una conversación cuando llega al modelo.
  6. [`06-contar-y-estimar-costo`](implementaciones/06-contar-y-estimar-costo): calculadora de costo por request y por mes.
- [`errores/`](errores): cada error común, cómo se ve y cómo se arregla.
  1. [`01-estimar-por-palabras`](errores/01-estimar-por-palabras): código, JSON, números y otros idiomas cuestan más tokens por palabra.
  2. [`02-espacios-y-mayusculas`](errores/02-espacios-y-mayusculas): `gato`, ` gato` y `Gato` son tokens distintos.
  3. [`03-contar-letras`](errores/03-contar-letras): el modelo ve IDs, no letras ni dígitos.
  4. [`04-ignorar-output`](errores/04-ignorar-output): recortar el prompt ahorra menos que acortar la respuesta.
  5. [`05-tokenizer-equivocado`](errores/05-tokenizer-equivocado): cada modelo cuenta distinto.
  6. [`06-cortar-por-caracteres`](errores/06-cortar-por-caracteres): truncar por bytes o caracteres rompe el texto o se pasa del límite.
  7. [`07-no-medir`](errores/07-no-medir): sin el `usage` no ves el caché roto ni la cola larga.

El código está en Python, solo con la librería estándar (nada de instalar paquetes). La idea es que se entienda aunque vengas de otro lenguaje: el foco está en el concepto, no en trucos del lenguaje.

```bash
python3 01-tokens-y-tokenizacion/implementaciones/02-bpe/bpe.py
python3 01-tokens-y-tokenizacion/errores/01-estimar-por-palabras/main.py
```

## Plan del proyecto

Los tokenizers de este proyecto se entrenan sobre un corpus chico: sirven para entender el mecanismo, no para dar números de producción. Para ver los reales:

1. **tiktoken**: tokenizar el mismo texto en inglés, español, código y JSON, y comparar cuántos tokens da cada uno.
2. **SentencePiece**: entrenar un modelo Unigram y uno BPE sobre el mismo corpus y comparar los vocabularios.
3. **Claude `count_tokens`**: contar los mismos textos y compararlos con tiktoken, para ver que cada tokenizer da números distintos.
4. **Costo real**: loguear el `usage` de cien requests reales y armar el costo por request y por mes.
5. **Romperlo a propósito**: reproducir los errores de arriba con un tokenizer real.
