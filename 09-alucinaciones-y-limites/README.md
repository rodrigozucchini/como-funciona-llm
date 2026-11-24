# Alucinaciones y límites de los LLM

> Viene de [08. Razonamiento](../08-razonamiento-test-time-compute/README.md). Con todo lo anterior ya se puede entender el problema más conocido de los LLM: por qué a veces **inventan** con total seguridad.

---

## 1. Qué es una alucinación

Una **alucinación** es una respuesta que suena correcta y segura, pero es falsa: un dato inventado, una cita que no existe, una función de programación que nadie escribió, un libro con autor y año que nunca se publicó.

Lo peligroso es que **se ve igual que una respuesta correcta**: mismo tono, misma seguridad, mismo formato.

---

## 2. Por qué pasa

Todo sale de lo que vimos en los temas anteriores:

**El modelo predice texto probable, no texto verdadero.** En cada paso elige un token que "encaja" ([tema 05](../05-siguiente-token-y-sampling/README.md)). Si no sabe algo, el texto más probable igual tiene forma de respuesta: un nombre que suena real, un número razonable, una fecha creíble.

```
"El libro 'Historia del mate' fue escrito por…"
   → el modelo no lo sabe, pero sabe cómo suele seguir una frase así
   → "…Juan Carlos Pérez en 1987"        ← suena perfecto, es inventado
```

**No tiene una base de datos adentro.** Lo que "sabe" quedó guardado de forma difusa en sus parámetros durante el entrenamiento. Lo que vio muchas veces (la capital de Francia) lo recuerda bien; lo que vio poco (un dato de nicho, una persona poco conocida) lo recuerda mal o mezclado con otra cosa.

**Su conocimiento tiene fecha de corte.** No sabe nada de lo que pasó después de que se entrenó, salvo que se lo des en el contexto.

**Solo ve lo que está en su ventana.** Si la información no está en el contexto ([tema 06](../06-ventana-de-contexto-y-context-rot/README.md)), la tiene que sacar de memoria, con todos los problemas de arriba.

**Fue entrenado para ser útil.** Responder suele premiarse más que decir "no sé". Los modelos actuales mejoraron mucho en esto, pero la tendencia a completar sigue estando.

---

## 3. Otros límites que conviene conocer

- **No ve letras ni hace cuentas confiables de cabeza** (por los tokens, [tema 01](../01-tokens-y-tokenizacion/README.md)).
- **No sabe la fecha ni la hora**, salvo que se las des.
- **No aprende de la conversación** de forma permanente: cuando termina, no queda nada.
- **Puede dar respuestas distintas** a la misma pregunta (por el sorteo del tema 05).
- **Puede seguirte la corriente:** si la pregunta trae una premisa falsa ("¿por qué Einstein ganó dos Nobel?"), a veces la acepta en vez de corregirla.

---

## 4. Cómo reducirlas

No se eliminan del todo, pero se reducen mucho:

| Qué hacer | Por qué funciona |
|---|---|
| **Darle la información** (documentos, RAG, búsqueda web) | Pasa de recordar a leer: es mucho más confiable copiar de un texto que sacarlo de memoria |
| **Pedirle que cite** de dónde saca cada dato | Si tiene que señalar la frase del documento, inventar es más difícil y verificar es más fácil |
| **Permitirle decir "no sé"** explícitamente | Le saca la presión de responder algo |
| **Darle herramientas** (calculadora, código, búsqueda) | Lo que se puede calcular o buscar no hace falta adivinarlo |
| **Dejarlo razonar** en tareas complejas ([tema 08](../08-razonamiento-test-time-compute/README.md)) | Tiene lugar para revisar antes de contestar |
| **Verificar lo importante** | Datos, citas, cifras y código se chequean antes de usarlos |

---

## 5. Cómo usarlo bien

Pensá en un LLM como un **asistente muy rápido y muy leído, que habla con seguridad aunque no sepa**:

- ✅ Excelente para redactar, resumir, explicar, traducir, programar, ordenar ideas y analizar lo que le das.
- ✅ Muy confiable cuando trabaja sobre información que está en el contexto.
- ⚠️ Desconfiar de datos puntuales sacados de memoria: nombres, fechas, cifras, citas, referencias.
- ⚠️ Cuanto más caro es un error (salud, plata, temas legales), más importa verificar.

---

## Resumen

- Una **alucinación** es una respuesta segura y falsa, que se ve igual que una correcta.
- Pasa porque el modelo **predice texto probable**, no consulta hechos; y lo que vio poco, lo recuerda mal.
- Tiene **fecha de corte**, solo ve **su ventana** y fue entrenado para **responder**.
- Se reduce **dándole la información**, pidiendo **citas**, permitiendo **"no sé"**, dándole **herramientas** y **verificando**.

---

**Fin del recorrido.** De texto a tokens, de tokens a vectores, de vectores a atención, de atención a un modelo que predice el próximo token, y lo que eso implica al usarlo. Volver al [índice](../README.md).
