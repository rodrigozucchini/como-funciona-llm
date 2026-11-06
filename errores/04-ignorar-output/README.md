# Optimizar solo el input

Recortar el prompt (sacar instrucciones, comprimir ejemplos) y dejar que el modelo conteste con párrafos que nadie lee. Cada token de output cuesta **5 veces** lo que uno de input, y los tokens de razonamiento también se cobran como output.

```
Clasificar 1.000.000 de tickets por mes con Opus 5.5:
  respuesta en prosa (1.500 in, 400 out)         $14.000
  prompt recortado 30%, misma prosa              $12.200   (13% menos)
  prompt original, JSON de 40 tokens              $6.800   (51% menos)
```

Además, el output es lo que más tarda: los tokens de input se procesan todos juntos (prefill), pero los de output se generan **de a uno**. Una respuesta más corta también es una respuesta más rápida.

**Fix:**
- Pedir un formato estructurado (JSON, una etiqueta) y nada más.
- `max_tokens` acorde a lo que esperás que mida la respuesta.
- Bajar el `effort` en tareas simples: menos razonamiento.
- Pedir explicaciones solo cuando hacen falta.

```bash
python3 errores/04-ignorar-output/main.py
```
