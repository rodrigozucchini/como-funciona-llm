import re
import sys
from pathlib import Path

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "implementaciones" / "03-byte-level-bpe"))
from byte_level_bpe import tokenizer_entrenado  # noqa: E402

tok = tokenizer_entrenado()
LIMITE = 18   # tokens que "entran" (en la vida real: la ventana de contexto, o lo que reservaste)

documento = ("el gato come pescado. el perro come carne 🥩. "
             "los gatitos corren rápido. nosotros comemos con los perros.")

print(f"Documento: {len(documento)} caracteres, {len(documento.encode('utf-8'))} bytes, "
      f"{len(tok.encode(documento))} tokens. Límite: {LIMITE} tokens.\n")

print("❌ 1. Cortar por bytes (ej: un campo de la DB de tamaño fijo, o un buffer):\n")
cortado = documento.encode("utf-8")[:44]
try:
    cortado.decode("utf-8")
except UnicodeDecodeError as e:
    print(f"     .decode('utf-8') -> UnicodeDecodeError: {e.reason}")
print(f"     con errors='replace' -> {cortado.decode('utf-8', errors='replace')!r}")
print("     El emoji ocupa 4 bytes y el corte cayó en el medio.\n")

print("❌ 2. Cortar por caracteres, con un \"4 caracteres por token\":\n")
cortado = documento[:LIMITE * 4]
print(f"     documento[:{LIMITE * 4}] -> {len(tok.encode(cortado))} tokens (límite: {LIMITE})")
print("     Te pasás igual: los caracteres por token cambian con cada texto.\n")

print("❌ 3. Cortar la lista de tokens sin mirar dónde:\n")
cortado = tok.decode(tok.encode(documento)[:LIMITE])
print(f"     tokens[:{LIMITE}] -> {cortado!r}")
print("     Entra, pero queda cortado en cualquier lado (y podría partir un carácter).\n")


def truncar(texto, limite):
    """Agrega oraciones completas mientras entren en el límite de tokens."""
    oraciones = re.findall(r"[^.!?]+[.!?]?\s*", texto)
    resultado = ""
    for oracion in oraciones:
        if len(tok.encode((resultado + oracion).strip())) > limite:
            break
        resultado += oracion
    return resultado.strip()


cortado = truncar(documento, LIMITE)
print("✅ Truncar por tokens, en un límite natural (oración, párrafo):\n")
print(f"     -> {cortado!r}")
print(f"     {len(tok.encode(cortado))} tokens, texto completo hasta donde llega.")
print("""
   Y antes de truncar, preguntate si hace falta: muchas veces conviene resumir,
   partir el documento en pedazos (chunking) o recuperar solo lo relevante.""")
