# Predicción del siguiente token y sampling

> Viene de [04. Arquitectura](../04-arquitectura-transformer-decoder-only/README.md): el modelo devuelve una **probabilidad para cada token** del vocabulario. Este tema explica cómo se elige cuál sale.

---

## 1. Lo que devuelve el modelo

Un LLM no "escribe una respuesta": en cada paso devuelve **una lista de probabilidades** para el próximo token, una por cada token del vocabulario.

```
"El gato se subió al"  →  modelo  →   techo    50%
                                      árbol    30%
                                      sillón   15%
                                      auto      5%

(en realidad son miles de opciones; acá dejamos 4 para que se vea simple)
```

Se elige un token, se agrega al texto, y se vuelve a preguntar. Así, token por token, sale la respuesta completa.

La forma de elegir se llama **sampling** (muestreo). Cambiarla cambia el estilo de la respuesta sin tocar el modelo.

---

## 2. Elegir siempre el más probable (greedy)

La opción más simple: quedarse siempre con el primero de la lista.

- ✅ Predecible: la misma pregunta da la misma respuesta.
- ❌ Aburrido y repetitivo: tiende a frases genéricas y a veces entra en loops ("y el gato y el gato y el gato…").

Lo más probable en cada paso no siempre arma el mejor texto completo.

---

## 3. Sortear según las probabilidades

En vez de elegir siempre el primero, se **sortea**: `techo` sale 50 de cada 100 veces, `árbol` 30, y así. Es como una ruleta donde cada opción tiene una porción proporcional a su probabilidad.

Así las respuestas varían y suenan más naturales. El riesgo: de vez en cuando sale una opción muy improbable que no tiene sentido. Para controlar eso hay tres perillas.

---

## 4. Temperature: qué tan "arriesgado" es el sorteo

La **temperatura** estira o aplana las probabilidades antes de sortear:

```
                      temperatura baja (0,2)   normal (1)   alta (1,5)
techo                        93%                  50%          42%
árbol                         7%                  30%          30%
sillón                       ~0%                  15%          19%
auto                         ~0%                   5%           9%
```

- **Baja (cerca de 0):** casi siempre gana el más probable. Respuestas precisas y estables. Bueno para extraer datos, clasificar, código.
- **Alta:** las opciones se emparejan. Respuestas más variadas y creativas, y también más errores. Bueno para ideas o escritura libre.
- **0** equivale a greedy.

---

## 5. Top-k y top-p: recortar la lista antes de sortear

Para que nunca salga algo absurdo, se descartan las opciones del fondo:

- **Top-k:** quedarse solo con las **k** opciones más probables. Con k = 3, solo pueden salir `techo`, `árbol` o `sillón`.
- **Top-p** (*nucleus*): quedarse con las opciones más probables hasta sumar **p** de probabilidad. Con p = 0,8: `techo` (50) + `árbol` (30) = 80%, el resto afuera.

Top-p se adapta solo: cuando el modelo está seguro, quedan una o dos opciones; cuando duda, quedan muchas. Por eso es el más usado.

---

## 6. Cómo se nota en la práctica

- **La misma pregunta puede dar respuestas distintas.** No es un error: es el sorteo.
- **Temperatura 0 no garantiza respuestas idénticas.** Detalles del hardware pueden cambiar algún token, y un token distinto cambia todo lo que sigue.
- **Cuándo cortar:** el modelo para cuando genera su token de fin, cuando llega al máximo de tokens permitido o cuando aparece una secuencia de parada que vos definiste.
- **No hace falta tocar todo.** Los valores por defecto suelen andar bien. Si se ajusta algo, conviene mover una sola perilla (normalmente la temperatura).

---

## Resumen

- El modelo devuelve **probabilidades** para el próximo token; se elige uno, se agrega y se repite.
- **Greedy** elige siempre el más probable: estable pero repetitivo.
- **Temperature** controla cuánto riesgo toma el sorteo: baja = preciso, alta = creativo.
- **Top-k** y **top-p** recortan las opciones improbables antes de sortear.

**Siguiente:** el modelo solo puede mirar una cantidad limitada de tokens a la vez → [06. Ventana de contexto](../06-ventana-de-contexto-y-context-rot/README.md).
