"""
Byte-level BPE: el mismo algoritmo que 02-bpe, pero arrancando desde los
256 bytes posibles en vez de los caracteres del corpus.

Así cualquier texto se puede tokenizar (emojis, chino, lo que sea): en el
peor caso, byte por byte. Nunca hay <unk>.

Uso:
    python3 byte_level_bpe.py
"""

import re
from collections import Counter

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


def pre_tokenizar(texto):
    # Igual que en 02-bpe: el espacio queda pegado al principio de la palabra.
    return re.findall(r" ?\w+| ?[^\w\s]+|\s+", texto)


def fusionar(tokens, par, nuevo):
    resultado = []
    i = 0
    while i < len(tokens):
        if i < len(tokens) - 1 and (tokens[i], tokens[i + 1]) == par:
            resultado.append(nuevo)
            i += 2
        else:
            resultado.append(tokens[i])
            i += 1
    return resultado


class ByteLevelBPE:
    """
    Los tokens son IDs (números). Cada ID representa una secuencia de bytes:
      - los IDs 0 a 255 son los bytes sueltos;
      - del 256 en adelante, uno por cada merge aprendido.
    """

    def __init__(self):
        self.vocab = {i: bytes([i]) for i in range(256)}   # id -> bytes
        self.merges = {}                                     # (id, id) -> id nuevo

    def entrenar(self, corpus, num_merges, mostrar_pasos=0):
        frecuencias = Counter(pre_tokenizar(corpus))
        # Cada palabra arranca como la lista de sus bytes en UTF-8.
        partidas = {p: list(p.encode("utf-8")) for p in frecuencias}

        for paso in range(1, num_merges + 1):
            pares = Counter()
            for palabra, ids in partidas.items():
                for par in zip(ids, ids[1:]):
                    pares[par] += frecuencias[palabra]
            if not pares:
                break

            par, veces = pares.most_common(1)[0]
            nuevo = 256 + len(self.merges)
            self.merges[par] = nuevo
            self.vocab[nuevo] = self.vocab[par[0]] + self.vocab[par[1]]
            for palabra in partidas:
                partidas[palabra] = fusionar(partidas[palabra], par, nuevo)

            if paso <= mostrar_pasos:
                print(f"  paso {paso:>2}: {mostrar_token(self.vocab[par[0]]):>10} + "
                      f"{mostrar_token(self.vocab[par[1]]):<10} aparece {veces:>2} veces"
                      f"  ->  {mostrar_token(self.vocab[nuevo])}")
        return self

    def encode(self, texto):
        ids = []
        for palabra in pre_tokenizar(texto):
            tokens = list(palabra.encode("utf-8"))
            while True:
                # Aplicar primero el merge que se aprendió antes (el ID más bajo).
                candidatos = [p for p in zip(tokens, tokens[1:]) if p in self.merges]
                if not candidatos:
                    break
                par = min(candidatos, key=lambda p: self.merges[p])
                tokens = fusionar(tokens, par, self.merges[par])
            ids.extend(tokens)
        return ids

    def tokenizar(self, texto):
        """Igual que encode, pero devuelve los bytes de cada token (para mostrarlos)."""
        return [self.vocab[i] for i in self.encode(texto)]

    def decode(self, ids):
        # Primero se juntan TODOS los bytes y recién después se decodifica UTF-8.
        datos = b"".join(self.vocab[i] for i in ids)
        return datos.decode("utf-8", errors="replace")


def mostrar_token(b):
    """Muestra un token: como texto si es UTF-8 válido, como <hex> si es un pedazo de carácter."""
    try:
        return repr(b.decode("utf-8").replace(" ", "▁"))
    except UnicodeDecodeError:
        return "<" + " ".join(f"{x:02x}" for x in b) + ">"


def mostrar(tokens):
    return " | ".join(mostrar_token(t) for t in tokens)


def tokenizer_entrenado(num_merges=150):
    """Atajo para que otros ejemplos (05-tokens-especiales) reusen este tokenizer."""
    return ByteLevelBPE().entrenar(CORPUS, num_merges)


# ---------------------------------------------------------------------------
# Demo
# ---------------------------------------------------------------------------

def main():
    print("=" * 70)
    print("1. UTF-8: un carácter puede ocupar de 1 a 4 bytes")
    print("=" * 70)
    for c in ["a", "ñ", "€", "日", "🐟"]:
        b = c.encode("utf-8")
        print(f"  {c!r:>5} -> {len(b)} byte(s): {' '.join(f'{x:02x}' for x in b)}")
    print("\n  El vocabulario inicial son los 256 valores posibles de un byte.")
    print("  Con eso alcanza para representar cualquier texto.")

    print("\n" + "=" * 70)
    print("2. ENTRENAMIENTO: fusiona bytes en vez de caracteres")
    print("=" * 70)
    tok = ByteLevelBPE().entrenar(CORPUS, num_merges=150, mostrar_pasos=12)
    print(f"  ... ({len(tok.merges)} merges en total: pedimos 150, pero el corpus no da para más)")
    print(f"\n  Vocabulario: {len(tok.vocab)} tokens = 256 bytes + {len(tok.merges)} merges")
    acentos = [mostrar_token(tok.vocab[i]) for i in tok.vocab
               if i >= 256 and len(tok.vocab[i]) == 2 and tok.vocab[i][0] == 0xc3]
    print(f"  Merges que reconstruyen letras acentuadas (2 bytes -> 1 token): {', '.join(acentos)}")

    print("\n" + "=" * 70)
    print("3. NUNCA HAY <unk>")
    print("=" * 70)
    frase = "el gato come 🐟 y paga 5€"
    ids = tok.encode(frase)
    print(f"  texto:   {frase!r}")
    print(f"  tokens:  {mostrar(tok.tokenizar(frase))}")
    print(f"  decode:  {tok.decode(ids)!r}")
    print(f"  ¿igual al original?  {tok.decode(ids) == frase}")
    print("\n  Comparalo con 02-bpe, donde el emoji y el € se perdían como <unk>.")
    print("  Acá el 🐟 son 4 tokens (sus 4 bytes) y el € son 3: más caro, pero no se pierde.")

    print("\n" + "=" * 70)
    print("4. EL MISMO SIGNIFICADO, DISTINTO PRECIO")
    print("=" * 70)
    frases = {
        "español (como el corpus)": "los gatos comen pescado",
        "inglés":                   "the cats eat fish",
        "japonés":                  "猫は魚を食べる",
        "emojis":                   "🐱🐱🍽️🐟",
    }
    print(f"  {'idioma':<26} {'caract':>6} {'tokens':>6} {'tokens/caract':>14}")
    for idioma, frase in frases.items():
        n = len(tok.encode(frase))
        print(f"  {idioma:<26} {len(frase):>6} {n:>6} {n / len(frase):>14.2f}")
    print("\n  El tokenizer aprendió merges solo para lo que vio. Lo demás cae a bytes.")
    print("  Con un tokenizer real pasa lo mismo, en menor escala: si el corpus de")
    print("  entrenamiento tenía poco japonés, el japonés cuesta más tokens.")

    print("\n" + "=" * 70)
    print("5. UN TOKEN PUEDE SER MEDIO CARÁCTER (cuidado al hacer streaming)")
    print("=" * 70)
    frase = "un 🐟 rápido"
    ids = tok.encode(frase)
    print(f"  texto: {frase!r}\n")
    print("  Decodificando token por token (como si llegaran de a uno):")
    for i in ids:
        print(f"    token {i:>3} = {mostrar_token(tok.vocab[i]):<16} -> {tok.decode([i])!r}")
    print(f"\n  Todo junto: {tok.decode(ids)!r}")
    print("\n  Los bytes del emoji sueltos no son UTF-8 válido y salen como '�'.")
    print("  Al recibir tokens de a uno hay que acumular los bytes hasta tener")
    print("  caracteres completos (las SDKs de los proveedores ya lo hacen).")


if __name__ == "__main__":
    main()
