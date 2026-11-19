# Similitud coseno

La forma estándar de comparar dos embeddings: **el coseno del ángulo entre los dos vectores**. No importa cuán largos sean, solo hacia dónde apuntan.

## La intuición en 2 dimensiones

```
        ▲
        │        b
        │       ╱
        │      ╱       a y b: ángulo chico  -> coseno cerca de 1  (parecidos)
        │     ╱  ╱ a
        │    ╱ ╱
        │   ╱╱
        │  ╱╱
        │ ╱╱
        └──────────────────► c     a y c: ángulo de ~70° -> coseno ~0,3
```

| Ángulo | Coseno | Lectura |
|---|---|---|
| 0° | 1 | Misma dirección |
| 45° | 0,71 | Bastante parecidos |
| 90° | 0 | Perpendiculares: sin relación |
| 180° | −1 | Opuestos |

En un embedding hay cientos o miles de dimensiones en vez de 2, pero la idea es la misma: cada texto es una flecha y se mide el ángulo entre flechas.

## La fórmula, pieza por pieza

```
                    a · b
   coseno(a, b) = ─────────
                   |a| |b|
```

**1. Producto punto (`a · b`)**: multiplicar coordenada a coordenada y sumar. Es grande cuando los dos vectores tienen valores altos en las mismas dimensiones y con el mismo signo.

**2. Norma (`|a|`)**: el largo del vector. Raíz cuadrada de la suma de los cuadrados (Pitágoras en N dimensiones).

**3. Dividir por las normas**: saca el efecto del largo. Lo que queda es solo la dirección.

## Ejemplo a mano

```
a = (1, 2, 2)
b = (2, 1, 2)
c = (2, 4, 4)       ← es a × 2
d = (2, -1, 0)

normas:
|a| = √(1 + 4 + 4)  = 3
|b| = √(4 + 1 + 4)  = 3
|c| = √(4 + 16 + 16) = 6
|d| = √(4 + 1 + 0)  = 2,236

productos punto:
a · b = 2 + 2 + 4 = 8
a · c = 2 + 8 + 8 = 18
a · d = 2 − 2 + 0 = 0

cosenos:
coseno(a, b) = 8  / (3 × 3)     = 0,889   parecidos
coseno(a, c) = 18 / (3 × 6)     = 1       misma dirección (c es a "estirado")
coseno(a, d) = 0  / (3 × 2,236) = 0       perpendiculares
```

## Por qué ignorar el largo

`a` y `c` apuntan al mismo lado y difieren solo en el largo. En embeddings, el largo del vector no suele llevar significado útil: puede depender de cuántos tokens tenía el texto, de palabras frecuentes o de detalles del modelo. **La dirección es lo que codifica el significado.** El coseno se queda solo con eso.

## Normalizar primero

Si cada vector se divide por su norma, todos pasan a medir 1 (quedan sobre la "superficie de una esfera"). Entonces:

```
a normalizado = (1/3, 2/3, 2/3)
b normalizado = (2/3, 1/3, 2/3)

producto punto = 2/9 + 2/9 + 4/9 = 8/9 = 0,889   ← igual al coseno
```

**Con vectores normalizados, coseno = producto punto.** Esto es muy útil en la práctica: se normaliza una vez al guardar, y después cada comparación es solo multiplicar y sumar, sin raíces ni divisiones. Muchas APIs de embeddings ya devuelven los vectores normalizados; otras no (ver [`errores/02-no-normalizar`](../../errores/02-no-normalizar)).

## Similitud y distancia

Algunas bases vectoriales hablan de **distancia coseno** en vez de similitud:

```
distancia coseno = 1 − similitud coseno
```

Va de 0 (idénticos) a 2 (opuestos). Mismo ranking, al revés: en una se ordena de mayor a menor, en la otra de menor a mayor. Conviene fijarse cuál devuelve cada herramienta antes de poner un umbral.

## Qué valores esperar en la práctica

En teoría el coseno va de −1 a 1. Con embeddings de texto reales:

- **Casi nunca da negativo**: los textos comparten mucha estructura (son todos "lenguaje"), así que los vectores tienden a apuntar a una misma zona.
- **Cada modelo tiene su rango**: en algunos, dos textos sin relación dan 0,1; en otros dan 0,7. Esto se llama **anisotropía**: los vectores ocupan un "cono" angosto en vez de toda la esfera.
- **Lo que importa es el orden**: el 0,82 de un modelo no es comparable con el 0,82 de otro. Dentro del mismo modelo, que A dé más que B sí significa algo.

Más sobre esto en [`errores/03-umbral-fijo`](../../errores/03-umbral-fijo).

## ✅ / ❌

- ✅ Ignora el largo del vector: compara solo el significado.
- ✅ Acotada entre −1 y 1: fácil de leer y de comparar dentro de un mismo modelo.
- ✅ Con vectores normalizados es un producto punto: barata de calcular, millones de veces por segundo.
- ✅ Es la métrica con la que se entrenan casi todos los modelos de embeddings.
- ❌ El número absoluto no se traslada entre modelos.
- ❌ Mide "qué tan cerca", no "qué tan relevante": dos textos sobre el mismo tema con conclusiones opuestas dan alto.
- ❌ En muchas dimensiones, los valores tienden a concentrarse en un rango angosto y las diferencias son chicas.
