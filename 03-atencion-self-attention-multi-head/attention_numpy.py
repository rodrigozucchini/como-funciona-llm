d = {"gato": "felino", "perro": "canino"}
d["gato"]  # → "felino"   (match exacto, devuelve UN valor)
import numpy as np


def softmax(x, axis=-1):
    x = x - x.max(axis=axis, keepdims=True)  # estabilidad numérica
    e = np.exp(x)
    return e / e.sum(axis=axis, keepdims=True)


def scaled_dot_product_attention(Q, K, V, causal=False):
    """
    Q: (..., n, d_k)   K: (..., n, d_k)   V: (..., n, d_v)
    """
    d_k = Q.shape[-1]
    scores = Q @ K.swapaxes(-1, -2) / np.sqrt(d_k)      # (..., n, n)

    if causal:
        n = scores.shape[-1]
        mask = np.triu(np.ones((n, n), dtype=bool), k=1)  # True arriba de la diagonal
        scores = np.where(mask, -np.inf, scores)

    weights = softmax(scores, axis=-1)                   # cada fila suma 1
    return weights @ V, weights


class MultiHeadAttention:
    def __init__(self, d_model, n_heads, seed=0):
        assert d_model % n_heads == 0
        rng = np.random.default_rng(seed)
        self.h = n_heads
        self.d_k = d_model // n_heads
        s = 1 / np.sqrt(d_model)
        self.W_Q = rng.normal(0, s, (d_model, d_model))
        self.W_K = rng.normal(0, s, (d_model, d_model))
        self.W_V = rng.normal(0, s, (d_model, d_model))
        self.W_O = rng.normal(0, s, (d_model, d_model))

    def _split_heads(self, x):
        # (n, d_model) → (h, n, d_k)
        n = x.shape[0]
        return x.reshape(n, self.h, self.d_k).transpose(1, 0, 2)

    def __call__(self, X, causal=True):
        Q = self._split_heads(X @ self.W_Q)
        K = self._split_heads(X @ self.W_K)
        V = self._split_heads(X @ self.W_V)

        out, weights = scaled_dot_product_attention(Q, K, V, causal)  # (h, n, d_k)

        # (h, n, d_k) → (n, h·d_k) = (n, d_model)
        n = X.shape[0]
        out = out.transpose(1, 0, 2).reshape(n, self.h * self.d_k)
        return out @ self.W_O, weights


if __name__ == "__main__":
    tokens = ["el", "gato", "duerme", "en", "el", "sillón"]
    n, d_model, n_heads = len(tokens), 16, 4

    X = np.random.default_rng(42).normal(size=(n, d_model))  # embeddings simulados
    mha = MultiHeadAttention(d_model, n_heads)
    out, weights = mha(X, causal=True)

    print("salida:", out.shape)        # (6, 16) → misma forma que la entrada
    print("pesos:", weights.shape)     # (4, 6, 6) → una matriz n×n por cabeza

    np.set_printoptions(precision=2, suppress=True)
    print("\nPesos de la cabeza 0 (fila = quien mira, columna = a quien mira):")
    print(weights[0])
