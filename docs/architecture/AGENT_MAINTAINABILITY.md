# Mantenibilidad para agentes

Estado de la refactorización orientada a reducir contexto, explicitar fronteras y hacer verificables los cambios realizados por agentes.

**Estado de la fase: completada.** Las extracciones restantes requieren primero nuevos contratos de ciclo de vida o pruebas de integración de UI; no forman parte de esta fase estructural.

## Fase de contratos de integración

En curso. El primer prerrequisito del backlog de escritorio ya existe:

- `tests/test_desktop_ui_contract.py` construye la ventana Qt en modo `offscreen`, sin audio, MIDI, caché ni escritura de configuración reales.
- El contrato comprueba los widgets públicos consumidos por los mixins y las transiciones entre Generación, Círculo de quintas y Escalas.
- `midichords/ui/desktop_ui_builders.py` contiene builders para la barra superior, la carcasa central y las raíces de cada modo, cubiertos por ese smoke test.

Las siguientes extracciones de `_build_ui()` deben ampliar primero la lista de widgets o señales del contrato cuando publiquen una frontera nueva.

El prerrequisito web también está en curso: `ui_lifecycle.js` aporta registro y desmontaje deterministas de listeners y temporizadores, probado con targets DOM y reloj falsos. La coordinación global de `window` y `document` ya está fuera de `bindEvents`; los listeners de controles se migrarán por bloques antes de separar el resto.

La separación del renderer ha comenzado por geometría pura: `staff_beam_geometry.js` decide la dirección común de plicas y calcula los segmentos primarios y secundarios de los grupos barrados. Sus pruebas fijan tanto la dirección coherente como el paralelismo de las barras de semicorchea sin depender del canvas.

En Flutter, `midi_activity_guard.dart` establece la primera frontera de ciclo de vida: encapsula `WakelockPlus` y la ventana temporal renovable de actividad MIDI. El widget conserva únicamente la decisión de cuándo renovar o cancelar; las pruebas usan un puerto falso y reloj controlado para fijar renovación, expiración y desmontaje idempotente.

## Resultado de esta fase

| Área | Antes | Ahora | Fronteras añadidas |
|---|---:|---:|---|
| Flutter `main.dart` | 13.774 líneas | 7.524 líneas | catálogo musical, servicio musical puro, painters, layout del piano, páginas por modo y subsistema de ayuda |
| Web `app.js` | 8.902 líneas | 7.169 líneas | textos, notación, teoría/interacción del círculo, intervalos/escalas, digitaciones, armaduras, ayudas, salida MIDI, audio por samples, resaltado de reproducción y matemática del afinador |
| Verificación | comandos dispersos | `scripts/check.py` + CI | perfiles Python, web y móvil; tests Node sin dependencias |

También se añadieron instrucciones locales `AGENTS.md` y la matriz [SOURCE_OF_TRUTH.md](SOURCE_OF_TRUTH.md), para que un agente pueda localizar contratos y copias sin leer el monorepo completo.

## Criterio usado

Se extrajeron primero datos declarativos, funciones puras y dibujo sin estado. Después se aislaron la salida MIDI, la descarga/caché de samples y la liberación de voces mediante dependencias inyectables, además de la matemática de audio mediante buffers y nodos falsos. Cada frontera nueva tiene al menos comprobación de sintaxis y, cuando contiene comportamiento, tests directos. No se introdujo un framework nuevo de estado ni una capa abstracta únicamente para reducir el contador de líneas.

## Límites deliberadamente pendientes

La auditoría de cierre localizó estos bloques. Son backlog de diseño, no trabajo estructural pendiente de esta fase:

| Área | Acoplamiento observado | Prerrequisito antes de separar |
|---|---|---|
| Flutter `main.dart` | audio, entrada/salida MIDI, preferencias, afinador, `initState()` y `dispose()` comparten plugins, suscripciones, timers y estado visual | adaptadores inyectables para plugins y pruebas de alta/baja, reconexión, cancelación y permisos |
| Web `app.js` | `renderStaff`, `renderGuitar`, `bindEvents` y el desbloqueo de audio comparten DOM, canvas, listeners, timers y estado global | fixture DOM/canvas con listeners y reloj falsos; pruebas de montar, cambiar de modo y desmontar |
| Escritorio `ui_mixin.py` | `_build_ui()` crea y enlaza en una sola operación los widgets Qt que consumen todos los mixins | smoke test de árbol de widgets, atributos públicos, señales y cambio de modo antes de extraer builders por panel |

No conviene continuar con extracciones mecánicas de estos bloques: mover métodos con estado sin definir primero esos contratos aumentaría el acoplamiento oculto. El tamaño de archivo por sí solo no autoriza una nueva separación.

## Criterio de cierre

- Las fuentes de verdad y copias están inventariadas.
- Cada módulo ejecutable extraído tiene tests directos o queda cubierto por analyzer/smoke tests existentes.
- Hay un comando único para validar Python, web y móvil.
- Los archivos grandes restantes tienen responsabilidad y prerrequisitos explícitos.
- La salida generada (`apps/web/pages-dist/`) no se versiona ni se usa como fuente.

## Verificación

Desde la raíz:

```bash
python scripts/check.py all
```

Para cambios web, `app.html` es la lista ordenada de scripts y CSS. El build, la comprobación de sintaxis y la salud de producción descubren automáticamente esos assets.
