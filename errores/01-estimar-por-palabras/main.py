import sys
from pathlib import Path

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "implementaciones" / "03-byte-level-bpe"))
from byte_level_bpe import tokenizer_entrenado  # noqa: E402

tok = tokenizer_entrenado()   # entrenado con prosa en español sobre gatos y perros

TEXTOS = {
    "prosa (como el corpus)": "los gatos comen pescado y los perros comen carne.",
    "prosa (otro tema)":      "el servidor responde con un error de autenticación.",
    "código":                 "def f(x): return x * 2 if x > 0 else -x",
    "JSON":                   '{"id": 4821, "activo": true, "tags": ["a", "b"]}',
    "números":                "3.14159 2718281 1618033 1414213",
    "URL":                    "https://ejemplo.com/api/v2/users?id=8812&ref=xyz",
    "japonés":                "猫は魚を食べます",
}

print(f"{'texto':<24} {'palabras':>8} {'caract/4':>9} {'tokens reales':>14} {'error':>7}")
for nombre, texto in TEXTOS.items():
    palabras = len(texto.split())
    por_caracteres = round(len(texto) / 4)
    reales = len(tok.encode(texto))
    error = (reales - palabras) / reales
    print(f"{nombre:<24} {palabras:>8} {por_caracteres:>9} {reales:>14} {error:>7.0%}")

print("""
❌ "1 palabra ≈ 1 token" o "4 caracteres ≈ 1 token": la columna 'error' es cuánto
   te quedás corto estimando por palabras. Solo se acerca en el texto parecido
   al que vio el tokenizer al entrenar.

(Este tokenizer es de juguete y exagera las diferencias. Con uno real la brecha
 es menor, pero tiene la misma dirección: el código, el JSON, los números y los
 idiomas con poca presencia en el entrenamiento cuestan más tokens por palabra.)

✅ Contar con el tokenizer del modelo que vas a usar: count_tokens antes de
   mandar, usage después.""")
