"""
Tokenizer Unigram (el algoritmo principal de SentencePiece) desde cero.

Al revés que BPE: arranca con un vocabulario ENORME (todos los substrings
frecuentes) y lo va PODANDO, sacando los tokens que menos aportan, hasta
llegar al tamaño buscado. Para tokenizar, elige la partición más probable
con el algoritmo de Viterbi.

Simplificación: para repartir los conteos entre todas las particiones
posibles, el SentencePiece real usa el algoritmo forward-backward. Acá las
palabras son cortas, así que directamente se enumeran todas las particiones.
El resultado es el mismo y se entiende mejor.

Uso:
    python3 unigram.py
"""

import math
import random
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

ESPACIO = "▁"
UNK = "<unk>"
LARGO_MAXIMO = 10   # largo máximo de un token candidato


# ---------------------------------------------------------------------------
# Normalización: SentencePiece no pre-tokeniza con reglas de cada idioma.
# Trata el texto como una secuencia de caracteres y el espacio pasa a ser "▁".
# ---------------------------------------------------------------------------

def normalizar(texto):
    return ESPACIO + " ".join(texto.split()).replace(" ", ESPACIO)


def palabras(texto):
    """Parte en los ▁ (cada pedazo arranca con ▁). Ningún token cruza un espacio."""
    normal = normalizar(texto)
    return [ESPACIO + p for p in normal.split(ESPACIO) if p]


# ---------------------------------------------------------------------------
# Viterbi: la partición de mayor probabilidad
# ---------------------------------------------------------------------------

def viterbi(palabra, logp):
    """
    mejor[i] = mejor puntaje para tokenizar palabra[:i].
    Para cada posición se prueban todos los tokens del vocabulario que terminan ahí.
    """
    n = len(palabra)
    mejor = [-math.inf] * (n + 1)
    desde = [0] * (n + 1)
    mejor[0] = 0.0
    castigo_unk = min(logp.values()) - 10   # un carácter desconocido es carísimo

    for fin in range(1, n + 1):
        for inicio in range(max(0, fin - LARGO_MAXIMO), fin):
            pieza = palabra[inicio:fin]
            if pieza in logp:
                puntaje = mejor[inicio] + logp[pieza]
            elif fin - inicio == 1:
                puntaje = mejor[inicio] + castigo_unk
            else:
                continue
            if puntaje > mejor[fin]:
                mejor[fin], desde[fin] = puntaje, inicio

    # Reconstruir el camino de atrás para adelante.
    piezas, fin = [], n
    while fin > 0:
        inicio = desde[fin]
        pieza = palabra[inicio:fin]
        piezas.append(pieza if pieza in logp else UNK)
        fin = inicio
    return mejor[n], piezas[::-1]


# ---------------------------------------------------------------------------
# Entrenamiento
# ---------------------------------------------------------------------------

def todas_las_particiones(palabra, logp):
    """Todas las formas de partir una palabra con tokens del vocabulario, con su log p."""
    if not palabra:
        return [(0.0, [])]
    resultado = []
    for fin in range(1, min(LARGO_MAXIMO, len(palabra)) + 1):
        pieza = palabra[:fin]
        if pieza in logp:
            for puntaje, resto in todas_las_particiones(palabra[fin:], logp):
                resultado.append((logp[pieza] + puntaje, [pieza] + resto))
    return resultado


def log_suma(valores):
    """log(sum(exp(v))) sin que se vaya a cero por números muy chicos."""
    m = max(valores)
    return m + math.log(sum(math.exp(v - m) for v in valores))


def log_probabilidad_palabra(palabra, logp):
    """P(palabra) = suma de las probabilidades de todas sus particiones."""
    return log_suma([s for s, _ in todas_las_particiones(palabra, logp)])


def a_log_probabilidades(conteos):
    total = sum(conteos.values())
    return {p: math.log(c / total) for p, c in conteos.items() if c > 0}


def reestimar(frecuencias, logp):
    """
    Un paso de EM:
      E) para cada palabra, cada partición posible pesa según su probabilidad,
         y cada token de esa partición suma ese peso a su conteo;
      M) las nuevas probabilidades son los conteos normalizados.
    """
    conteos = Counter()
    for palabra, f in frecuencias.items():
        particiones = todas_las_particiones(palabra, logp)
        z = log_suma([s for s, _ in particiones])
        for puntaje, piezas in particiones:
            peso = f * math.exp(puntaje - z)
            for pieza in piezas:
                conteos[pieza] += peso
    # Los caracteres sueltos tienen un piso: si no, uno raro (la 'q' de 'que')
    # puede quedar con conteo 0 y desaparecer, y ya no se podría partir todo.
    return a_log_probabilidades(
        {p: max(conteos[p], 1e-3) if len(p) == 1 else conteos[p] for p in logp})


def perdida_total(frecuencias, logp):
    """Log-likelihood negativa del corpus: cuanto más baja, mejor lo explica el vocabulario."""
    return -sum(f * log_probabilidad_palabra(p, logp) for p, f in frecuencias.items())


def entrenar(corpus, tamano_vocab, mostrar_progreso=False):
    frecuencias = Counter(palabras(corpus))
    caracteres = {c for p in frecuencias for c in p}

    # 1. Vocabulario inicial: todos los substrings que aparecen al menos 2 veces.
    candidatos = Counter()
    for palabra, f in frecuencias.items():
        for i in range(len(palabra)):
            for j in range(i + 1, min(i + LARGO_MAXIMO, len(palabra)) + 1):
                candidatos[palabra[i:j]] += f
    logp = a_log_probabilidades(
        {p: c for p, c in candidatos.items() if c >= 2 or p in caracteres})

    if mostrar_progreso:
        print(f"  Vocabulario inicial: {len(logp)} candidatos")
        print(f"  (todos los substrings con 2+ apariciones, ej: "
              f"{', '.join(repr(p) for p in ['▁gat', 'atos', 'rr', 'itos', '▁come'] if p in logp)})\n")
        print(f"  {'ronda':>5} {'vocab':>6} {'pérdida del corpus':>19}")

    ronda = 0
    while True:
        for _ in range(2):   # un par de pasos de EM por ronda
            logp = reestimar(frecuencias, logp)
        if mostrar_progreso:
            print(f"  {ronda:>5} {len(logp):>6} {perdida_total(frecuencias, logp):>19.1f}")
        if len(logp) <= tamano_vocab:
            break
        ronda += 1

        # 2. Para cada token: ¿cuánto empeora el corpus si lo sacamos?
        actual = {p: log_probabilidad_palabra(p, logp) for p in frecuencias}
        perdida_si_saco = {}
        for pieza in logp:
            if len(pieza) == 1:
                continue   # los caracteres sueltos no se podan nunca: garantizan poder partir todo
            sin_pieza = {p: lp for p, lp in logp.items() if p != pieza}
            perdida_si_saco[pieza] = sum(
                f * (actual[palabra] - log_probabilidad_palabra(palabra, sin_pieza))
                for palabra, f in frecuencias.items() if pieza in palabra
            )

        # 3. Podar el 25% que menos aporta (SentencePiece usa el mismo número).
        a_sacar = len(logp) - tamano_vocab
        cuantos = max(1, min(a_sacar, len(perdida_si_saco) // 4))
        for pieza in sorted(perdida_si_saco, key=perdida_si_saco.get)[:cuantos]:
            del logp[pieza]

    return logp


# ---------------------------------------------------------------------------
# Tokenizar / decode
# ---------------------------------------------------------------------------

def tokenizar(texto, logp):
    tokens = []
    for palabra in palabras(texto):
        tokens.extend(viterbi(palabra, logp)[1])
    return tokens


def decode(tokens):
    return "".join(tokens).replace(ESPACIO, " ").lstrip()


# ---------------------------------------------------------------------------
# Demo
# ---------------------------------------------------------------------------

def mostrar(tokens):
    return " | ".join(tokens)


def main():
    print("=" * 70)
    print("1. ENTRENAMIENTO: arrancar grande y podar")
    print("=" * 70)
    logp = entrenar(CORPUS, tamano_vocab=50, mostrar_progreso=True)
    print("\n  Cada ronda saca el 25% de los tokens que menos aportan. Al principio son")
    print("  substrings que no sirven ('atos' sin la 'g') y la pérdida casi no cambia.")
    print("  Al final saca tokens que sí se usaban y la pérdida sube: es el precio de")
    print("  un vocabulario más chico.")

    largos = sorted((p for p in logp if len(p) > 1), key=logp.get, reverse=True)
    print(f"\n  Vocabulario final: {len(logp)} tokens. Los más probables (sin contar letras sueltas):")
    for p in largos[:12]:
        print(f"    {p!r:<12} p = {math.exp(logp[p]):.3f}")

    print("\n" + "=" * 70)
    print("2. VITERBI: la partición más probable")
    print("=" * 70)
    for palabra in ["gatos", "perritos", "gatitas", "comiendo", "corremos"]:
        puntaje, piezas = viterbi(ESPACIO + palabra, logp)
        print(f"  {palabra!r:<12} -> {mostrar(piezas):<28} log p = {puntaje:.1f}")

    print("\n" + "=" * 70)
    print("3. UNA PALABRA, MUCHAS PARTICIONES POSIBLES")
    print("=" * 70)
    palabra = ESPACIO + "comemos"
    particiones = sorted(todas_las_particiones(palabra, logp), reverse=True)
    total = sum(math.exp(s) for s, _ in particiones)
    print(f"  {palabra!r} se puede partir de {len(particiones)} formas:\n")
    for puntaje, piezas in particiones:
        print(f"    {math.exp(puntaje) / total:>6.1%}   {mostrar(piezas)}")
    print("\n  BPE siempre da una sola partición. Unigram sabe cuánto vale cada una.")

    print("\n  Subword regularization: al ENTRENAR un modelo, en vez de usar siempre")
    print("  la mejor partición se sortea una. SentencePiece usa un parámetro alpha")
    print("  que aplana las probabilidades (p^alpha) para que salgan más variadas.")
    print("  El modelo ve la misma palabra partida de varias formas y se vuelve más")
    print("  robusto a typos y variantes. 1.000 sorteos con alpha = 0.2:\n")
    random.seed(3)
    alpha = 0.2
    pesos = [math.exp(alpha * s) for s, _ in particiones]
    sorteos = Counter(
        mostrar(random.choices(particiones, weights=pesos)[0][1]) for _ in range(1000))
    for piezas, veces in sorteos.most_common():
        print(f"    {veces:>4} veces   {piezas}")
    print("\n  Para usar el modelo (no para entrenarlo) siempre se usa la mejor: Viterbi.")

    print("\n" + "=" * 70)
    print("4. TEXTO COMPLETO Y CARACTERES DESCONOCIDOS")
    print("=" * 70)
    frase = "los gatitos comen pescado."
    tokens = tokenizar(frase, logp)
    print(f"  texto:   {frase!r}")
    print(f"  tokens:  {mostrar(tokens)}")
    print(f"  decode:  {decode(tokens)!r}")
    print("\n  Sin pre-tokenización, el '.' es un carácter más: si 'pescado.' fuera muy")
    print("  frecuente podría quedar como un solo token, cosa que el BPE de 02 (que")
    print("  separa la puntuación antes) nunca haría.")

    frase = "el gato come 🐟"
    tokens = tokenizar(frase, logp)
    print(f"\n  texto:   {frase!r}")
    print(f"  tokens:  {mostrar(tokens)}")
    print("\n  Unigram también puede tener <unk>. SentencePiece lo resuelve con la")
    print("  opción byte_fallback: lo que no está en el vocabulario se parte en bytes,")
    print("  como en 03-byte-level-bpe.")


if __name__ == "__main__":
    main()
