# One-hot y bag of words

La forma más directa de convertir texto en números: **cada palabra del vocabulario es una dimensión**. Es el punto de partida, y entender por qué no alcanza explica para qué existen los embeddings.

## One-hot

Cada palabra es un vector con un único `1` en su posición y `0` en todas las demás.

```
vocabulario:  [ perro, gato, can, come, avión ]

perro  ->  [ 1, 0, 0, 0, 0 ]
gato   ->  [ 0, 1, 0, 0, 0 ]
can    ->  [ 0, 0, 1, 0, 0 ]
avión  ->  [ 0, 0, 0, 0, 1 ]
```

El problema se ve enseguida: **todos los vectores están a la misma distancia de todos**. El coseno entre dos palabras distintas siempre da 0 (no comparten ninguna posición con un 1). Para este modelo, `perro` y `can` son tan distintos como `perro` y `avión`.

## Bag of words

Un texto es la **suma** de los one-hot de sus palabras: cuenta cuántas veces aparece cada una. El orden se pierde (por eso "bolsa" de palabras).

```
vocabulario:  [ el, perro, gato, come, carne, pescado ]

"el perro come carne"    ->  [ 1, 1, 0, 1, 1, 0 ]
"el gato come pescado"   ->  [ 1, 0, 1, 1, 0, 1 ]
"carne come el perro"    ->  [ 1, 1, 0, 1, 1, 0 ]   ← idéntico al primero
```

Con estos vectores ya se puede calcular un coseno: los dos primeros comparten `el` y `come`, así que dan 0,5. El primero y el tercero dan 1, aunque digan algo distinto (o absurdo).

## TF-IDF

Una mejora: no todas las palabras pesan igual. `el` aparece en todos los documentos y no dice nada; `pescado` aparece en pocos y dice mucho.

- **TF** (*term frequency*): cuántas veces aparece la palabra en este documento.
- **IDF** (*inverse document frequency*): qué tan rara es en toda la colección. Cuanto más rara, más pesa.
- El peso de cada palabra es **TF × IDF**.

Con TF-IDF, `el` queda casi en 0 y las palabras que distinguen a cada documento quedan con peso alto. Es la base de BM25, que sigue siendo muy bueno para búsqueda por palabras clave (ver [`errores/07-palabras-exactas`](../../errores/07-palabras-exactas)).

## Denso vs disperso

| | Bag of words / TF-IDF | Embedding |
|---|---|---|
| Dimensión | Tamaño del vocabulario (decenas de miles o más) | Fija y chica (cientos a pocos miles) |
| Valores | Casi todos 0 (**disperso**) | Todos con información (**denso**) |
| Qué significa cada dimensión | Una palabra concreta | Nada interpretable por separado |
| `perro` vs `can` | Sin relación | Cerca |

## ✅ / ❌

- ✅ No hay que entrenar nada: se arma contando.
- ✅ Interpretable: sabés exactamente por qué dos textos se parecen (comparten estas palabras).
- ✅ Muy bueno para coincidencias exactas: nombres, códigos, términos técnicos.
- ❌ No entiende sinónimos ni paráfrasis: `reseteo mi contraseña` y `olvidé la clave` no comparten nada.
- ❌ Pierde el orden: `el perro muerde al hombre` = `el hombre muerde al perro`.
- ❌ Vectores enormes y casi vacíos; una palabra que no está en el vocabulario no existe.
- ❌ No funciona entre idiomas: `dog` y `perro` son dimensiones distintas.
