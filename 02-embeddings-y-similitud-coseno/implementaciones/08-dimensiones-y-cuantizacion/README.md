# Dimensiones y cuantización

Los vectores ocupan memoria, y la memoria se paga en cada búsqueda y todos los meses. Hay dos formas de achicarlos: **menos números** (menos dimensiones) o **números más chicos** (cuantización).

## Cuánto ocupa un vector

```
tamaño = dimensiones × bytes por número

1536 dimensiones × 4 bytes (float32) = 6.144 bytes ≈ 6 KB por vector

× 1.000.000 de chunks = 6,1 GB
× 100.000.000         = 614 GB
```

Y para que la búsqueda sea rápida, casi todo eso tiene que estar en RAM (más el grafo del índice, si es HNSW).

## Menos dimensiones: Matryoshka

Normalmente no se puede cortar un vector por la mitad: la información está repartida en todas las dimensiones. Los modelos entrenados con **Matryoshka Representation Learning** son distintos: se los entrena para que **las primeras dimensiones lleven lo más importante**, como las muñecas rusas, una adentro de otra.

```
vector completo:   [ ████████ ▓▓▓▓▓▓▓▓ ▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒ ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░ ]
                     primeras   ...                         últimas
                     256        512        1024              2048
                     ─────┬────
                          └─ ya sirve sola, con algo menos de precisión
```

Con un modelo así se pueden guardar solo las primeras 256 o 512 dimensiones. Varios proveedores lo exponen como un parámetro de "dimensiones" al pedir el embedding.

Dos cuidados:
- **Solo funciona con modelos entrenados así.** Cortar un vector de un modelo común destruye la información.
- **Después de cortar hay que volver a normalizar**: el vector recortado ya no mide 1 (ver [`errores/02-no-normalizar`](../../errores/02-no-normalizar)).

## Números más chicos: cuantización

Cada dimensión es un `float32` (4 bytes). Se puede representar con menos:

| Formato | Bytes por dimensión | Tamaño (1M × 1536) | Pérdida de calidad |
|---|---|---|---|
| `float32` | 4 | 6,1 GB | — |
| `float16` | 2 | 3,1 GB | Casi nula |
| `int8` | 1 | 1,5 GB | Chica |
| Binario | 1/8 (1 bit) | 0,19 GB | Notable sin re-ordenar |

### int8 (escalar)

Cada dimensión se lleva a un entero entre −128 y 127. Se mira una muestra de vectores para saber el rango de valores y se lo reparte en 256 escalones. En el ejemplo, el valor más extremo es −0,201, así que cada escalón vale 0,201 / 128 ≈ 0,0016.

```
valores float:  -0,083   0,012   0,154   -0,201
                   │       │       │        │
                   ▼       ▼       ▼        ▼
valores int8:    -53       8      98     -128
```

4 veces menos memoria, y el ranking casi no cambia.

### Binario

Cada dimensión se reduce a **un bit**: 1 si es positiva, 0 si no. La comparación pasa a ser **distancia de Hamming** (cuántos bits difieren), que las CPUs calculan rapidísimo.

```
float:    [ 0,12  -0,48   0,33  -0,02   0,07  -0,19   0,41   0,05 ]
binario:  [  1     0      1      0      1      0      1      1   ]   = 1 byte
```

32 veces menos memoria, pero se pierde bastante precisión. El truco para recuperarla es el **rescoring**:

```
1. buscar con vectores binarios          ->  top 100 candidatos (rápido, barato)
2. re-ordenar esos 100 con float32/int8  ->  top 10 final       (preciso)
```

Los vectores completos se pueden guardar en disco y leer solo para esos pocos candidatos.

## Combinarlos

Matryoshka y cuantización se suman: 512 dimensiones en int8 ocupan **12 veces menos** que 1536 en float32. Lo que hay que hacer es **medir el recall** en cada combinación con tus consultas reales, porque cuánto se pierde depende del modelo y de los datos.

## ¿Y más dimensiones es mejor?

No necesariamente. Pasar de 384 a 1024 suele mejorar; de 1024 a 3072 la ganancia es más chica y el costo es el triple. Un modelo mejor entrenado con menos dimensiones le gana a menudo a uno peor con más. La dimensión es una perilla de costo, no de calidad garantizada.

## ✅ / ❌

- ✅ int8 da 4× menos memoria casi sin pérdida: suele convenir siempre.
- ✅ Binario + rescoring da 32× menos memoria con resultados cercanos al original.
- ✅ Matryoshka permite elegir el tamaño sin cambiar de modelo.
- ❌ Cortar dimensiones de un modelo que no es Matryoshka arruina los vectores.
- ❌ Hay que volver a normalizar después de recortar.
- ❌ La pérdida depende de los datos: sin medir, no sabés cuánto estás resignando.
