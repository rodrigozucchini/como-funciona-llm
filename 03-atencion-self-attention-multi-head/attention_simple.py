import math

# Frase: "el gato duerme" — miramos qué atiende "duerme"
tokens = ["el", "gato", "duerme"]

q_duerme = [1.0, 0.5, 0.0, 1.0]          # lo que "duerme" busca
keys = {
    "el":     [0.5, 0.0, 0.5, 0.5],
    "gato":   [1.5, 1.0, 0.0, 1.0],
    "duerme": [1.0, 0.0, 1.0, 1.0],
}
values = {
    "el":     [1, 0],
    "gato":   [0, 1],
    "duerme": [1, 1],
}

def dot(a, b):
    return sum(x * y for x, y in zip(a, b))

def softmax(xs):
    exps = [math.exp(x) for x in xs]
    total = sum(exps)
    return [e / total for e in exps]

d_k = len(q_duerme)

# 1. Scores: producto punto query · key, escalado por √d_k
scores = [dot(q_duerme, keys[t]) / math.sqrt(d_k) for t in tokens]

# 2. Softmax → pesos de atención
pesos = softmax(scores)

# 3. Promedio ponderado de los values
salida = [sum(p * values[t][i] for p, t in zip(pesos, tokens)) for i in range(2)]

for t, s, p in zip(tokens, scores, pesos):
    print(f"{t:>7} | score {s:.2f} | peso {p:.3f}")
print("salida de 'duerme':", [round(x, 3) for x in salida])
