# Buscar palabras exactas con embeddings

Los embeddings son buenos justamente porque **generalizan**: `auto` ≈ `coche`. Esa misma virtud es un problema cuando lo que se busca es una cadena exacta, que no tiene sinónimos.

```
consulta:  "ERR-4012"

resultados por embeddings:
  1. "ERR-4021: timeout de conexión"        ← parecido, no es
  2. "ERR-4102: credenciales inválidas"     ← parecido, no es
  3. "Lista de errores de la serie 4000"
  ...
  9. "ERR-4012: cuota excedida"             ← el que se buscaba
```

Para el modelo, `ERR-4012` y `ERR-4021` son casi el mismo texto: los mismos tokens en otro orden. Lo mismo pasa con:

- **Códigos e IDs**: SKUs, números de factura, códigos de error, hashes, números de ticket.
- **Nombres propios raros**: apellidos, productos internos, siglas de la empresa que el modelo nunca vio.
- **Términos técnicos muy específicos**: nombres de funciones, flags, nombres de tablas.
- **Consultas de una sola palabra**: hay muy poco significado para "entender", y el embedding termina trayendo cosas del mismo tema.

Acá la búsqueda por palabras clave (BM25, la evolución de TF-IDF, ver [`implementaciones/01-one-hot-y-bag-of-words`](../../implementaciones/01-one-hot-y-bag-of-words)) gana fácil: `ERR-4012` es un término raro, con muchísimo peso, y solo aparece en un documento.

**Fix: búsqueda híbrida.**

```
consulta ──┬──► embeddings ──► ranking semántico ──┐
           │                                       ├──► combinar ──► (reranker) ──► top-k
           └──► BM25       ──► ranking por palabras┘
```

- Correr las dos búsquedas y **combinar los rankings**. La forma más simple y robusta es *Reciprocal Rank Fusion* (RRF): cada documento suma puntos según la posición en la que quedó en cada lista. No hace falta que los puntajes de las dos búsquedas estén en la misma escala, porque usa solo las posiciones.
- Si la consulta tiene forma de código o ID (por un patrón reconocible), además se puede **filtrar por coincidencia exacta**.
- Bases como Elasticsearch, OpenSearch, Weaviate, Qdrant o PostgreSQL (full-text + pgvector) permiten hacer las dos cosas en el mismo lugar.
- Medir con consultas de los dos tipos (conceptuales y exactas): la híbrida casi nunca es peor que cualquiera de las dos sola.
