# Ventana de contexto y context rot

> Viene de [05. Sampling](../05-siguiente-token-y-sampling/README.md): el modelo genera token por token mirando todo lo anterior. Pero "todo lo anterior" tiene un límite.

---

## 1. Qué es la ventana de contexto

La **ventana de contexto** es la cantidad máxima de tokens que el modelo puede tener en cuenta a la vez. Incluye **todo**:

```
┌──────────────────────────── ventana de contexto ────────────────────────────┐
│ instrucciones │ herramientas │ documentos │ historial del chat │ respuesta  │
└─────────────────────────────────────────────────────────────────────────────┘
```

Lo que no entra en la ventana, **para el modelo no existe**. No tiene memoria entre conversaciones: todo lo que "sabe" de vos en este momento es lo que está ahí adentro.

Los modelos actuales tienen ventanas de cientos de miles de tokens, y algunos llegan al millón. Como referencia, una novela entera ocupa unos 150.000 tokens.

---

## 2. Por qué hay un límite

Por la atención ([tema 03](../03-atencion-self-attention-multi-head/README.md)): cada token mira a todos los anteriores. Con el doble de tokens hay que hacer unas **cuatro veces más comparaciones**, y guardar en memoria información de cada token mientras se genera ([tema 07](../07-kv-cache-prefill-decode-prompt-caching/README.md)).

Además, cada token de la ventana **se paga** en cada pedido. Una ventana grande es posible, pero no gratis.

---

## 3. Qué pasa cuando se llena

Depende de la aplicación:

- **La API da error** si mandás más de lo que entra.
- **Las apps de chat** recortan o resumen los mensajes viejos sin avisar. Por eso, en una conversación muy larga, el modelo "se olvida" de lo que dijiste al principio.
- **La respuesta se corta** si no queda lugar para terminarla.

---

## 4. Context rot: que entre no significa que lo use bien

Aunque todo entre, el rendimiento **baja a medida que la ventana se llena**. A esto se le dice **context rot** (el contexto se "pudre"):

- **Se pierden cosas en el medio.** Los modelos suelen aprovechar mejor lo que está al principio y al final que lo que queda en el medio de un texto largo.
- **El ruido distrae.** Documentos que no vienen al caso, intentos fallidos viejos o instrucciones repetidas compiten con lo importante.
- **Instrucciones que se diluyen.** Una regla dada al principio de una conversación larga pesa menos después de cien mensajes.

```
contexto corto y limpio        →  responde bien
mismo dato + 200 páginas más   →  puede pasarlo por alto o confundirlo con otro
```

La regla práctica: **más contexto no es mejor contexto**. Lo que importa es que lo que está ahí sea lo necesario.

---

## 5. Cómo aprovechar bien la ventana

- **Mandar solo lo relevante.** En vez de pegar un manual entero, buscar las partes que responden la pregunta (eso es RAG, [tema 02](../02-embeddings-y-similitud-coseno/README.md)).
- **Lo importante, al principio o al final.** Las instrucciones clave no deberían quedar enterradas en el medio.
- **Resumir lo viejo.** En conversaciones o tareas largas, reemplazar el historial por un resumen de lo que importa.
- **Empezar de nuevo.** Si una conversación se desvió mucho, a veces lo mejor es abrir una nueva con un resumen.
- **Ordenar y etiquetar.** Separar con títulos o etiquetas qué es instrucción, qué es documento y qué es ejemplo.

---

## Resumen

- La **ventana de contexto** es todo lo que el modelo puede ver a la vez: instrucciones, documentos, historial y respuesta.
- Lo que no está en la ventana, el modelo **no lo sabe**.
- El límite existe porque la atención se vuelve más cara con cada token.
- **Context rot:** con mucho contenido, el modelo usa peor lo que tiene. Menos y más relevante funciona mejor.

**Siguiente:** cómo hace el modelo para no recalcular todo en cada token, y cómo se aprovecha eso para ahorrar → [07. KV cache y prompt caching](../07-kv-cache-prefill-decode-prompt-caching/README.md).
