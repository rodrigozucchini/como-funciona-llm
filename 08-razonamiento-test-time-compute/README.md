# Modelos de razonamiento y test-time compute

> Viene de [07. KV cache](../07-kv-cache-prefill-decode-prompt-caching/README.md). Hasta acá, el modelo responde directo: token tras token, sin pausa. Este tema explica qué cambia cuando **piensa antes de responder**.

---

## 1. El problema: un token tiene un esfuerzo fijo

Cada token sale de pasar por el modelo **una sola vez**: la misma cantidad de cálculo para decir "hola" que para resolver un problema difícil. Si la respuesta tiene que salir de una, no hay lugar para probar, equivocarse y corregir.

Con una persona pasa lo mismo: si te preguntan `17 × 24` y tenés que contestar en el acto, es fácil errarle. Si podés hacer la cuenta en un papel, no.

---

## 2. La solución: escribir el razonamiento

Si el modelo **escribe los pasos intermedios**, cada paso queda en el contexto y el siguiente se apoya en él. Cada token extra es más cálculo dedicado al problema.

```
sin razonar:   "¿17 × 24?"  →  "418"                         ✗

razonando:     "¿17 × 24?"  →  "17 × 20 = 340
                                17 × 4  = 68
                                340 + 68 = 408"  →  "408"    ✓
```

Los **modelos de razonamiento** están entrenados para hacer esto solos: antes de la respuesta generan un bloque de "pensamiento" donde descomponen el problema, prueban caminos, detectan errores y se corrigen.

---

## 3. Test-time compute: gastar más al responder

Hay dos formas de que un modelo rinda más:

| | Cuándo se gasta | Ejemplo |
|---|---|---|
| **Entrenamiento** | Antes, una vez | Un modelo más grande, más datos |
| **Test-time compute** | En cada respuesta | Dejarlo pensar más tokens antes de contestar |

La idea clave: **dejar pensar más al mismo modelo mejora sus resultados** en tareas difíciles (matemática, programación, planificación, análisis con muchos pasos). Es como darle más tiempo a la misma persona.

---

## 4. El costo: pensar se paga

Los tokens de pensamiento **son tokens de output**: se cobran como tales (el tipo más caro, [tema 01](../01-tokens-y-tokenizacion/README.md)) y se generan de a uno, así que tardan.

```
respuesta directa:           500 tokens de output
pensar + responder:   4.000 + 500 tokens de output    → ~9 veces más caro y más lento
```

Muchas veces no ves el pensamiento completo (se muestra un resumen o nada), pero igual se cobra.

Por eso se puede **regular cuánto piensa**. En la API de Claude, por ejemplo, con un parámetro de **esfuerzo** (*effort*):

- **Bajo:** respuestas rápidas y baratas. Para tareas simples: clasificar, extraer datos, responder algo directo.
- **Alto:** más pensamiento. Para problemas difíciles, donde equivocarse sale caro.

Lo que importa es el costo **por tarea bien resuelta**: una respuesta barata que hay que repetir tres veces no es barata.

---

## 5. Cuándo vale la pena

- ✅ Problemas de varios pasos: matemática, código, lógica, planificación.
- ✅ Tareas donde un error es caro y conviene que el modelo se revise.
- ❌ Preguntas simples o de conocimiento puntual: pensar más no agrega nada y solo suma demora.
- ❌ Datos que el modelo no tiene: pensar no reemplaza información que falta ([tema 09](../09-alucinaciones-y-limites/README.md)).

---

## Resumen

- Cada token sale con un **esfuerzo fijo**; para problemas difíciles no alcanza responder de una.
- Los **modelos de razonamiento** escriben pasos intermedios antes de responder y se corrigen solos.
- **Test-time compute:** gastar más cálculo al responder mejora los resultados en tareas difíciles.
- Pensar **se paga como output** y tarda. Se regula con el **esfuerzo**: bajo para lo simple, alto para lo difícil.

**Siguiente:** por qué un modelo puede responder con total seguridad algo falso → [09. Alucinaciones y límites](../09-alucinaciones-y-limites/README.md).
