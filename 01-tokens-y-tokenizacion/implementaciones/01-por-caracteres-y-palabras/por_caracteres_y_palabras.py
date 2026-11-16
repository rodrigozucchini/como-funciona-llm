"""
Los dos extremos de la tokenización: por caracteres y por palabras.

Muestra por qué ninguno de los dos sirve para un LLM:
- por caracteres, las secuencias quedan larguísimas;
- por palabras, el vocabulario no para de crecer y siempre aparecen palabras nuevas.

Uso:
    python3 por_caracteres_y_palabras.py
"""

import re

CORPUS = [
    "el gato come pescado. los gatos comen pescado todos los días.",
    "el perro come carne. los perros comen carne y también comen pescado.",
    "nosotros comemos con los gatos y con los perros.",
    "el gatito corre. los gatitos corren detrás del perrito.",
    "el perrito corre rápido. los perritos corren más rápido que los gatitos.",
    "nosotros corremos con el perro y el gato. todos corremos y comemos.",
    "el gato duerme. los gatos duermen. el perro duerme. los perros duermen.",
    "nosotros dormimos poco porque los gatos comen temprano.",
]

UNK = "<unk>"


# ---------------------------------------------------------------------------
# Tokenizer por caracteres
# ---------------------------------------------------------------------------

class TokenizerCaracteres:
    def __init__(self, textos):
        caracteres = sorted({c for texto in textos for c in texto})
        self.vocab = [UNK] + caracteres
        self.token_a_id = {t: i for i, t in enumerate(self.vocab)}

    def tokenizar(self, texto):
        return [c if c in self.token_a_id else UNK for c in texto]


# ---------------------------------------------------------------------------
# Tokenizer por palabras
# ---------------------------------------------------------------------------

def partir_en_palabras(texto):
    # Palabras y signos de puntuación por separado. Los espacios se descartan.
    return re.findall(r"\w+|[^\w\s]", texto)


class TokenizerPalabras:
    def __init__(self, textos):
        palabras = sorted({p for texto in textos for p in partir_en_palabras(texto)})
        self.vocab = [UNK] + palabras
        self.token_a_id = {t: i for i, t in enumerate(self.vocab)}

    def tokenizar(self, texto):
        return [p if p in self.token_a_id else UNK for p in partir_en_palabras(texto)]


# ---------------------------------------------------------------------------
# Demo
# ---------------------------------------------------------------------------

def mostrar(tokens):
    # El espacio se muestra como ␣ para que se vea que también es un token.
    return " | ".join("␣" if t == " " else t for t in tokens)


def main():
    por_caracteres = TokenizerCaracteres(CORPUS)
    por_palabras = TokenizerPalabras(CORPUS)

    print("=" * 70)
    print("1. LA MISMA FRASE CON LOS DOS TOKENIZERS")
    print("=" * 70)
    frase = "los gatitos comen pescado."
    c = por_caracteres.tokenizar(frase)
    p = por_palabras.tokenizar(frase)
    print(f"  texto: {frase!r}\n")
    print(f"  caracteres ({len(c)} tokens):  {mostrar(c)}")
    print(f"  palabras   ({len(p)} tokens):  {mostrar(p)}")
    print(f"\n  Vocabulario por caracteres: {len(por_caracteres.vocab)} tokens")
    print(f"  Vocabulario por palabras:   {len(por_palabras.vocab)} tokens")

    print("\n" + "=" * 70)
    print("2. PALABRAS QUE NO ESTABAN EN EL CORPUS")
    print("=" * 70)
    frase = "las gatitas comieron pescado."
    c = por_caracteres.tokenizar(frase)
    p = por_palabras.tokenizar(frase)
    print(f"  texto: {frase!r}\n")
    print(f"  caracteres: {mostrar(c)}")
    print(f"  palabras:   {mostrar(p)}")
    print("\n  Por palabras, 'las', 'gatitas' y 'comieron' no existen: se vuelven <unk>")
    print("  y el modelo no tiene forma de saber qué decían. Además 'gato', 'gatos' y")
    print("  'gatito' son tres IDs sin ninguna relación entre sí.")
    print("  Por caracteres no hay <unk>, pero cada letra es un paso del modelo.")

    print("\n" + "=" * 70)
    print("3. EL VOCABULARIO POR PALABRAS NO PARA DE CRECER")
    print("=" * 70)
    print(f"  {'oraciones':>10} {'vocab caracteres':>17} {'vocab palabras':>15}")
    for n in range(1, len(CORPUS) + 1):
        vc = len(TokenizerCaracteres(CORPUS[:n]).vocab)
        vp = len(TokenizerPalabras(CORPUS[:n]).vocab)
        print(f"  {n:>10} {vc:>17} {vp:>15}")
    print("\n  Los caracteres se estabilizan enseguida. Las palabras siguen creciendo con")
    print("  cada oración nueva. En un corpus real (nombres propios, typos, código,")
    print("  otros idiomas, conjugaciones) serían millones.")

    print("\n" + "=" * 70)
    print("4. EL COSTO DE CADA EXTREMO")
    print("=" * 70)
    texto = " ".join(CORPUS)
    c = len(por_caracteres.tokenizar(texto))
    p = len(por_palabras.tokenizar(texto))
    print(f"  Todo el corpus ({len(texto)} caracteres):")
    print(f"    caracteres: {c:>4} tokens")
    print(f"    palabras:   {p:>4} tokens   ({c / p:.1f}x menos)")
    print("\n  Un modelo con ventana de contexto de 1.000 tokens leería ~1.000 letras por")
    print("  caracteres, o ~1.000 palabras por palabras. Y la atención crece con el")
    print("  cuadrado del largo: el doble de tokens es ~4x de cómputo.")
    print("\n  Los subwords (02-bpe) son el punto medio: vocabulario fijo, sin <unk>")
    print("  para palabras nuevas y secuencias casi tan cortas como por palabras.")


if __name__ == "__main__":
    main()
