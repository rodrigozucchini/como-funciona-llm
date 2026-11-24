# Tokens y tokenización

> Punto de partida: un LLM no lee letras ni palabras, solo **números**. Este tema explica cómo el texto se convierte en esos números.

---

## 1. Texto → tokens → números

Un **tokenizer** parte el texto en pedazos llamados **tokens** y le da a cada uno un número (su **ID**) sacado de una lista fija, el **vocabulario**. El modelo recibe números, devuelve números, y el tokenizer los vuelve a convertir en texto.

```
"los gatitos comen"
        │  partir
        ▼
 [ "▁los" | "▁gatit" | "os" | "▁comen" ]      ▁ = espacio (va pegado a la palabra que sigue)
        │  buscar en el vocabulario
        ▼
 [  412   ,   9081   ,  278 ,   3305   ]  ──►  modelo  ──►  1534  ──►  " pescado"
```

Todo en un LLM se mide en tokens: cuánto texto entra, cuánto tarda en responder y **cuánto cuesta**.

---

## 2. ¿De qué tamaño son los pedazos?

Hay dos opciones obvias, y ninguna sirve:

- **Por letras:** el vocabulario es chico (unos cientos de símbolos), pero un texto se vuelve larguísimo. Cada token es un paso de trabajo para el modelo, así que todo se vuelve lento y caro.
- **Por palabras:** el texto queda corto, pero el vocabulario no tiene fin: `gato`, `gatos`, `gatito`, `gatitas`… cada variante es una entrada distinta, sin relación entre sí. Y una palabra que no estaba en la lista no se puede representar.

La solución es el punto medio: **pedazos de palabra** (*subwords*). Lo frecuente queda entero (`▁los`) y lo raro se arma con partes (`▁gatit` + `os`). Los modelos actuales usan vocabularios de 50.000 a 200.000 tokens.

| | Por letras | Por palabras | Subwords |
|---|---|---|---|
| Tamaño del vocabulario | Chico | Infinito | 50k–200k, fijo |
| Largo del texto en tokens | Muy largo | Corto | Casi tan corto como por palabras |
| Palabra nueva | Se puede | No se puede | Se arma con pedazos |

---

## 3. Cómo se elige qué pedazos existen

### BPE (Byte Pair Encoding): fusionar lo que más se repite

Se toma muchísimo texto, se lo parte en letras, y se repite un único paso: **buscar el par de vecinos que más aparece y juntarlo en un pedazo nuevo**.

```
inicio:   ▁ l o s   ▁ g a t o s   ▁ p e r r o s
paso 1:   "o"+"s" es el par más frecuente  →  ▁ l os   ▁ g a t os   ▁ p e r r os
paso 2:   "▁"+"l"                           →  ▁l os    ▁ g a t os   ▁ p e r r os
...
paso N:                                        ▁los     ▁gatos       ▁perros
```

Cada fusión agrega un token al vocabulario. Se frena al llegar al tamaño buscado. Después, para partir un texto nuevo, se aplican las mismas fusiones en el mismo orden: una palabra que nunca vio igual se arma con pedazos conocidos (`gatitas` → `▁gatit | a | s`).

### Byte-level BPE: arrancar de bytes

El mismo método, pero en vez de arrancar de letras arranca de los **256 bytes** con los que la computadora guarda cualquier texto. Así **cualquier cosa se puede representar** (emojis, chino, símbolos raros): en el peor caso, byte por byte. **Es lo que usan casi todos los LLM actuales.**

El costo: lo que el tokenizer vio poco al entrenar se parte en muchos pedazos. Un emoji puede ser 4 tokens.

### Unigram (SentencePiece): podar en vez de fusionar

El camino inverso: arranca con una lista **enorme** de pedazos posibles y va **sacando** los que menos aportan hasta llegar al tamaño buscado. Funciona igual de bien en idiomas sin espacios, como japonés o chino. Lo usan modelos como T5.

---

## 4. Consecuencias que se notan al usar un LLM

**El modelo no ve letras.** Recibe `▁strawberry` como 2 o 3 números, no como 10 letras. Por eso le cuesta contar cuántas "r" tiene una palabra, invertirla o hacer cuentas largas "de cabeza": los números también se parten de forma arbitraria (`2024` puede ser `202 | 4`). Para eso conviene darle una herramienta (que ejecute código).

**Espacios y mayúsculas cambian los tokens.** `gato`, ` gato` y `Gato` son tokens distintos. Un ejemplo con formato inconsistente o un prompt que termina en espacio pueden empeorar la respuesta.

**No todos los textos cuestan lo mismo.** La regla "1 palabra ≈ 1 token" sirve más o menos para prosa en inglés. El código, el JSON, las URLs, los números y otros idiomas usan bastantes más tokens por palabra. El mismo contenido en español o japonés puede costar bastante más que en inglés.

**Cada modelo tiene su tokenizer.** El mismo texto da otra cantidad de tokens en Claude, en GPT o en Llama, e incluso entre versiones del mismo modelo. Para contar bien hay que usar el del modelo exacto.

---

## 5. Tokens especiales

El modelo no recibe "mensajes de un chat": recibe **una sola tira de tokens**. Para marcar quién habla y dónde termina cada mensaje se usan **tokens especiales**, números reservados que nunca salen del texto común:

```
[<inicio>] [<system>] respondé corto. [<fin>] [<user>] ¿qué comen los gatos? [<fin>] [<assistant>]  ← el modelo sigue desde acá
```

Cuando el modelo termina de responder, **genera** el token de fin; así se sabe cuándo cortar. Estos marcadores, y la descripción de las herramientas que le das al modelo, también cuentan como tokens.

---

## 6. Costo por token

Las APIs cobran **por millón de tokens**, con un precio distinto según el tipo:

| Tipo | Qué es | Precio relativo |
|---|---|---|
| **Input** | Todo lo que mandás: instrucciones, historial, documentos | 1× |
| **Output** | Lo que escribe el modelo, **incluido lo que "piensa"** antes de responder | ~5× |
| **Caché** | Reusar un comienzo de prompt que ya se mandó | ~0,1× |
| **Batch** | Pedidos sin apuro, procesados en horas | 50% de descuento |

```
Ejemplo con Opus 5.5 ($4 input / $20 output por millón, octubre 2026):
  2.000 tokens de input  →  $0,008
    500 tokens de output →  $0,010   ← un quinto de los tokens, más de la mitad del costo
```

Tres consecuencias:
1. **La respuesta pesa más que la pregunta**: pedir respuestas cortas ahorra más que recortar el prompt.
2. **En un chat, todo el historial se vuelve a mandar en cada turno**: el turno 20 paga los 19 anteriores. Para eso existe el caché.
3. **Lo que no se mide no se ve**: cada respuesta de la API trae cuántos tokens usó (`usage`). Guardarlo es la única forma de saber de dónde sale el costo.

> Los precios cambian seguido: [página de precios de Claude](https://platform.claude.com/docs/en/about-claude/pricing).

Para ver cómo se parte un texto real: [tiktokenizer.vercel.app](https://tiktokenizer.vercel.app).

---

## Resumen

- Un LLM trabaja con **números**: el tokenizer convierte texto en tokens y cada token en un ID.
- Los tokens son **pedazos de palabra**: lo frecuente entero, lo raro en partes.
- El vocabulario se arma **fusionando** lo que más se repite (BPE) o **podando** una lista grande (Unigram).
- Por eso el modelo **no ve letras**, y el mismo contenido **cuesta distinto** según el idioma, el formato y el modelo.
- Se paga **por token**, y la respuesta cuesta ~5 veces más que la pregunta.

**Siguiente:** cada ID se convierte en una lista de números que representa su significado → [02. Embeddings](../02-embeddings-y-similitud-coseno/README.md).
