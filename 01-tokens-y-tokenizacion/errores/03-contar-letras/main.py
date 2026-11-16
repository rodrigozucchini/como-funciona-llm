import sys
from pathlib import Path

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "implementaciones" / "03-byte-level-bpe"))
from byte_level_bpe import ByteLevelBPE, tokenizer_entrenado, mostrar  # noqa: E402

tok = tokenizer_entrenado()

print("1. LETRAS: lo que vos ves vs. lo que ve el modelo\n")
for palabra in [" perritos", " corremos"]:
    ids = tok.encode(palabra)
    print(f"  vos:     {palabra.strip()!r}  ->  {palabra.count('r')} letras 'r'")
    print(f"  modelo:  {ids}   ({mostrar(tok.tokenizar(palabra))})\n")
print(f"""  El modelo recibe números. Para saber cuántas 'r' tiene el token {tok.encode(" perritos")[0]} tiene
  que haberlo aprendido de memoria a partir de los datos: no lo puede "mirar".
  Por eso falla al contar letras, deletrear al revés o encontrar rimas.
""")

# Un tokenizer entrenado con texto que tiene años y precios, como pasa en la web.
corpus_numeros = " ".join(
    [f"en {a} costaba {p} pesos." for a in range(1990, 2026) for p in (100, 250, 500, 1000)]
)
tok_num = ByteLevelBPE().entrenar(corpus_numeros, num_merges=60)

print("2. NÚMEROS: se parten según lo que era frecuente, no por valor\n")
for numero in [" 2024", " 2042", " 1000", " 1001", " 12345", " 99999"]:
    print(f"  {numero.strip():>6} -> {mostrar(tok_num.tokenizar(numero))}")
print("""
  '2024' y '2042' tienen los mismos dígitos pero se parten distinto, y las
  unidades, decenas y centenas no quedan alineadas entre un número y otro.
  Sumar 2024 + 2042 "de cabeza" es sumar pedazos que no coinciden.

❌ Pedirle al modelo que cuente caracteres, invierta texto o haga cuentas
   largas confiando en que "lo ve".

✅ Darle una herramienta (ejecutar código) para esas tareas, o hacerlas en tu
   propio código antes o después de llamar al modelo:""")
print(f"""
     "perritos".count("r")  ->  {"perritos".count("r")}
     2024 + 2042            ->  {2024 + 2042}""")
