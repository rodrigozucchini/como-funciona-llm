# Cortar mal los chunks

Un embedding es **un solo vector por texto**. Si el texto habla de muchas cosas, el vector termina siendo un promedio de todas, y no se parece especialmente a ninguna. Si el texto es demasiado chico, pierde el contexto que le da sentido.

```
chunk enorme (todo el manual):
  instalación + facturación + seguridad + API + preguntas frecuentes
                         │
                         ▼
              un vector "de todo un poco"
  consulta "¿cómo roto la API key?"  ->  coseno mediocre, aunque la respuesta esté adentro

chunk diminuto:
  "Hacé click en Regenerar."
                         │
                         ▼
  ¿regenerar qué? el vector no sabe que esto es sobre la API key
```

Cómo aparece en la práctica:

- **Chunks muy largos**: un documento entero o páginas completas en un solo vector. La búsqueda trae el documento correcto a veces, y cuando lo trae, el LLM recibe mucho texto que no necesita.
- **Chunks muy cortos**: oraciones sueltas. Se pierden referencias ("esto", "el paso anterior") y aparecen muchos falsos positivos.
- **Cortar por cantidad fija de caracteres**: el corte cae en la mitad de una oración, de una tabla o de un bloque de código.
- **Truncado silencioso**: el chunk pasa el límite de tokens del modelo. Según el proveedor, da error o **se trunca sin avisar**: el final del texto no está en el vector, aunque sí esté guardado como texto. La búsqueda nunca lo encuentra por lo que decía al final.
- **Tablas, código y listas** cortados como si fueran prosa.

**Fix:**
- Cortar por **estructura**: secciones, títulos, párrafos; bloques de código y tablas enteros.
- Un tamaño en tokens (no en caracteres) cómodamente por debajo del límite del modelo. Para RAG suele andar bien algo de unos cientos de tokens, pero depende del contenido: medir.
- Un poco de **solapamiento** entre chunks para no partir una idea en dos.
- Agregar **contexto** a cada chunk: el título del documento y de la sección ("Manual > Seguridad > API keys: Hacé click en Regenerar...").
- Verificar el conteo de tokens antes de embeddear y desactivar el truncado automático, para que un chunk largo falle en vez de perderse en silencio.
