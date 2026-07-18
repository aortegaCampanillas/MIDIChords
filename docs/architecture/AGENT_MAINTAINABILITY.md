# Mantenibilidad para agentes

Estado de la refactorización orientada a reducir contexto, explicitar fronteras y hacer verificables los cambios realizados por agentes.

## Resultado de esta fase

| Área | Antes | Ahora | Fronteras añadidas |
|---|---:|---:|---|
| Flutter `main.dart` | 13.774 líneas | 8.576 líneas | catálogo musical, servicio musical puro, painters, layout del piano y páginas por modo |
| Web `app.js` | 8.902 líneas | ~7.750 líneas | textos, notación, teoría del círculo e intervalos, ayuda de acordes y configuración de callouts |
| Verificación | comandos dispersos | `scripts/check.py` + CI | perfiles Python, web y móvil; tests Node sin dependencias |

También se añadieron instrucciones locales `AGENTS.md` y la matriz [SOURCE_OF_TRUTH.md](SOURCE_OF_TRUTH.md), para que un agente pueda localizar contratos y copias sin leer el monorepo completo.

## Criterio usado

Se extrajeron primero datos declarativos, funciones puras y dibujo sin estado. Cada frontera nueva tiene al menos comprobación de sintaxis y, cuando contiene comportamiento, tests directos. No se introdujo un framework nuevo de estado ni una capa abstracta únicamente para reducir el contador de líneas.

## Siguientes candidatos

Las siguientes unidades siguen siendo grandes, pero ya requieren cambios de diseño:

1. `apps/mobile_flutter/lib/main.dart`: separar audio, MIDI, preferencias y afinador por ciclo de vida. Antes conviene crear tests con adaptadores falsos para permisos, dispositivos y temporizadores.
2. `apps/web/static/app.js`: aislar audio/Web MIDI y después renderers por modo. Debe conservarse el gesto de audio del navegador, notas retenidas, selección MIDI y orden de carga.
3. `midichords/mixins/ui_mixin.py`: dividir construcción de paneles Qt por modo. Los nuevos módulos deben seguir usando el estado de la aplicación y el shim Qt existente, sin reintroducir Tk real.

No conviene continuar con extracciones mecánicas de estos bloques: mover métodos con estado sin definir primero sus contratos aumentaría el acoplamiento oculto y dificultaría las pruebas.

## Verificación

Desde la raíz:

```bash
python scripts/check.py all
```

Para cambios web, `app.html` es la lista ordenada de scripts y CSS. El build, la comprobación de sintaxis y la salud de producción descubren automáticamente esos assets.
