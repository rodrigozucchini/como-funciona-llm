# Embeddear la consulta igual que los documentos

En búsqueda, lo que se compara no es simétrico: una **consulta** es corta y es una pregunta ("¿cómo cancelo el plan?"); un **documento** es largo y es una respuesta ("Para cancelar tu suscripción, entrá en..."). Muchos modelos se entrenan sabiendo eso y esperan que les digas de qué lado está cada texto.

Las formas más comunes:

| Cómo lo pide el modelo | Ejemplo |
|---|---|
| **Prefijo en el texto** | `query: ¿cómo cancelo el plan?` / `passage: Para cancelar tu suscripción...` (familia E5 y otras) |
| **Instrucción** | `Instruct: dada una pregunta, encontrá el pasaje que la responde\nQuery: ...` |
| **Parámetro de la API** | Un `input_type` (o `task_type`) con valores tipo "query" / "document" |

Si no se respeta, el modelo **funciona igual** pero rinde peor. No hay error, solo resultados un poco más flojos que nadie compara con nada.

Cómo aparece en la práctica:

- **Sin prefijos ni tipo**: se usa el modelo como si fuera simétrico.
- **Prefijo solo en un lado**: se agregó `passage: ` al indexar y se olvidó `query: ` en las consultas (o al revés).
- **El mismo tipo para todo**: se indexó con tipo "query" porque era el valor de ejemplo de la documentación.
- **Usar el modo asimétrico para comparar pares iguales**: para detectar duplicados entre dos documentos, los dos son del mismo tipo.

Y al revés: un modelo simétrico (entrenado con paráfrasis) puede rendir mal emparejando preguntas cortas con documentos largos.

**Fix:**
- Leer la ficha del modelo: si usa prefijos, instrucciones o `input_type`, usarlos **exactamente** como dice, en los dos lados.
- Consulta → modo consulta. Documento → modo documento. Comparar dos textos del mismo tipo → el modo simétrico que indique el modelo.
- Guardar el modo usado junto con los vectores, igual que el modelo (ver [`01-mezclar-modelos`](../01-mezclar-modelos)).
- Medir con y sin, sobre tus consultas reales (ver [`08-no-medir`](../08-no-medir)).
