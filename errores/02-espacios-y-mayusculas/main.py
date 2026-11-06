import sys
from pathlib import Path

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "implementaciones" / "03-byte-level-bpe"))
from byte_level_bpe import tokenizer_entrenado, mostrar  # noqa: E402

tok = tokenizer_entrenado()

print("La 'misma' palabra, cuatro tokenizaciones distintas:\n")
for variante in ["gato", " gato", "Gato", " GATO"]:
    print(f"  {variante!r:<8} -> ids {str(tok.encode(variante)):<22} {mostrar(tok.tokenizar(variante))}")

print("""
  Para el modelo son IDs distintos. Que ' gato' y 'Gato' signifiquen lo mismo
  lo tiene que aprender de los datos; no viene dado por el tokenizer.
""")

print("❌ Un prompt que termina con espacio:\n")
for prompt in ["el gato come", "el gato come "]:
    print(f"  {prompt!r:<17} -> {mostrar(tok.tokenizar(prompt))}")
print("""
  Con el espacio al final, el último token es un '▁' suelto. En el texto de
  entrenamiento el espacio casi siempre va pegado a la palabra que sigue
  ('▁pescado'), así que el modelo arranca de una situación rara y la
  continuación puede salir peor.
""")

print("❌ Ejemplos few-shot con formato inconsistente:\n")
ejemplos = ["Animal: gato", "animal:perro", "ANIMAL : pez"]
for e in ejemplos:
    print(f"  {e!r:<16} -> {mostrar(tok.tokenizar(e))}")
print("""
  Tres formatos, tres secuencias de tokens distintas: el modelo no sabe cuál
  imitar. Y 'perro' pegado a los dos puntos, sin espacio antes, ya no es
  '▁perro' sino p | e | rr | o, pedazos que el modelo ve mucho menos.

✅ Formato idéntico en todos los ejemplos, sin espacios al final del prompt, y
   el texto normalizado (strip, mismo uso de mayúsculas) antes de comparar o
   de usarlo como stop sequence.""")
