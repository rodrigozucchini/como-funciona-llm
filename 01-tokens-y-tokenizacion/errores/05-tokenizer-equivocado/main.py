import sys
from pathlib import Path

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "implementaciones" / "03-byte-level-bpe"))
from byte_level_bpe import CORPUS, ByteLevelBPE  # noqa: E402

CORPUS_INGLES = """
the cat eats fish. the cats eat fish every day.
the dog eats meat. the dogs eat meat and they also eat fish.
we eat with the cats and with the dogs.
the kitten runs. the kittens run behind the puppy.
the puppy runs fast. the puppies run faster than the kittens.
we run with the dog and the cat. we all run and we all eat.
"""

# Dos "modelos" con el mismo algoritmo y la misma cantidad de merges,
# entrenados sobre textos distintos.
modelo_a = ByteLevelBPE().entrenar(CORPUS, num_merges=100)          # el que usás para contar
modelo_b = ByteLevelBPE().entrenar(CORPUS_INGLES, num_merges=100)   # el que te cobra

textos = [
    "los gatos comen pescado.",
    "the cats eat fish.",
    "el perrito corre detrás del gato.",
    "the puppy runs behind the cat.",
]

print("Mismo algoritmo, mismo tamaño de vocabulario, distinto corpus de entrenamiento:\n")
print(f"  {'texto':<36} {'tokenizer A':>12} {'tokenizer B':>12} {'error':>7}")
for texto in textos:
    a, b = len(modelo_a.encode(texto)), len(modelo_b.encode(texto))
    print(f"  {texto!r:<36} {a:>12} {b:>12} {(a - b) / b:>+7.0%}")

print("""
❌ Contás con el tokenizer A (el que tenías a mano) pero usás el modelo B.
   La columna 'error' es cuánto le errás: según el texto, de más o de menos.
   (Con tokenizers reales, entrenados sobre muchísimo texto, la diferencia es
   menor que con estos de juguete, pero no es cero y cambia según el texto.)""")

texto = "the cat"
print(f"""
❌ Tampoco se pueden reusar los IDs entre modelos:
     {texto!r} en A -> {modelo_a.encode(texto)}
     {texto!r} en B -> {modelo_b.encode(texto)}
   Y el mismo ID significa cosas distintas en cada vocabulario:
     ID 257 en A = {modelo_a.vocab[257].decode("utf-8", "replace")!r}, en B = {modelo_b.vocab[257].decode("utf-8", "replace")!r}

Pasa también dentro del mismo proveedor: el tokenizer de Claude que llegó con
Opus 4.7 genera entre 1x y 1,35x los tokens del anterior para el mismo texto.
Un presupuesto calculado con el modelo viejo queda corto con el nuevo.

✅ Contar con el tokenizer del modelo exacto que vas a usar (count_tokens en la
   API de Claude, tiktoken solo para modelos de OpenAI), y volver a medir cada
   vez que cambiás de modelo.""")
