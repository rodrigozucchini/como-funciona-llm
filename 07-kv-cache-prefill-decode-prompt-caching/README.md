# KV cache, prefill, decode y prompt caching

> Viene de [06. Ventana de contexto](../06-ventana-de-contexto-y-context-rot/README.md): el modelo mira todo el contexto para generar cada token. Si lo recalculara todo cada vez, sería lentísimo. Este tema explica el truco que lo evita, y cómo ese mismo truco abarata los pedidos.

---

## 1. Dos etapas: leer y escribir

Cuando le mandás un pedido a un LLM pasan dos cosas distintas:

| Etapa | Qué hace | Cómo es |
|---|---|---|
| **Prefill** (leer) | Procesa todo tu prompt | **Todo a la vez**, en paralelo. Rápido aunque el prompt sea largo |
| **Decode** (escribir) | Genera la respuesta | **De a un token**, porque cada uno depende del anterior. Es la parte lenta |

Por eso hay dos tiempos que importan:
- **Tiempo hasta el primer token:** cuánto tarda en empezar a responder. Depende sobre todo del largo del prompt (prefill).
- **Velocidad de escritura:** tokens por segundo una vez que arrancó (decode).

Y por eso una respuesta larga tarda más que un prompt largo: leer es en paralelo, escribir no.

---

## 2. KV cache: no recalcular lo que ya se hizo

En la atención ([tema 03](../03-atencion-self-attention-multi-head/README.md)) cada token calcula una **key** (cómo lo encuentran los demás) y un **value** (qué información aporta). Gracias a la máscara causal, lo calculado para un token **nunca cambia** cuando se agregan tokens nuevos después.

Entonces se guarda. Esa memoria es la **KV cache**:

```
sin cache:   token 100 → recalcular keys y values de los tokens 1 a 99 → generar
             token 101 → recalcular keys y values de los tokens 1 a 100 → generar   (cada vez más lento)

con cache:   token 100 → usar lo guardado de 1 a 99, calcular solo el 100, guardarlo
             token 101 → usar lo guardado de 1 a 100, calcular solo el 101, guardarlo
```

Cada token nuevo solo calcula lo suyo. El costo: **memoria**. La KV cache crece con cada token del contexto, y es una de las razones por las que las ventanas de contexto tienen límite.

---

## 3. Prompt caching: reusar entre pedidos

La KV cache vive dentro de un pedido. El **prompt caching** va un paso más allá: guarda la KV cache del **comienzo de un prompt** para reusarla en el pedido siguiente.

Es muy útil porque muchos pedidos empiezan igual:

```
pedido 1:  [instrucciones largas] [documento de 50 páginas] [pregunta 1]
pedido 2:  [instrucciones largas] [documento de 50 páginas] [pregunta 2]
            └──────────── igual: se reusa del caché ────────┘  └─ nuevo ─┘
```

En un chat pasa en cada turno: el historial se vuelve a mandar entero, y solo cambia el mensaje nuevo.

**Lo que ganás:**
- **Más barato:** leer del caché cuesta alrededor del **10%** del precio normal del input. Guardarlo la primera vez cuesta un poco más (alrededor de 1,25×).
- **Más rápido:** se saltea el prefill de la parte cacheada, así que la respuesta arranca antes.

---

## 4. La regla para que funcione: mismo comienzo, exacto

El caché funciona por **prefijo**: sirve solo si el comienzo del prompt es **idéntico**, carácter por carácter. Un solo cambio invalida todo lo que viene después.

```
✅  [instrucciones fijas] [documentos] [historial] [mensaje nuevo]
     lo estable primero ─────────────────────────► lo que cambia al final

❌  [fecha y hora actual] [instrucciones] [documentos] …
     cambia en cada pedido → nunca se reusa nada
```

- Poner **lo que no cambia al principio** (instrucciones, herramientas, documentos) y **lo que cambia al final**.
- No meter cosas variables (la hora, un ID aleatorio) al comienzo.
- El caché dura poco: unos **5 minutos** sin uso por defecto (hay opciones de hasta 1 hora). Sirve para pedidos seguidos, no para el mes que viene.
- Para saber si funciona, mirar el `usage` de cada respuesta: indica cuántos tokens se leyeron del caché.

---

## Resumen

- **Prefill** lee el prompt entero en paralelo; **decode** escribe la respuesta de a un token.
- La **KV cache** guarda lo calculado para cada token, así no se recalcula. Cuesta memoria.
- El **prompt caching** reusa esa cache entre pedidos que empiezan igual: más barato y más rápido.
- Solo funciona si el **comienzo es idéntico**: lo fijo primero, lo variable al final.

**Siguiente:** qué pasa cuando el modelo usa tokens extra para "pensar" antes de responder → [08. Modelos de razonamiento](../08-razonamiento-test-time-compute/README.md).
