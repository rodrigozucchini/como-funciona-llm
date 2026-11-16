"""
Calculadora de costo por token.

No tokeniza nada: recibe cantidades de tokens, que en la práctica salen del
`usage` de cada respuesta o del endpoint `count_tokens`. La idea es ver de
dónde sale la plata: input vs output, el historial de un chat, el caché,
el razonamiento y el modo batch.

Uso:
    python3 costo.py
"""

# ---------------------------------------------------------------------------
# Precios en dólares por millón de tokens (MTok).
# Consultados en octubre de 2026 en la referencia de la API de Claude.
# CAMBIAN SEGUIDO: antes de usar estos números para algo real, revisá
# https://platform.claude.com/docs/en/about-claude/pricing
# ---------------------------------------------------------------------------

PRECIOS = {
    #                      input   output  cache read
    "claude-fable-5-1":  (10.00,   50.00,   0.25),
    "claude-opus-5-5":   ( 4.00,   20.00,   0.20),
    "claude-sonnet-5-5": ( 2.00,   10.00,   0.20),
    "claude-haiku-5-5":  ( 0.10,    0.50,   0.01),   # hasta 100K tokens de prompt; cache read estimado con la regla general (0,1x)
}

# Escribir en el caché cuesta más que el input normal, según cuánto dura.
MULTIPLICADOR_CACHE_WRITE = {"5m": 1.25, "1h": 2.0}
DESCUENTO_BATCH = 0.5   # la Batch API cobra la mitad


def costo(modelo, input=0, output=0, cache_write=0, cache_read=0, ttl="5m", batch=False):
    """
    input:        tokens de input que NO se leen del caché
    output:       tokens generados (incluye los de razonamiento)
    cache_write:  tokens de input que se escriben en el caché
    cache_read:   tokens de input que se leen del caché
    """
    p_in, p_out, p_read = PRECIOS[modelo]
    total = (
        input * p_in
        + output * p_out
        + cache_write * p_in * MULTIPLICADOR_CACHE_WRITE[ttl]
        + cache_read * p_read
    ) / 1_000_000
    return total * DESCUENTO_BATCH if batch else total


def a_espanol(texto):
    """1,234.56 -> 1.234,56"""
    return texto.replace(",", "_").replace(".", ",").replace("_", ".")


def miles(n):
    return a_espanol(f"{n:,}")


def dolares(x):
    if x >= 100:
        return "$" + a_espanol(f"{x:,.0f}")
    if x >= 1:
        return "$" + a_espanol(f"{x:,.2f}")
    if x >= 0.001:
        return "$" + a_espanol(f"{x:.4f}")
    return "$" + a_espanol(f"{x:.5f}")


# ---------------------------------------------------------------------------
# Demo
# ---------------------------------------------------------------------------

def main():
    print("=" * 70)
    print("1. UN REQUEST: 2.000 tokens de input, 500 de output")
    print("=" * 70)
    print(f"  {'modelo':<19} {'input':>9} {'output':>9} {'total':>9} {'% output':>9}")
    for modelo in PRECIOS:
        i = costo(modelo, input=2000)
        o = costo(modelo, output=500)
        print(f"  {modelo:<19} {dolares(i):>9} {dolares(o):>9} {dolares(i + o):>9} {o / (i + o):>9.0%}")
    print("\n  El output es 1/5 de los tokens y más de la mitad del costo:")
    print("  cada token de output cuesta 5 veces lo que uno de input.")

    print("\n" + "=" * 70)
    print("2. UN CHAT DE 20 TURNOS: el historial se paga en cada turno")
    print("=" * 70)
    modelo = "claude-opus-5-5"
    system, pregunta, respuesta = 3000, 50, 300
    print(f"  {modelo}. System prompt de {miles(system)} tokens; cada turno el usuario")
    print(f"  manda {pregunta} tokens y el modelo responde {respuesta}.\n")
    print(f"  {'turno':>5} {'input del turno':>16} {'sin caché':>11} {'con caché':>11}")

    total_sin = total_con = 0
    historial = system
    cacheado = 0
    for turno in range(1, 21):
        input_turno = historial + pregunta
        sin = costo(modelo, input=input_turno, output=respuesta)
        # Con caché: lo que ya estaba cacheado se lee barato; lo nuevo se escribe.
        con = costo(modelo, cache_read=cacheado, cache_write=input_turno - cacheado,
                    output=respuesta)
        total_sin += sin
        total_con += con
        if turno in (1, 2, 5, 10, 20):
            print(f"  {turno:>5} {miles(input_turno):>16} {dolares(sin):>11} {dolares(con):>11}")
        cacheado = input_turno
        historial = input_turno + respuesta

    print(f"\n  Total de la conversación: sin caché {dolares(total_sin)}, "
          f"con caché {dolares(total_con)} ({1 - total_con / total_sin:.0%} menos)")
    print("\n  Sin caché, el turno 20 vuelve a pagar los 19 anteriores completos: el costo")
    print("  total crece con el cuadrado de los turnos. Con prompt caching, el prefijo")
    print("  que ya se mandó se lee a una fracción del precio. El turno 1 sale más caro")
    print("  (escribir en el caché cuesta 1,25x), pero desde el 2 ya conviene.")

    print("\n" + "=" * 70)
    print("3. RAZONAMIENTO: los tokens que no ves también se cobran")
    print("=" * 70)
    print("  Mismo request (2.000 de input, 500 de respuesta visible), con distintas")
    print("  cantidades de razonamiento (los números de tokens son ilustrativos):\n")
    print(f"  {'razonamiento':>13} {'output total':>13} {'costo':>9} {'vs. sin pensar':>15}")
    base = costo(modelo, input=2000, output=500)
    for pensamiento in [0, 1000, 4000, 16000]:
        c = costo(modelo, input=2000, output=500 + pensamiento)
        print(f"  {miles(pensamiento):>13} {miles(500 + pensamiento):>13} {dolares(c):>9} "
              f"{a_espanol(f'{c / base:.1f}'):>14}x")
    print("\n  Los tokens de razonamiento se cobran como output (el más caro). El parámetro")
    print("  effort controla cuánto piensa el modelo: alto para lo difícil, bajo para lo")
    print("  simple. Medí el costo por tarea resuelta, no por request.")

    print("\n" + "=" * 70)
    print("4. POR MES: 100.000 requests por día")
    print("=" * 70)
    por_mes = 100_000 * 30
    print(f"  {miles(por_mes)} requests de 2.000 input + 500 output:\n")
    print(f"  {'modelo':<19} {'normal':>12} {'batch (-50%)':>13}")
    for m in PRECIOS:
        normal = costo(m, input=2000, output=500) * por_mes
        lote = costo(m, input=2000, output=500, batch=True) * por_mes
        print(f"  {m:<19} {dolares(normal):>12} {dolares(lote):>13}")
    print("\n  Batch: si no necesitás la respuesta al instante (clasificar, resumir,")
    print("  evaluar), la Batch API procesa en horas y cobra la mitad.")

    print("\n" + "=" * 70)
    print("5. DÓNDE CONVIENE RECORTAR")
    print("=" * 70)
    base = costo(modelo, input=2000, output=500)
    opciones = {
        "recortar el prompt 20%":             costo(modelo, input=1600, output=500),
        "respuestas 20% más cortas":          costo(modelo, input=2000, output=400),
        "cachear 1.500 tokens del prompt":    costo(modelo, input=500, cache_read=1500, output=500),
        "batch":                              costo(modelo, input=2000, output=500, batch=True),
    }
    print(f"  Base: {dolares(base)} por request ({modelo}, 2.000 input + 500 output)\n")
    for nombre, c in opciones.items():
        print(f"  {nombre:<34} {dolares(c):>9}   ({1 - c / base:>4.0%} menos)")
    print("\n  Recortar el output 20% ahorra más que recortar el prompt 20%.")
    print("  (El caso del caché asume que el prefijo ya estaba escrito por un request anterior.)")


if __name__ == "__main__":
    main()
