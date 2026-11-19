# word2vec: un vector por palabra

La idea viene de la lingüística: **una palabra se conoce por las palabras que la acompañan**. `perro` y `can` aparecen rodeadas de `ladra`, `correa`, `paseo`, `veterinario`. Si una red aprende a predecir esos vecinos, las palabras con vecinos parecidos terminan con vectores parecidos.

**Ejemplo real:** word2vec (Google, 2013), GloVe (Stanford, 2014) y FastText (Facebook, 2016). Vectores de 100 a 300 dimensiones.

## El truco: una tarea falsa

Nadie quiere el predictor: se lo entrena por una tarea que no importa, y lo que se guarda son los **pesos** que aprendió en el camino. Esos pesos son los embeddings.

```
oración:   "el  perro  ladra  en  el  patio"
ventana de 2 alrededor de "ladra":

                 el   perro  [ladra]  en   el
                  ▲     ▲               ▲    ▲
                  └─────┴──── contexto ─┴────┘
```

Hay dos variantes:

| | Skip-gram | CBOW |
|---|---|---|
| Entrada | La palabra del medio (`ladra`) | Las palabras de alrededor |
| Predice | Cada palabra de alrededor | La palabra del medio |
| Rinde mejor con | Palabras raras, corpus chicos | Corpus grandes, más rápido |

## Negative sampling

Predecir "cuál de las 100.000 palabras del vocabulario es la vecina" es carísimo. El atajo: convertirlo en una pregunta de sí o no.

```
¿("ladra", "perro") aparecen juntas?        -> sí   (par real del corpus)
¿("ladra", "hipoteca") aparecen juntas?     -> no   (par inventado al azar)
¿("ladra", "fotosíntesis") aparecen juntas? -> no
```

Por cada par real se sortean unos pocos pares falsos (**negativos**). El modelo aprende a acercar los vectores de los pares reales y alejar los de los falsos. Esta misma idea, a mucha mayor escala, es la que se usa hoy para entrenar modelos de embeddings (ver [`04-entrenamiento-contrastivo`](../04-entrenamiento-contrastivo)).

## Aritmética de significados

Como resultado, algunas relaciones quedan como **direcciones** en el espacio:

```
vector(rey) − vector(hombre) + vector(mujer)   ≈  vector(reina)
vector(París) − vector(Francia) + vector(Italia) ≈  vector(Roma)
vector(caminando) − vector(caminar) + vector(nadar) ≈ vector(nadando)
```

"Masculino → femenino" o "país → capital" son desplazamientos más o menos constantes. Es el ejemplo más famoso, y conviene tomarlo con pinzas: funciona en casos elegidos, falla en muchos otros, y hay que excluir las palabras de la consulta para que el resultado no sea `rey` mismo.

## FastText: pedazos de palabra

word2vec no tiene vector para una palabra que no vio. FastText arma el vector de cada palabra sumando los de sus **n-gramas de caracteres**:

```
"gatito"  ->  <ga, gat, ati, tit, ito, to>, <gatito>
```

Así, `gatitos` (que nunca vio) comparte casi todos sus pedazos con `gatito` y recibe un vector razonable. Es la misma intuición que los subwords del proyecto de tokens.

## El límite: un vector por palabra

```
"me senté en el banco de la plaza"
"pedí un préstamo en el banco"
                         │
                         ▼
            el mismo vector para los dos
```

Cada palabra tiene **un único vector**, que termina siendo un promedio de todos sus sentidos. Y no hay vector para una oración: la solución de la época era promediar los vectores de sus palabras, que pierde el orden y la negación (`bueno` y `no bueno` quedan casi iguales). Esto lo resuelven los [embeddings contextuales](../03-embeddings-contextuales).

## ✅ / ❌

- ✅ Vectores densos y chicos donde los sinónimos quedan cerca.
- ✅ Se entrena sin etiquetas: alcanza con texto crudo.
- ✅ Capturan relaciones (género, plural, país–capital) como direcciones.
- ❌ Un vector por palabra: no distingue sentidos (`banco`, `vela`, `planta`).
- ❌ No representa oraciones; promediar palabras pierde orden y negación.
- ❌ Heredan los sesgos del corpus: las mismas "direcciones" que dan `reina` también codifican estereotipos.
- ❌ Sin FastText, una palabra nueva no tiene vector.
