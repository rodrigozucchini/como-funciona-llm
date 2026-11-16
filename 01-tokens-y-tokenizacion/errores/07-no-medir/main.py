import random
import statistics
import sys
from pathlib import Path

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "implementaciones" / "06-contar-y-estimar-costo"))
from costo import costo, dolares, miles  # noqa: E402

MODELO = "claude-opus-5-5"
random.seed(42)


def simular_request(funcion):
    """Devuelve un dict con la misma forma que el `usage` de la API."""
    if funcion == "chat":
        # El system prompt tiene la fecha y hora adentro: cambia en cada request,
        # así que el caché se escribe siempre y no se lee nunca.
        historial = random.randint(3_000, 12_000)
        return {"input_tokens": 50, "output_tokens": random.randint(150, 500),
                "cache_creation_input_tokens": historial, "cache_read_input_tokens": 0}
    if funcion == "resumir":
        # La mayoría son documentos chicos, pero de vez en cuando alguien sube un PDF enorme.
        doc = random.randint(80_000, 180_000) if random.random() < 0.03 else random.randint(1_500, 6_000)
        return {"input_tokens": doc, "output_tokens": random.randint(200, 600),
                "cache_creation_input_tokens": 0, "cache_read_input_tokens": 0}
    # clasificar: chico y con el prompt bien cacheado
    return {"input_tokens": random.randint(80, 200), "output_tokens": random.randint(10, 30),
            "cache_creation_input_tokens": 0, "cache_read_input_tokens": 1_800}


def costo_de(u):
    return costo(MODELO, input=u["input_tokens"], output=u["output_tokens"],
                 cache_write=u["cache_creation_input_tokens"], cache_read=u["cache_read_input_tokens"])


# Un mes, muestreado: 10.000 requests que representan 3.000.000.
MUESTRA, REALES = 10_000, 3_000_000
escala = REALES / MUESTRA
log = []
for _ in range(MUESTRA):
    funcion = random.choices(["chat", "resumir", "clasificar"], weights=[30, 10, 60])[0]
    log.append({"funcion": funcion, **simular_request(funcion)})

real = sum(costo_de(u) for u in log) * escala
estimado = costo(MODELO, input=2000, output=300) * REALES

print("❌ Sin medir: \"un request típico tiene ~2.000 de input y ~300 de output\"\n")
print(f"     estimación:  {dolares(estimado)} por mes")
proporcion = f"{real / estimado:.1f}".replace(".", ",")
print(f"     factura:     {dolares(real)} por mes   ({proporcion}x)")
print("\n     Y aunque el total diera parecido, no sabrías de dónde sale la plata.\n")

print("✅ Guardando el usage de cada respuesta, con la función que lo generó:\n")
print(f"  {'función':<11} {'requests':>9} {'input p50':>10} {'input máx':>10} {'cache hit':>10} "
      f"{'costo/mes':>10} {'% total':>8}")
for funcion in ["chat", "resumir", "clasificar"]:
    filas = [u for u in log if u["funcion"] == funcion]
    entradas = sorted(u["input_tokens"] + u["cache_creation_input_tokens"] + u["cache_read_input_tokens"]
                      for u in filas)
    leidos = sum(u["cache_read_input_tokens"] for u in filas)
    hit = leidos / sum(entradas)
    total = sum(costo_de(u) for u in filas) * escala
    print(f"  {funcion:<11} {miles(round(len(filas) * escala)):>9} {miles(int(statistics.median(entradas))):>10} "
          f"{miles(entradas[-1]):>10} {hit:>10.0%} {dolares(total):>10} {total / real:>8.0%}")

grandes = [u for u in log if u["funcion"] == "resumir" and u["input_tokens"] > 50_000]
costo_grandes = sum(costo_de(u) for u in grandes) * escala
print(f"""
  Con la tabla aparecen dos problemas que el promedio escondía:

  1. 'chat' tiene 0% de cache hit: el caché se escribe en cada request (a 1,25x)
     y no se lee nunca. Causa típica: algo que cambia en el prefijo, como la
     fecha y hora en el system prompt. Moverlo al final del prompt lo arregla.

  2. En 'resumir', el {len(grandes) / len([u for u in log if u['funcion'] == 'resumir']):.0%} de los requests son documentos de más de 50.000
     tokens y se llevan {dolares(costo_grandes)} por mes ({costo_grandes / (sum(costo_de(u) for u in log if u["funcion"] == "resumir") * escala):.0%} del costo de 'resumir').
     El p50 no los muestra; el máximo sí. Con un límite de tamaño, o un modelo
     más barato para esos casos, se resuelve.

✅ Qué guardar de cada respuesta: input_tokens, output_tokens,
   cache_creation_input_tokens, cache_read_input_tokens, el modelo y la función
   del producto que hizo el request. Y una alerta si el costo diario se dispara.""")
