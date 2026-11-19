# Búsqueda semántica

Juntar todo lo anterior: guardar los embeddings de muchos documentos y, dada una consulta, **devolver los k más parecidos** (top-k). Es la base de RAG, de los buscadores internos y de los sistemas de recomendación.

## El flujo completo

```
INDEXAR (una vez, y cada vez que cambian los documentos)

 documentos ──► cortar en chunks ──► modelo de embeddings ──► vectores ──► base vectorial
                                                                          (vector + texto + metadata)

BUSCAR (en cada consulta)

 consulta ──► modelo de embeddings ──► vector ──► top-k por similitud ──► chunks más parecidos
              (mismo modelo, modo "query")
```

Dos reglas que no se negocian: **el mismo modelo** para indexar y para buscar, y **la misma métrica** con la que se entrenó.

## Fuerza bruta (búsqueda exacta)

Comparar la consulta contra **todos** los vectores y quedarse con los k mejores.

```
consulta · doc₁   = 0,31
consulta · doc₂   = 0,87   ◄ top 1
consulta · doc₃   = 0,12
consulta · doc₄   = 0,79   ◄ top 2
...
consulta · doc_N  = 0,44
```

El costo crece lineal con la cantidad de documentos: con 1 millón de vectores de 1024 dimensiones son unos mil millones de multiplicaciones por consulta. Para miles o pocas decenas de miles de documentos, **la fuerza bruta alcanza y es exacta**. Recién más arriba conviene un índice.

## Índices aproximados (ANN)

La idea: **no comparar contra todo**. Se acepta perderse de vez en cuando alguno de los verdaderos top-k a cambio de ser cientos de veces más rápido. Lo que se pierde se mide con el **recall**: de los k vecinos reales, cuántos encontró el índice.

### HNSW (grafo de mundo pequeño)

Cada vector es un nodo conectado a sus vecinos más cercanos. Se arman varias capas: arriba pocos nodos con conexiones largas, abajo todos con conexiones cortas.

```
capa 2:   A ─────────────────────── F                 saltos largos
          │                          │
capa 1:   A ──────── C ──────────── F ──── H          saltos medianos
          │          │              │      │
capa 0:   A ── B ── C ── D ── E ── F ── G ── H ── I   todos, vecinos cercanos
```

Buscar es como llegar a una dirección: primero autopista (capa alta) hasta la zona, después calles (capas bajas) hasta el lugar. En cada nodo se salta al vecino más parecido a la consulta, hasta que ninguno mejora.

- ✅ Muy rápido y con recall alto. Es el índice por defecto en pgvector, Qdrant, Weaviate, Milvus y Elasticsearch.
- ❌ Usa bastante memoria (el grafo además de los vectores) y construirlo es lento.
- Parámetros: cuántos vecinos por nodo (`M`) y cuántos candidatos explorar al buscar (`ef`). Más = mejor recall y más lento.

### IVF (índice de archivos invertidos)

Se agrupan los vectores en clusters (por ejemplo con k-means). Cada cluster tiene un centro.

```
         ┌─────────┐   ┌─────────┐   ┌─────────┐
         │ ●  ●    │   │    ●    │   │  ●   ●  │
         │   ★ ●   │   │ ● ★  ●  │   │ ●  ★    │   ★ = centro del cluster
         │ ●    ●  │   │   ●     │   │    ●  ● │
         └─────────┘   └─────────┘   └─────────┘
                              ▲
                              │ la consulta cae acá: se busca solo en este cluster
                              │ (y en los nprobe más cercanos)
```

Para buscar: se compara la consulta contra los centros, se eligen los `nprobe` clusters más cercanos y se busca por fuerza bruta solo adentro de esos.

- ✅ Menos memoria que HNSW; se combina bien con compresión (PQ).
- ❌ Si el vecino real quedó en un cluster que no se miró, se pierde. Más `nprobe` = mejor recall y más lento.
- ❌ Hay que entrenar los clusters con datos representativos.

### Product Quantization (PQ)

No es un índice sino una forma de **comprimir** los vectores: se parte cada vector en pedazos y cada pedazo se reemplaza por el ID del "prototipo" más parecido. Un vector de 4 KB puede quedar en unas decenas de bytes. Se usa junto con IVF cuando no entra todo en memoria.

## Comparación

| | Fuerza bruta | HNSW | IVF | IVF + PQ |
|---|---|---|---|---|
| Recall | 100% | Muy alto | Alto | Medio–alto |
| Velocidad | Lenta con muchos datos | Muy rápida | Rápida | Rápida |
| Memoria | Vectores | Vectores + grafo | Vectores | Muy poca |
| Cuándo | Hasta decenas de miles | El default | Datos grandes | Datos enormes |

## Filtros

En la práctica casi nunca se busca "en todo": se busca en los documentos de **este cliente**, de **este año**, en **este idioma**. Cómo combina la base vectorial el filtro con el índice importa:

- **Filtrar después**: se buscan los top-k y se descartan los que no cumplen. Si el filtro es muy restrictivo, pueden quedar 0 resultados.
- **Filtrar antes / durante**: se busca solo entre los que cumplen. Más correcto, y las bases modernas lo soportan, pero puede ser más lento.

## Dónde se guarda

| Opción | Qué es |
|---|---|
| **FAISS** | Librería (no base de datos) para índices en memoria. |
| **pgvector** | Extensión de PostgreSQL: vectores en la misma base que el resto de los datos. |
| **Qdrant, Weaviate, Milvus, Chroma** | Bases vectoriales dedicadas, con filtros y API propia. |
| **Elasticsearch / OpenSearch** | Buscadores de texto que también soportan vectores: cómodos para búsqueda híbrida. |
| **Servicios gestionados** | Pinecone, Turbopuffer y las ofertas de cada nube. |

## ✅ / ❌

- ✅ Encuentra por significado: sinónimos, paráfrasis, otro idioma.
- ✅ Los documentos se embeddean una vez; cada consulta es un embedding y una búsqueda.
- ✅ Con un índice ANN escala a cientos de millones de vectores.
- ❌ Los índices aproximados pierden resultados, y no avisan: hay que medir el recall (ver [`errores/08-no-medir`](../../errores/08-no-medir)).
- ❌ Malo para coincidencias exactas (códigos, IDs): ver [`errores/07-palabras-exactas`](../../errores/07-palabras-exactas).
- ❌ Siempre devuelve k resultados, aunque ninguno sea relevante: "el más parecido" puede ser malo igual.
