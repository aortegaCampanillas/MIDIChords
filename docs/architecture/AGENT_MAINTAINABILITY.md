# Mantenibilidad para agentes

Estado de la refactorización orientada a reducir contexto, explicitar fronteras y hacer verificables los cambios realizados por agentes.

**Estado de la fase: completada.** La fase estructural y su continuación de contratos de integración están cerradas; las extracciones futuras deberán ampliar estos contratos antes de mover más estado.

## Fase de contratos de integración

Completada. El contrato del backlog de escritorio queda establecido:

- `tests/test_desktop_ui_contract.py` construye la ventana Qt en modo `offscreen`, sin audio, MIDI, caché ni escritura de configuración reales.
- El contrato comprueba los widgets públicos consumidos por los mixins y las transiciones entre Generación, Círculo de quintas y Escalas.
- `midichords/ui/desktop_ui_builders.py` contiene builders para la barra superior, la carcasa central, las raíces de cada modo y los selectores de tipo, tónica y alteración de escalas, cubiertos por ese smoke test.

Las siguientes extracciones de `_build_ui()` deben ampliar primero la lista de widgets o señales del contrato cuando publiquen una frontera nueva.

El contrato web queda establecido en `ui_lifecycle.js`: aporta registro y desmontaje deterministas de listeners y temporizadores, probado con targets DOM y reloj falsos. La coordinación global de `window` y `document` ya está fuera de `bindEvents`; los listeners de controles podrán migrarse por bloques bajo el mismo contrato.

La primera migración de controles también está cerrada: los botones de pulsación
inmediata (Play/Stop en varios modos) delegan ratón, touch, teclado, estado visual
y liberación diferida en `bindImmediatePress`. El contrato comprueba la supresión
del clic que sigue a una pulsación de puntero y el desmontaje conjunto de listeners
del botón y del documento.

Los controles de modales también delegan ya en `bindModalControls`: el módulo
posee los listeners de apertura, cierre y fondo, mientras `app.js` conserva las
acciones concretas de ayuda, feedback y descargas. El fixture comprueba que un
clic en el contenido no cierre el diálogo y que el desmontaje sea completo.

Los eventos globales de teclado están igualmente encapsulados: Escape se enruta
a la política de cierre de `app.js`, mientras el módulo normaliza pulsación,
repetición, liberación y pérdida de foco de Mayús. El estado específico de
detección permanece en la SPA y se limpia también si el foco cambia.

Los gestos de desbloqueo de Web Audio usan asimismo el ciclo de vida compartido:
el callback de la SPA conserva la decisión de crear o reanudar el contexto, y el
módulo garantiza el alta y desmontaje conjunto de puntero y teclado.

Los listeners de controles generales, MIDI, detección, intervalos, generación y
escalas han migrado también al registro común. Sus callbacks y estado permanecen
en `app.js`, pero la propiedad y retirada de eventos ya no se gestiona de forma
ad hoc en cada control.

La migración de `bindEvents` queda completada con metrónomo, temporizador,
afinador y feedback. `test_web_ui_lifecycle_contract.py` fija la frontera: ese
bloque no puede volver a registrar listeners directos fuera de `uiLifecycle`.

La separación del renderer web avanza mediante geometría pura: `staff_beam_geometry.js` decide la dirección común de plicas y calcula los segmentos primarios y secundarios; `staff_geometry.js` transforma MIDI en posiciones de clave de sol/fa y calcula líneas adicionales. Sus pruebas no dependen del canvas.

Las familias del selector de escalas conservan implementaciones declarativas locales por plataforma, pero `test_scale_family_cross_platform.py` fija composición y orden idénticos. Cualquier escala nueva obliga así a actualizar explícitamente las tres copias antes de pasar la suite.

En Flutter, `midi_activity_guard.dart` establece la primera frontera de ciclo de vida: encapsula `WakelockPlus` y la ventana temporal renovable de actividad MIDI. El widget conserva únicamente la decisión de cuándo renovar o cancelar; las pruebas usan un puerto falso y reloj controlado para fijar renovación, expiración y desmontaje idempotente.

`app_preferences.dart` aplica el mismo patrón a configuración persistente: el estado intercambia una instantánea tipada y el repositorio concentra claves, defaults y validación sobre un puerto reemplazable. Así se pueden probar migraciones y valores corruptos sin inicializar el plugin de preferencias.

`midi_input_lifecycle.dart` posee las dos suscripciones del plugin MIDI y transforma los paquetes en listas de bytes antes de entregarlos al estado. Su contrato evita registros duplicados y garantiza que datos y eventos de conexión se cancelan juntos durante el desmontaje.

`midi_output_controller.dart` encapsula los mensajes de salida detrás de un puerto mínimo. Conserva la caché de Program Change fuera del widget, normaliza bytes, reintenta un cambio de timbre fallido y fuerza su reenvío después de desconectar la sesión; las pruebas no necesitan hardware ni el plugin activo.

## Resultado de esta fase

| Área | Antes | Ahora | Fronteras añadidas |
|---|---:|---:|---|
| Flutter `main.dart` | 13.774 líneas | 7.516 líneas | catálogo y servicio musical, painters, páginas por modo, ayuda, preferencias y entrada/salida MIDI |
| Web `app.js` | 8.902 líneas | 7.158 líneas | textos, teoría, notación, ayudas, MIDI/audio, resaltado, ciclo de vida global y geometría de partitura |
| Escritorio `ui_mixin.py` | 4.012 líneas | 3.905 líneas | builders Qt para estructura principal y selectores de escalas, bajo smoke contract |
| Verificación | comandos dispersos | `scripts/check.py` + CI | perfiles Python, web y móvil; tests Node sin dependencias |

También se añadieron instrucciones locales `AGENTS.md` y la matriz [SOURCE_OF_TRUTH.md](SOURCE_OF_TRUTH.md), para que un agente pueda localizar contratos y copias sin leer el monorepo completo.

## Criterio usado

Se extrajeron primero datos declarativos, funciones puras y dibujo sin estado. Después se aislaron la salida MIDI, la descarga/caché de samples y la liberación de voces mediante dependencias inyectables, además de la matemática de audio mediante buffers y nodos falsos. Cada frontera nueva tiene al menos comprobación de sintaxis y, cuando contiene comportamiento, tests directos. No se introdujo un framework nuevo de estado ni una capa abstracta únicamente para reducir el contador de líneas.

## Límites deliberadamente pendientes

La auditoría de cierre localizó estos bloques. Son backlog de diseño, no trabajo estructural pendiente de esta fase:

| Área | Acoplamiento observado | Prerrequisito antes de separar |
|---|---|---|
| Flutter `main.dart` | audio y afinador aún comparten plugins y estado visual | puertos específicos de sesión/player y pruebas de integración del widget antes de moverlos |
| Web `app.js` | `renderStaff`, `renderGuitar` y eventos de controles conservan DOM/canvas y estado global | ampliar el fixture con el canvas o control concreto antes de cada extracción |
| Escritorio `ui_mixin.py` | los controles internos de cada modo aún se construyen en métodos extensos | ampliar el smoke contract con sus señales públicas antes de nuevos builders |

No conviene continuar con extracciones mecánicas de estos bloques: mover métodos con estado sin definir primero esos contratos aumentaría el acoplamiento oculto. El tamaño de archivo por sí solo no autoriza una nueva separación.

## Auditoría funcional posterior: guitarra

La revisión de digitaciones se ejecuta por familias mediante
`scripts/sync_guitar_chord_reference.py`. La utilidad fija el mapeo entre sufijos
internos y el catálogo público actual, y deja explícitos los tipos propios sin
equivalente exacto. Ya están verificadas las familias de notas añadidas (`add2`,
`add4`, `madd2`, `madd4`, `add9`, `madd9`) y las tríadas básicas (mayor, menor,
disminuida y aumentada). Las siguientes familias se revisarán con la misma
utilidad, sin sustituir tipos propios por acordes solo aproximadamente iguales.
También están sincronizados los power chords y los suspendidos `sus2` y `sus4`;
`sus2sus4` permanece explícitamente como tipo propio.
La familia de sextas compartida (`6`, `6add9`, `m6`) está asimismo sincronizada;
`m6add9` se conserva como tipo propio.
Las séptimas dominantes simples (`7`, `7sus4`, `7#5`, `7b5`, `7#9`, `7b9`)
están sincronizadas; las cuatro combinaciones de quinta y novena alteradas siguen
siendo tipos propios.
Las extensiones dominantes compartidas (`9`, `9#5`, `9b5`, `11`, `13`, `13b9`,
`13#11`) están sincronizadas; `11b9` se conserva como tipo propio.
Las extensiones mayores compartidas (`maj7`, `maj7#5`, `maj9`, `maj11`, `maj13`)
están sincronizadas; `maj7b5`, `maj9#11` y `maj13#11` se conservan como tipos
propios.
Las familias menores compartidas (`m7`, `m9`, `m11`, `m13`, `mMaj7`, `mMaj9`,
`dim7`, `m7b5`) están sincronizadas; `m7#5` se conserva como tipo propio. Con
este bloque, los 42 tipos con equivalente exacto están auditados para las doce
tónicas. Los 12 tipos restantes están identificados como catálogo propio y no
forman parte de la sincronización externa.

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
