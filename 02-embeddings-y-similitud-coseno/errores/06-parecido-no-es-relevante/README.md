# Confundir "parecido" con "relevante"

Los embeddings capturan muy bien **de qué habla** un texto, y bastante peor **qué dice** sobre eso. Dos textos sobre el mismo tema con conclusiones opuestas quedan muy cerca.

```
"el producto funciona perfecto"     vs  "el producto no funciona"        ->  alto
"el vuelo sale a las 10"            vs  "el vuelo sale a las 22"         ->  altísimo
"¿cómo cancelo el plan?"            vs  "¿cómo contrato el plan?"        ->  alto
"pacientes que deben tomar X"       vs  "pacientes que NO deben tomar X" ->  alto
```

Es una consecuencia de cómo se entrenan: los pares de entrenamiento enseñan sobre todo "mismo tema = cerca". La negación es una palabra; los números, unos pocos tokens; la intención (cancelar vs contratar), un detalle frente a todo lo que comparten.

Cómo aparece en la práctica:

- **RAG que responde lo contrario**: trae el párrafo de "quiénes **no** pueden" para la pregunta "quiénes pueden", y el LLM lo usa.
- **Detección de duplicados** que junta tickets opuestos ("no puedo entrar" con "ya puedo entrar").
- **Recomendaciones** que sugieren lo mismo que el usuario acaba de rechazar.
- **Búsqueda con números o fechas**: el chunk de otra fecha u otra versión aparece primero.
- **Siempre hay un top-k**: aunque no haya nada relevante, la búsqueda devuelve los k "más parecidos", y se tratan como si respondieran.

**Fix:**
- **Reranker (cross-encoder)** sobre los primeros 20–100 resultados: lee la consulta y cada candidato juntos y distingue mucho mejor negación e intención (ver [`implementaciones/03-embeddings-contextuales`](../../implementaciones/03-embeddings-contextuales)).
- **Filtros por metadata** para lo que es exacto: fechas, versiones, producto, idioma. No pedirle al embedding que distinga "v2" de "v3".
- Que el sistema pueda decir **"no encontré nada"**: un umbral calibrado (ver [`03-umbral-fijo`](../03-umbral-fijo)) o un reranker que descarte.
- En RAG, pedirle al LLM que verifique que el contexto responde la pregunta antes de usarlo.
- Incluir casos con negaciones y opuestos en el set de evaluación (ver [`08-no-medir`](../08-no-medir)).
