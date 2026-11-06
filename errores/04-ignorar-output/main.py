import sys
from pathlib import Path

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "implementaciones" / "06-contar-y-estimar-costo"))
from costo import costo, dolares, miles  # noqa: E402

MODELO = "claude-opus-5-5"
REQUESTS_POR_MES = 1_000_000

# Clasificar tickets de soporte: el prompt tiene instrucciones y el ticket.
casos = {
    "❌ original: respuesta en prosa":      dict(input=1500, output=400),
    "❌ prompt recortado 30%, misma prosa": dict(input=1050, output=400),
    "✅ prompt original, JSON corto":       dict(input=1500, output=40),
}

print(f"Clasificar tickets con {MODELO}, {miles(REQUESTS_POR_MES)} requests por mes\n")
print(f"  {'caso':<38} {'input':>6} {'output':>7} {'por mes':>10}")
base = costo(MODELO, **casos["❌ original: respuesta en prosa"]) * REQUESTS_POR_MES
for nombre, tokens in casos.items():
    mes = costo(MODELO, **tokens) * REQUESTS_POR_MES
    ahorro = f"({1 - mes / base:.0%} menos)" if mes < base else ""
    print(f"  {nombre:<38} {miles(tokens['input']):>6} {tokens['output']:>7} {dolares(mes):>10}  {ahorro}".rstrip())

print("""
  La respuesta en prosa ("Este ticket parece estar relacionado con un problema
  de facturación, ya que el usuario menciona...") son ~400 tokens. Lo que hace
  falta es:

    {"categoria": "facturacion", "urgencia": "alta"}

  Recortar el prompt un 30% (y arriesgar la calidad) ahorra menos que dejar de
  pedir una explicación que nadie lee.

✅ Qué hacer con el output:
   - Pedir un formato estructurado (JSON, una etiqueta, una lista) y nada más.
   - Poner un max_tokens acorde a lo que esperás que mida la respuesta.
   - Para tareas simples, bajar el effort: menos razonamiento, que también es output.
   - Si necesitás la explicación, pedila solo cuando hace falta (ej: urgencia alta).""")
