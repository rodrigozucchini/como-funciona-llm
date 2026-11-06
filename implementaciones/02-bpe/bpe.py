"""
BPE (Byte Pair Encoding) desde cero.

Entrena un tokenizer sobre un corpus chico, muestra cada merge paso a paso
y después lo usa para tokenizar (encode) y reconstruir (decode) texto.

Uso:
    python3 bpe.py
"""

import re
from collections import Counter

# Un corpus chico con palabras que comparten raíces y terminaciones
# (gat-o, gat-os, gat-ito / com-e, com-en, com-emos). Así se ve cómo BPE
# descubre solo los pedazos que se repiten.
CORPUS = """
el gato come pescado. los gatos comen pescado todos los días.
el perro come carne. los perros comen carne y también comen pescado.
nosotros comemos con los gatos y con los perros.
el gatito corre. los gatitos corren detrás del perrito.
el perrito corre rápido. los perritos corren más rápido que los gatitos.
nosotros corremos con el perro y el gato. todos corremos y comemos.
el gato duerme. los gatos duermen. el perro duerme. los perros duermen.
nosotros dormimos poco porque los gatos comen temprano.
"""

# Marca de "acá empieza una palabra" (había un espacio antes).
# SentencePiece usa este mismo símbolo; GPT-2 usa "Ġ". Es la misma idea.
ESPACIO = "▁"
UNK = "<unk>"


# ---------------------------------------------------------------------------
# 1. Pre-tokenización: partir el texto en "palabras" antes de aplicar BPE.
#    Los merges nunca cruzan de una palabra a otra.
# ---------------------------------------------------------------------------

def pre_tokenizar(texto):
    # Cada pedazo es: (espacio opcional + letras) | (espacio opcional + signos) | espacios sueltos
    pedazos = re.findall(r" ?\w+| ?[^\w\s]+|\s+", texto)
    # El espacio del principio pasa a ser parte de la palabra, como "▁gato".
    return [p.replace(" ", ESPACIO) for p in pedazos]


# ---------------------------------------------------------------------------
# 2. Entrenamiento
# ---------------------------------------------------------------------------

def contar_pares(palabras_partidas, frecuencias):
    """Cuenta cuántas veces aparece cada par de tokens vecinos en todo el corpus."""
    pares = Counter()
    for palabra, tokens in palabras_partidas.items():
        for i in range(len(tokens) - 1):
            pares[(tokens[i], tokens[i + 1])] += frecuencias[palabra]
    return pares


def fusionar(tokens, par):
    """Reemplaza cada aparición de `par` en la lista por un único token."""
    resultado = []
    i = 0
    while i < len(tokens):
        if i < len(tokens) - 1 and (tokens[i], tokens[i + 1]) == par:
            resultado.append(tokens[i] + tokens[i + 1])
            i += 2
        else:
            resultado.append(tokens[i])
            i += 1
    return resultado


def entrenar(corpus, num_merges, mostrar_pasos=0):
    frecuencias = Counter(pre_tokenizar(corpus))

    # Al principio cada palabra está partida en caracteres.
    palabras_partidas = {palabra: list(palabra) for palabra in frecuencias}

    # Vocabulario inicial: token especial + todos los caracteres que aparecen.
    caracteres = sorted({c for palabra in frecuencias for c in palabra})
    vocab = [UNK] + caracteres
    merges = []

    for paso in range(1, num_merges + 1):
        pares = contar_pares(palabras_partidas, frecuencias)
        if not pares:
            break  # todas las palabras ya son un solo token

        mejor_par, veces = pares.most_common(1)[0]
        nuevo_token = mejor_par[0] + mejor_par[1]

        for palabra in palabras_partidas:
            palabras_partidas[palabra] = fusionar(palabras_partidas[palabra], mejor_par)

        merges.append(mejor_par)
        vocab.append(nuevo_token)

        if paso <= mostrar_pasos:
            print(f"  paso {paso:>2}: {mejor_par[0]!r:>8} + {mejor_par[1]!r:<8}"
                  f" aparece {veces:>2} veces  ->  {nuevo_token!r}")

    return vocab, merges


# ---------------------------------------------------------------------------
# 3. Encode y decode
# ---------------------------------------------------------------------------

class Tokenizer:
    def __init__(self, vocab, merges):
        self.vocab = vocab
        self.token_a_id = {token: i for i, token in enumerate(vocab)}
        # El orden importa: los merges se aplican en el mismo orden en que se aprendieron.
        self.prioridad = {par: i for i, par in enumerate(merges)}

    def tokenizar_palabra(self, palabra):
        tokens = [c if c in self.token_a_id else UNK for c in palabra]
        while True:
            # De todos los pares vecinos, buscamos el que se aprendió primero.
            candidatos = [
                (self.prioridad[par], par)
                for par in zip(tokens, tokens[1:])
                if par in self.prioridad
            ]
            if not candidatos:
                return tokens
            _, par = min(candidatos)
            tokens = fusionar(tokens, par)

    def tokenizar(self, texto):
        tokens = []
        for palabra in pre_tokenizar(texto):
            tokens.extend(self.tokenizar_palabra(palabra))
        return tokens

    def encode(self, texto):
        return [self.token_a_id[t] for t in self.tokenizar(texto)]

    def decode(self, ids):
        texto = "".join(self.vocab[i] for i in ids)
        return texto.replace(ESPACIO, " ")


# ---------------------------------------------------------------------------
# Demo
# ---------------------------------------------------------------------------

def mostrar(tokens):
    return " | ".join(tokens)


def main():
    print("=" * 70)
    print("1. ENTRENAMIENTO: cada paso fusiona el par más frecuente")
    print("=" * 70)
    vocab, merges = entrenar(CORPUS, num_merges=80, mostrar_pasos=20)
    print(f"  ... (80 merges en total)")
    print(f"\n  Vocabulario final: {len(vocab)} tokens "
          f"(1 especial + {len(vocab) - 1 - len(merges)} caracteres + {len(merges)} merges)")

    tok = Tokenizer(vocab, merges)

    print("\n" + "=" * 70)
    print("2. TOKENIZAR: palabras vistas y no vistas")
    print("=" * 70)
    for palabra in [" gatos", " comemos", " perritos", " gatitas", " comiendo", " dormimos"]:
        tokens = tok.tokenizar_palabra(palabra.replace(" ", ESPACIO))
        unidad = "token" if len(tokens) == 1 else "tokens"
        print(f"  {palabra!r:<13} -> {mostrar(tokens)}   ({len(tokens)} {unidad})")
    print("\n  Las palabras frecuentes quedan en 1 token. Las nuevas ('gatitas',")
    print("  'comiendo') se arman con pedazos conocidos: nunca hace falta <unk>")
    print("  mientras los caracteres estén en el vocabulario.")

    print("\n" + "=" * 70)
    print("3. ENCODE / DECODE: texto -> tokens -> IDs -> texto")
    print("=" * 70)
    frase = "los gatitos comen pescado con el perro."
    tokens = tok.tokenizar(frase)
    ids = tok.encode(frase)
    print(f"  texto:   {frase!r}")
    print(f"  tokens:  {mostrar(tokens)}")
    print(f"  ids:     {ids}")
    print(f"  decode:  {tok.decode(ids)!r}")
    print(f"  ¿igual al original?  {tok.decode(ids) == frase}")
    print("\n  Ojo con el primer 'los': no tiene espacio antes, así que no es '▁los'")
    print("  y se parte en 'l | os'. La misma palabra da tokens distintos según")
    print("  dónde esté (ver errores/02-espacios-y-mayusculas).")

    print("\n" + "=" * 70)
    print("4. CARACTERES QUE NUNCA VIO -> <unk>")
    print("=" * 70)
    frase = "el gato come 🐟 y paga 5€"
    tokens = tok.tokenizar(frase)
    print(f"  texto:   {frase!r}")
    print(f"  tokens:  {mostrar(tokens)}")
    print(f"  decode:  {tok.decode(tok.encode(frase))!r}")
    print("\n  Se perdió información: el emoji, el 5 y el € no están en el vocabulario.")
    print("  Byte-level BPE (03) resuelve esto empezando desde los 256 bytes.")

    print("\n" + "=" * 70)
    print("5. TAMAÑO DEL VOCABULARIO: más merges = menos tokens por texto")
    print("=" * 70)
    frase = "nosotros corremos con los perritos y comemos con los gatitos."
    print(f"  texto: {frase!r}  ({len(frase)} caracteres)\n")
    print(f"  {'merges':>7} {'vocab':>6} {'tokens':>7} {'caract/token':>13}")
    for n in [0, 10, 30, 80, 200]:
        v, m = entrenar(CORPUS, num_merges=n)
        cantidad = len(Tokenizer(v, m).tokenizar(frase))
        print(f"  {len(m):>7} {len(v):>6} {cantidad:>7} {len(frase) / cantidad:>13.1f}")
    print("\n  Con 0 merges es tokenización por caracteres. A partir de cierto punto")
    print("  no hay más pares para fusionar: el corpus es chico. Los modelos reales")
    print("  entrenan sobre terabytes y usan vocabularios de 50.000 a 200.000 tokens.")


if __name__ == "__main__":
    main()
