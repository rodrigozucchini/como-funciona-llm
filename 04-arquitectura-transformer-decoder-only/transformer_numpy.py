"""Forward pass de un Transformer decoder-only mínimo (pesos aleatorios).

Muestra el camino completo: tokens -> embeddings -> N bloques -> logits -> próximo token.
Requiere: pip install numpy
"""
import numpy as np

rng = np.random.default_rng(0)

# Hiperparámetros (GPT-2 small usa 50257, 768, 12, 12, 1024)
vocab, d_model, n_heads, n_layers, max_len = 10, 16, 4, 2, 8
d_head = d_model // n_heads
vocab_words = ["<bos>", "el", "gato", "perro", "duerme", "come", "en", "la", "casa", "."]


def layer_norm(x, eps=1e-5):
    mu = x.mean(-1, keepdims=True)
    var = x.var(-1, keepdims=True)
    return (x - mu) / np.sqrt(var + eps)


def softmax(x):
    x = x - x.max(-1, keepdims=True)
    e = np.exp(x)
    return e / e.sum(-1, keepdims=True)


def gelu(x):
    return 0.5 * x * (1 + np.tanh(np.sqrt(2 / np.pi) * (x + 0.044715 * x**3)))


def W(*shape):
    return rng.normal(0, 0.1, shape)


# Pesos
tok_emb = W(vocab, d_model)          # tabla de embeddings (también se usa al final: weight tying)
pos_emb = W(max_len, d_model)        # posiciones aprendidas (como GPT-2)
blocks = [
    {
        "Wqkv": W(d_model, 3 * d_model), "Wo": W(d_model, d_model),
        "W1": W(d_model, 4 * d_model), "W2": W(4 * d_model, d_model),
    }
    for _ in range(n_layers)
]


def causal_self_attention(x, b):
    T = x.shape[0]
    q, k, v = np.split(x @ b["Wqkv"], 3, axis=-1)                 # (T, d_model) cada uno
    # separar en cabezas: (n_heads, T, d_head)
    q, k, v = (m.reshape(T, n_heads, d_head).transpose(1, 0, 2) for m in (q, k, v))
    scores = q @ k.transpose(0, 2, 1) / np.sqrt(d_head)           # (n_heads, T, T)
    mask = np.triu(np.ones((T, T), dtype=bool), k=1)               # True = futuro
    scores[:, mask] = -np.inf                                      # no mirar adelante
    out = softmax(scores) @ v                                      # (n_heads, T, d_head)
    out = out.transpose(1, 0, 2).reshape(T, d_model)               # juntar cabezas
    return out @ b["Wo"]


def mlp(x, b):
    return gelu(x @ b["W1"]) @ b["W2"]


def forward(ids):
    x = tok_emb[ids] + pos_emb[: len(ids)]                         # (T, d_model)
    for b in blocks:
        x = x + causal_self_attention(layer_norm(x), b)            # residual 1
        x = x + mlp(layer_norm(x), b)                              # residual 2
    x = layer_norm(x)
    return x @ tok_emb.T                                           # logits (T, vocab)


ids = [0, 1, 2]  # "<bos> el gato"
logits = forward(ids)
probs = softmax(logits[-1])  # sólo importa la última posición para predecir

print("entrada:", " ".join(vocab_words[i] for i in ids))
print("shape logits:", logits.shape, "(una distribución por posición)")
print("\nprobabilidades del próximo token (pesos aleatorios, sin entrenar):")
for i in np.argsort(-probs)[:5]:
    print(f"  {vocab_words[i]:>7}  {probs[i]:.3f}")

# Chequeo de causalidad: cambiar el futuro no cambia el pasado
logits2 = forward([0, 1, 3])  # "<bos> el perro"
print("\n¿cambiar el token 3 alteró las posiciones 1-2?",
      not np.allclose(logits[:2], logits2[:2]))

n_params = tok_emb.size + pos_emb.size + sum(sum(w.size for w in b.values()) for b in blocks)
print("parámetros:", n_params)
