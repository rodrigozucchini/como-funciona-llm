# Contar tokens y estimar costo

Las APIs cobran **por millón de tokens (MTok)**, con un precio distinto para cada tipo de token. Para estimar el costo de un sistema hace falta saber cuántos tokens de cada tipo consume un request típico y multiplicar.

```
costo = input × precio_input
      + output × precio_output              ← incluye los tokens de razonamiento
      + cache_write × precio_input × 1,25   (TTL 5 min) o × 2 (TTL 1 h)
      + cache_read × precio_cache_read
                                            × 0,5 si es batch
```

## Precios (octubre 2026)

| Modelo | Input | Output | Cache read |
|---|---|---|---|
| Claude Fable 5.1 | $10,00 | $50,00 | $0,25 |
| Claude Opus 5.5 | $4,00 | $20,00 | $0,20 |
| Claude Sonnet 5.5 | $2,00 | $10,00 | $0,20 |
| Claude Haiku 5.5 | $0,10 | $0,50 | ~$0,01 |

Dólares por millón de tokens. Haiku 5.5: hasta 100K tokens de prompt ($0,50 / $2,50 por encima); su cache read está estimado con la regla general de 0,1× el input.

> ⚠️ Los precios cambian seguido. Antes de usar estos números para algo real, revisá [la página de precios](https://platform.claude.com/docs/en/about-claude/pricing). En `costo.py` están todos en el diccionario `PRECIOS`, para actualizarlos en un solo lugar.

## De dónde salen los conteos

| Cuándo | Cómo |
|---|---|
| **Antes** de mandar (estimar) | El endpoint `count_tokens` de la API: devuelve los tokens de input exactos para ese modelo, sin generar nada. |
| **Después** de mandar (medir) | El campo `usage` de cada respuesta: `input_tokens`, `output_tokens`, `cache_creation_input_tokens`, `cache_read_input_tokens`. |
| **Nunca** | Contar palabras, dividir caracteres por 4 o usar el tokenizer de otro proveedor (ver [`errores/01-estimar-por-palabras`](../../errores/01-estimar-por-palabras) y [`errores/05-tokenizer-equivocado`](../../errores/05-tokenizer-equivocado)). |

## Lo que muestran los números

**1. El output pesa más.** Con 2.000 tokens de input y 500 de output, el output es el 20% de los tokens y el 56% del costo, porque cada token de output vale 5 veces lo que uno de input.

**2. En un chat, el historial se paga en cada turno.** El turno 20 vuelve a mandar los 19 anteriores. Sin caché, el costo total crece con el **cuadrado** de la cantidad de turnos.

```
Opus 5.5, system prompt de 3.000 tokens, 20 turnos:
  turno   input    sin caché   con caché
      1   3.050     $0,0182     $0,0213    ← escribir en el caché cuesta 1,25x
      2   3.400     $0,0196     $0,0084    ← desde acá ya conviene
     20   9.700     $0,0448     $0,0096
  total:            $0,6300     $0,1921    (70% menos)
```

El prompt caching funciona por **prefijo**: el caché solo sirve si el comienzo del prompt es idéntico byte por byte. Lo estable (system prompt, tools, documentos) va primero y lo que cambia, al final. Eso es tema del proyecto de contexto e inferencia.

**3. El razonamiento se cobra como output.** Un modelo que "piensa" 4.000 tokens antes de responder 500 cuesta ~5 veces más que uno que responde directo. El parámetro `effort` controla cuánto piensa: alto para lo difícil, bajo para lo simple. Lo que importa es el costo **por tarea resuelta**, no por request: una respuesta barata que hay que repetir tres veces no es barata.

**4. Batch cobra la mitad.** Si la respuesta no tiene que ser inmediata (clasificar, resumir, evaluar, procesar un backlog), la Batch API la procesa en horas al 50%.

**5. Dónde conviene recortar** (Opus 5.5, 2.000 input + 500 output):

| Cambio | Ahorro |
|---|---|
| Recortar el prompt 20% | 9% |
| Respuestas 20% más cortas | 11% |
| Cachear 1.500 tokens del prompt | 32% |
| Batch | 50% |

## Correr el ejemplo

```bash
python3 implementaciones/06-contar-y-estimar-costo/costo.py
```

Muestra:

1. El costo de un request en cada modelo, separado en input y output.
2. Un chat de 20 turnos con y sin prompt caching.
3. Cuánto suma el razonamiento al mismo request.
4. El costo mensual de 100.000 requests por día, normal y en batch.
5. Cuánto ahorra cada optimización.

Para usarlo con tus números: importá `costo()` y pasale los tokens del `usage` de tus respuestas reales.

```python
from costo import costo
costo("claude-opus-5-5", input=1200, output=350, cache_read=8000)
```
