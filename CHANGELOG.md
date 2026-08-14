# Changelog

Historial de versiones publicadas de MIDIChords.

## Unreleased

- **Práctica de intervalos**: durante la corrección, las columnas correcta e incorrecta se pueden pulsar para escucharlas aunque estén excluidas por el filtro, en web, escritorio y móvil.
- **Escritorio / práctica de intervalos**: las respuestas incorrectas marcan en rojo su columna de semitonos y muestran en verde la esperada, incluso al contestar la nota en otra octava.
- **Web / generación de acordes**: al cambiar de acorde o inversión se selecciona automáticamente la primera variante de guitarra.
- **Escritorio / generación de acordes**: las posiciones abiertas de Re mayor, Sol mayor y La mayor conservan sus digitaciones habituales; Sol ya no se representa erróneamente con una cejilla.
- **Distribución iOS**: actualizado el requisito mínimo a iOS 15 para cumplir las nuevas condiciones de App Store Connect.
- **Audio**: aumentado el nivel general del escritorio manteniendo margen seguro para acordes.
- **Práctica de intervalos**: el resaltado de la primera nota ya no puede desaparecer por temporizadores pendientes al cambiar de modo o avanzar rápidamente.
- **Presentación**: renovadas las capturas bilingües de la portada y corregidos varios ajustes visuales del escritorio.
- **Práctica de intervalos**: nuevo modo de entrenamiento auditivo en web, escritorio y móvil, con configuración del ejercicio, corrección visual, puntuación y revisión de resultados.
- **PianoPilot (landing)**: sincronizados la versión pública y el historial bilingüe con la versión 1.0.4 del proyecto fuente, incluida la corrección de conexión MIDI en Windows.
- **Web (landing)**: la portada muestra la insignia oficial de nominación de FreeMIDIChords a los Open Education Awards for Excellence 2026, con contexto bilingüe y enlace a la credencial verificable.
- **Móvil / audio Android**: los samples nativos se reproducen desde PCM precodificado y solo fuerzan el altavoz interno cuando existe una salida de audio USB, evitando la creación repetida de decodificadores y la reconstrucción innecesaria de pistas de audio.
- **Detección de Notas**: nuevo modo didáctico que conserva la última nota tocada desde el piano o MIDI, la representa sin armadura en la clave correspondiente y permite repetirla, limpiarla u ocultar su nombre junto con las etiquetas del teclado.
- Mantenimiento: el changelog de producto tiene ahora una única fuente canónica y las copias necesarias para web y Flutter se generan automáticamente durante lanzamientos, verificaciones y builds web.

### Versión

- **1.0.7**: preparadas las compilaciones de distribución para App Store Connect: iOS build 26 y macOS build 24.
- **1.0.7**: comienza el registro de cambios de la próxima versión.
- **1.0.5**: preparadas las compilaciones de distribución para App Store Connect: iOS build 19 y macOS build 21.
- **1.0.2**: versión alineada en **escritorio** (`APP_RELEASE_NAME`), **web** (`/api/meta` → `app_version`, JSON-LD) y **móvil** (`pubspec.yaml` **1.0.2+8**).

### Documentado

- **Landings (mantenimiento)**: MIDIChords y PianoPilot comparten ahora la infraestructura de idioma, capturas ampliables y formulario de comentarios; el perfil web descubre también los scripts enlazados exclusivamente desde las páginas públicas.
- **PianoPilot (landing)**: añadida una fuente de verdad versionada y contrastable con el repositorio del producto; se corrigen el catálogo a 153 tonos, las promesas absolutas de control y la explicación de USB MIDI, Bluetooth MIDI y posibles controladores del sistema.
- **Mantenimiento / agentes**: cerrada la fase estructural con resultados cuantitativos, criterios verificables y un backlog explícito para ciclos de vida Flutter, renderers/eventos web y construcción Qt; cada bloque pendiente indica las pruebas de integración necesarias antes de dividirlo.
- **Mantenimiento / agentes**: completada la continuación de contratos de integración: smoke contract y builders Qt, ciclo de vida y geometría de partitura web, y adaptadores probados para actividad, preferencias y suscripciones MIDI en Flutter.
- **Mantenimiento / tests**: consolidados los contratos de digitación de escalas en un harness parametrizado común, eliminando tablas y extensores duplicados sin perder fixtures, tonalidades, manos, direcciones ni casos de una y dos octavas.
- **Mantenimiento / teoría musical**: añadido un contrato offline único de generación de acordes, escalas y detección que se ejecuta sobre Python, Worker y Flutter; cubre idiomas, alteraciones, inversiones y familias representativas sin depender de producción.
- **Detección de acordes**: las etiquetas de las notas reconocidas en Python respetan ahora la ortografía armónica del acorde, manteniendo la preferencia visual de sostenidos o bemoles solo para notas ajenas, en paridad con web y móvil.
- **Escritorio (mantenimiento)**: extraída la construcción de los selectores de variante e inversión de Generación a una especificación común del builder Qt, después de fijar padres, atributos y configuración mediante el smoke contract.
- **Escritorio (mantenimiento)**: la fila de reproducción y ayuda de Generación se construye ahora en el builder Qt bajo un contrato previo de jerarquía; la liberación global del ratón permanece en el mixin como coordinación transversal.
- **Web (guitarra / mantenimiento)**: extraído al canvas probado el dibujo de cuerdas y nombres del mástil, incluida la simetría para zurdos; marcadores, cejillas, hit-testing y eventos conservan su estado en la SPA.
- **Mantenimiento / estructura**: los helpers reutilizables de digitación se agrupan en `tests/support/`, dejando la raíz de tests para casos y fixtures; imports y carga relativa de datos quedan actualizados.
- **Empaquetado macOS**: entitlements y plantilla de entorno se agrupan en `packaging/macos/`, mientras los comandos públicos permanecen en `scripts/`; firma, MAS, documentación e ignores apuntan a las nuevas rutas.
- **Escritorio (mantenimiento)**: actualizada la consulta de familias tipográficas a la API estática vigente de Qt, eliminando avisos de deprecación durante el arranque y el smoke contract.
- **Escalas**: los siete modos diatónicos muestran su grado en números romanos tanto en el selector como en el campo de nombre de la escala generada: Jónico (I), Dórico (II), Frigio (III), Lidio (IV), Mixolidio (V), Eólico (VI) y Locrio (VII).
- **Escalas**: el selector agrupa el catálogo por familias teóricas: Modos griegos, Escalas menores, Modos alterados, Pentatónicas y blues, Bebop, Simétricas y sintéticas y Tradicionales del mundo; las cabeceras no son seleccionables y cada escala aparece una sola vez.
- **Escritorio (escalas)**: el desplegable de Tipo respeta ahora su altura configurada de veinte filas, mostrando muchas más familias y opciones sin necesidad de desplazarse inmediatamente.
- **Mantenimiento / escalas**: añadida una prueba de contrato que impide que la composición y el orden de las familias teóricas diverjan entre escritorio, web y Flutter.
- **Generación de acordes**: añadidas las variantes menor con segunda añadida (`madd2`) y menor con cuarta añadida (`madd4`), con nombres bilingües, fórmulas, ayuda teórica y paridad de intervalos en las tres plataformas.
- **Web (partitura / mantenimiento)**: extraídas a un módulo puro la conversión MIDI→posición vertical en claves de sol y fa y la geometría de líneas adicionales, con pruebas de referencias, enarmonías y notas fuera del pentagrama.
- **Web (mantenimiento)**: extraída al ciclo de vida probado la interacción de los botones de pulsación inmediata; ratón, táctil y teclado comparten ahora liberación, resaltado y supresión del clic duplicado, y sus listeners y temporizadores se desmontan con la página.
- **Web (mantenimiento)**: ayuda de acordes, feedback y descargas comparten un contrato probado para abrir, cerrar y descartar modales desde el fondo, con desmontaje automático de todos sus listeners.
- **Web (mantenimiento)**: Escape, Mayús y la pérdida de foco se gestionan mediante el ciclo de vida probado; se ignoran repeticiones de Mayús y se limpia de forma consistente su estado global y de detección al soltar la tecla o cambiar de ventana.
- **Web (mantenimiento)**: los gestos globales que desbloquean Web Audio conservan sus reintentos cuando el navegador suspende el contexto, pero sus listeners de puntero y teclado se eliminan ahora durante el desmontaje.
- **Web (mantenimiento)**: los controles generales, MIDI, detección, intervalos, generación y escalas registran sus eventos mediante el ciclo de vida común, evitando listeners huérfanos tras abandonar o reconstruir la página.
- **Web (mantenimiento)**: metrónomo, temporizador, afinador y formulario de feedback completan la migración de `bindEvents`; una prueba de contrato impide volver a introducir listeners directos en ese bloque.
- **Web (guitarra / mantenimiento)**: extraída la detección de cejillas completas y parciales a una geometría pura y probada, incluyendo runs separados, cuerdas silenciadas y entradas inválidas; el renderer conserva únicamente el dibujo y el estado interactivo.
- **Web (guitarra / mantenimiento)**: el layout del mástil, sus centros de traste, la simetría para zurdos, el escalado de coordenadas del canvas y el hit-testing circular pasan a geometría pura con pruebas directas.
- **Web (partitura / mantenimiento)**: extraída la adaptación de octavas entre piano y pentagrama, incluida la nota visible más cercana, las voces sostenidas/reproducidas y el emparejado RH/LH de grados de escala, con pruebas sin canvas.
- **Escritorio (mantenimiento)**: extraída la construcción del selector agrupado de escalas y su filtro al módulo de builders Qt, conservando jerarquía, callbacks y altura bajo el smoke contract.
- **Móvil (mantenimiento)**: encapsulada la salida MIDI detrás de un puerto probado, incluyendo selección y caché de timbre, normalización de mensajes, reintento tras fallos y reinicio al desconectar dispositivos.
- **Móvil (mantenimiento)**: la captura del afinador queda detrás de una sesión y un puerto inyectables; inicialización, callbacks, frecuencia real, arranque único, recuperación tras fallo nativo y cierre idempotente se prueban sin micrófono ni plugin activo.
- **Escritorio (mantenimiento)**: extraída la construcción de los selectores de tónica y alteración de Escalas a un builder Qt, manteniendo atributos, callbacks y jerarquía bajo el smoke contract.

- **Mantenimiento / agentes**: corregida la arquitectura documentada del escritorio (Qt/PySide6 con compatibilidad de API Tk), añadidas instrucciones locales para Python, web y Flutter, y una matriz de fuentes de verdad y copias multiplataforma.

### Mejorado

- **Móvil (generación y práctica de intervalos)**: en tablet, el pentagrama ocupa menos altura y los paneles de selección y práctica ganan espacio para mostrar todo su contenido.
- **Móvil (detección de intervalos)**: el piano se centra correctamente en Do4 al entrar en el modo y al cambiar la orientación.
- **Móvil (generación de acordes)**: el piano vuelve a centrarse en Do4 al cambiar a orientación vertical, sin reutilizar desplazamientos calculados con otro ancho.
- **Móvil (tablet)**: en orientación vertical, la barra principal centra y amplía el selector de modo; los controles de Piano/Guitarra y mano derecha/izquierda usan iconos accesibles y ocupan menos espacio para ampliar el instrumento.
- **Móvil (detección de acordes)**: al abrir el modo, el piano se centra correctamente en Do4 también con la tablet en vertical.
- **Móvil (generación de intervalos)**: compactado el panel de resultados y la separación entre controles para aprovechar mejor la altura disponible.
- **Web (detección de notas)**: nuevo primer modo para identificar la última nota tocada desde el piano o MIDI, verla en la clave correspondiente del pentagrama sin armadura, repetirla, limpiarla y ocultar con fines didácticos tanto su resultado como los nombres sobre el teclado.
- **Detección de acordes e intervalos**: incorporado, junto a Limpiar, un botón con icono de ojo para ocultar la información detectada con fines didácticos y volver a mostrarla para comprobar la respuesta.
- **Móvil (ayuda de escalas)**: la tónica, su alteración/armadura y el tipo de escala disponen de resaltados y explicaciones independientes; su geometría estable se conserva al activar el overlay para que los desplegables no pierdan el contorno durante su relayout.
- **Web (ayuda de intervalos)**: el contorno de la tabla se ancla al viewport desplazable visible, que ocupa solo el espacio restante del panel y dibuja su borde hacia dentro para mantener visibles sus cuatro lados.
- **Web (ayuda de escalas)**: las anclas de tónica y digitación dibujan el contorno hacia dentro del panel para que sean visibles también los bordes izquierdo y derecho.
- **Móvil (ayuda)**: los resaltados de controles situados dentro de zonas desplazables se limitan ahora a la parte realmente visible; la tabla de Generación de intervalos ya no invade el panel inferior cuando necesita scroll y las anclas conservan una geometría estable durante el relayout del overlay.
- **Teclado**: al mostrar los nombres de las teclas, cada Do/C incluye ahora su número de octava (`Do4`, `C4`, etc.) en escritorio, web y móvil para facilitar la orientación en el registro.
- **Móvil (generación de intervalos)**: las zonas táctiles de las dos notas del pentagrama coinciden ahora con sus columnas melódicas visibles, permitiendo pulsar y reproducir también la segunda nota.
- **Móvil (teclado)**: el centrado inicial se aplica al terminar de restaurar la pantalla y cargar todos sus datos; al entrar en Generación de intervalos también se recalcula con el ancho real disponible, fijando C4 como referencia sin reutilizar el desplazamiento de Detección.
- **Ayuda**: el pentagrama de Generación de intervalos tiene una explicación propia en escritorio, web y móvil: muestra las notas elegidas en la tabla y permite previsualizarlas y resaltarlas en el instrumento.
- **Escritorio (ayuda)**: la fila Notas de Generación de intervalos deja de reutilizar “las dos últimas notas pulsadas” de Detección; sus ayudas de resultado e instrumento quedan alineadas con las equivalentes de web.
- **Móvil (ayuda)**: Generación de intervalos incorpora ayudas individuales para tónica, notas, nombre, semitonos y tabla, con los mismos textos que web; se omite únicamente Alternativos porque esa fila no existe en móvil.
- **Generación de intervalos**: el piano, la guitarra y la entrada MIDI reconocen las notas válidas del intervalo en cualquier octava y resaltan en azul su equivalente representado en el pentagrama, también en móvil; el aviso de nota incorrecta queda reservado para alturas ajenas al intervalo.
- **Generación de intervalos**: los controles de reproducción usan flechas izquierda/derecha coherentes en las tres plataformas y solo el último sentido elegido permanece resaltado en amarillo.
- **Web (preferencias)**: al recargar la aplicación se restaura el último modo utilizado; los valores guardados se validan y Detección sigue siendo el modo seguro por defecto.

- **Móvil (generación de intervalos)**: el selector adopta la tabla completa de categorías y semitonos de las otras plataformas; en tablet se reduce el ancho del pentagrama para dar más espacio a la cuadrícula y en pantallas estrechas puede desplazarse horizontalmente.

- **Móvil (generación de intervalos)**: los botones de reproducción ascendente y descendente se sitúan junto a los selectores de tónica y alteración para reducir la altura ocupada por los controles.

- **Intervalos (piano)**: las notas de los intervalos se identifican ahora mediante círculos sobre las teclas —verde para la nota inicial y amarillo para la segunda— en escritorio, web y móvil, evitando las etiquetas blancas separadas del teclado.

- **Móvil (generación de intervalos)**: añadido el modo para elegir tónica e intervalo por categoría teórica, reproducirlo en ambos sentidos y visualizarlo en pentagrama, piano o guitarra; el selector de modos adopta además el mismo orden que la web.

- **Escritorio (generación de intervalos)**: añadido un modo específico para elegir la tónica y generar intervalos desde una tabla por categoría y semitonos, con reproducción ascendente o descendente, representación en pentagrama y resaltado en el piano.

- **Escritorio (intervalos)**: los controles de reproducción ascendente y descendente reatacan las notas retenidas desde la primera pulsación, sin requerir un segundo intento para oírlas.

- **Escritorio (partitura)**: las notas de un mismo grupo de corcheas o semicorcheas comparten ahora dirección de plica y el grupo se corta al cambiar entre las claves de fa y sol, evitando barras diagonales incorrectas dentro del pentagrama o entre ambos pentagramas.

- **MIDIChords (landing)**: el hero muestra ahora la aplicación real, presenta primero el beneficio de comprender visualmente acordes, intervalos, escalas y armonía, identifica sus públicos principales y prioriza el acceso directo a la app web.
- **PianoPilot (landing)**: la portada presenta el producto real, limita claramente la compatibilidad al Roland FP-30X y añade una guía visible para USB MIDI, Bluetooth MIDI y controladores; las capturas servidas pasan de más de 13 MB en PNG a unos 167 KB en WebP.
- **Landings (accesibilidad)**: las galerías se navegan ahora con teclado mediante botones semánticos, los paneles de funciones exponen su estado, los diálogos anuncian apertura y cierre, el foco resulta visible y las animaciones respetan la preferencia de movimiento reducido.
- **Landings (SEO)**: añadidos Twitter Cards y datos estructurados `SoftwareApplication` específicos de MIDIChords y PianoPilot; una comprobación automática protege títulos, descripciones, Open Graph, imágenes dimensionadas, recursos locales y jerarquía de encabezados.
- **Landings (responsive)**: la navegación permanece disponible en pantallas pequeñas mediante una fila desplazable, los diálogos confinan el foco hasta cerrarse y los enlaces internos a la app web dejan de abrir pestañas nuevas de forma inesperada.
- **Landings (capturas)**: las galerías usan dos columnas apaisadas en escritorio y una en móvil, preservan la proporción de cada captura sin deformarla y MIDIChords incorpora una vista adicional del círculo de quintas.
- **MIDIChords (landing)**: la galería completa los siete flujos principales con capturas de detección de acordes, detección de intervalos, generación en piano y guitarra, escalas, círculo de quintas y metrónomo.
- **MIDIChords (landing)**: sustituidas todas las imágenes antiguas y mezcladas por la serie coherente de capturas apaisadas de iPad preparada para App Store, optimizada a WebP y reutilizada también en el hero.
- **Landings (capturas)**: reducido el espacio vertical de las galerías y normalizados tamaño, pie y altura de todas las tarjetas; cuando hay un número impar, la última captura conserva el mismo ancho y queda centrada.
- **Landings (capturas)**: eliminado el alto porcentual que hacía crecer artificialmente cada tarjeta y centraba la imagen dentro de una gran franja vacía; la proporción de la captura determina ahora directamente el alto del recuadro.
- **Landings (capturas)**: las miniaturas sobrescriben explícitamente con `height: auto` la altura intrínseca declarada para evitar que el navegador reserve 1050 píxeles CSS y centre la captura dentro de ese espacio.
- **Landings (SEO bilingüe)**: añadidas URLs alternas `?lang=en` y `?lang=es` con `hreflang`; cambiar de idioma conserva la variante en la URL y traduce también título, descripción, Open Graph y Twitter Cards.
- **Web (bundle)**: el constructor de Cloudflare Pages descubre y versiona ahora los JS/CSS de todos los HTML públicos, evitando que la infraestructura compartida de las landings quede fuera del fingerprint de caché.
- **Generación de acordes (guitarra)**: las variantes `add2`, `add4`, `madd2` y `madd4` disponen ahora de digitaciones concretas de cuatro notas; el mástil muestra solo las cuerdas de la variante seleccionada en lugar de marcar todas las posiciones posibles.
- **Generación de acordes (guitarra)**: al cambiar de digitación se reproduce inmediatamente el nuevo voicing, manteniendo sincronizados sonido, mástil y pentagrama.
- **Generación de acordes (guitarra)**: cambiar el tipo de acorde desde el selector reinicia siempre la digitación a la primera variante del nuevo acorde.
- **Generación de acordes (guitarra)**: cada tónica add2 ofrece las tres digitaciones de referencia verificadas; los mástiles llegan ahora hasta el traste 15 para mostrar también las posiciones más altas.
- **Generación de acordes (guitarra)**: cada tónica add4 ofrece sus dos digitaciones de referencia verificadas, incluidas las posiciones abiertas especiales de Mi y La.
- **Generación de acordes (guitarra)**: cada tónica menor add2 ofrece sus dos digitaciones de referencia verificadas, incluida la posición abierta especial de Mi menor add2.
- **Generación de acordes (guitarra)**: cada tónica menor add4 ofrece sus dos digitaciones de referencia y cada add9 sus tres posiciones verificadas, incluidas las digitaciones abiertas especiales.
- **Generación de acordes (guitarra)**: las tríadas mayores, menores, disminuidas y aumentadas usan ya las posiciones y dedos del catálogo público actual para las doce tónicas; una nueva utilidad audita los tipos compartidos y separa explícitamente las variantes propias sin referencia directa.
- **Generación de acordes (guitarra)**: los power chords y acordes suspendidos `sus2` y `sus4` quedan sincronizados con sus digitaciones de referencia para las doce tónicas.
- **Generación de acordes (guitarra)**: completada la auditoría de la familia de notas añadidas; `madd9` corrige trastes y dedos en las ocho tónicas que todavía divergían, mientras `add2`, `add4`, `madd2`, `madd4` y `add9` conservan sus posiciones ya verificadas.
- **Generación de acordes (guitarra)**: los acordes `6`, `6add9` y `m6` usan las digitaciones actuales de referencia para todas las tónicas; `m6add9` permanece como variante propia sin equivalente exacto.
- **Generación de acordes (guitarra)**: las séptimas dominantes `7`, `7sus4`, `7#5`, `7b5`, `7#9` y `7b9` quedan sincronizadas con la referencia en las doce tónicas; las alteraciones dobles se conservan como variantes propias.
- **Generación de acordes (guitarra)**: las extensiones dominantes `9`, `9#5`, `9b5`, `11`, `13`, `13b9` y `13#11` quedan auditadas y sincronizadas para todas las tónicas; `11b9` se mantiene como variante propia.
- **Generación de acordes (guitarra)**: las extensiones mayores `maj7`, `maj7#5`, `maj9`, `maj11` y `maj13` usan ya las digitaciones públicas actuales en todas las tónicas; `maj7b5`, `maj9#11` y `maj13#11` permanecen como variantes propias.
- **Generación de acordes (guitarra)**: las familias menores `m7`, `m9`, `m11`, `m13`, `mMaj7`, `mMaj9`, `dim7` y `m7b5` completan la sincronización del catálogo compartido; los 42 tipos con equivalente exacto quedan auditados en las doce tónicas y los 12 tipos propios permanecen separados.

- **Escritorio (mantenimiento)**: añadido un smoke test Qt aislado de audio, MIDI y configuración que fija widgets públicos, jerarquía y cambios de modo; la barra superior, la carcasa central y las raíces de cada modo se trasladaron a builders dedicados protegidos por ese contrato.

- **Escritorio (rendimiento)**: el selector principal cierra antes de aplicar el cambio de modo, se evitan actualizaciones visuales duplicadas y las digitaciones de guitarra se calculan solo al mostrar la guitarra; cambiar de tónica y reproducir acordes desde el piano deja de quedar bloqueado por ese cálculo.

- **Escritorio (integración)**: definida explícitamente la identidad interna de producto en Qt para que títulos y menús propios no hereden el nombre del intérprete.

- **Escritorio (partitura)**: las barras secundarias parciales de semicorchea siguen ahora la pendiente de la barra principal en lugar de dibujarse siempre horizontales.

- **Móvil (partitura)**: las notas de un mismo grupo de corcheas o semicorcheas comparten dirección de plica, evitando barras diagonales que atravesaban las cabezas cuando las notas quedaban a lados opuestos del centro del pentagrama.

- **Partitura / interacción**: al pulsar notas alteradas en Generación de acordes o Círculo de quintas, el símbolo correspondiente de la armadura se resalta junto con la nota en escritorio, web y móvil, igual que en Escalas.

- **Móvil (mantenimiento)**: separado el catálogo contextual, las anclas, la selección y la geometría del tour de ayuda a una extensión privada `part`, reduciendo en más de mil líneas el contexto de `main.dart` y conservando estado, callbacks y animación existentes.

- **Web (mantenimiento)**: trasladados al módulo del círculo de quintas el hit-testing de sectores/anillos, la selección diatónica y la geometría del acorde resaltado; modo y tónica son ahora entradas explícitas y las pruebas cubren clics interiores, exteriores, fuera del anillo y bandas mayor/menor/disminuida.

- **Web (mantenimiento)**: añadido un ciclo de vida inyectable para listeners y temporizadores con DOM y reloj falsos; la coordinación global de ventana, visibilidad y desmontaje está separada de `bindEvents` y se registra y libera mediante ese contrato.

- **Móvil (mantenimiento)**: aislados el bloqueo de pantalla nativo y su temporizador renovable de actividad MIDI detrás de un adaptador probado; el widget ya no coordina directamente `WakelockPlus` y se verifican cancelación, renovación y desmontaje idempotente.

- **Móvil (mantenimiento)**: centralizadas las claves, valores predeterminados, validación y persistencia de preferencias en un repositorio con puerto sustituible; las pruebas cubren carga inválida, guardado completo y eliminación de opciones obsoletas.

- **Móvil (mantenimiento)**: extraída la propiedad de las suscripciones MIDI de datos y cambios de conexión a un ciclo de vida dedicado; el estado recibe bytes independientes del plugin y las pruebas fijan alta única, reenvío y cancelación idempotente.

- **Web (partitura / mantenimiento)**: extraídas y probadas la elección de plica común y la geometría de barras primarias y secundarias; los grupos barrados conservan una dirección coherente y las barras de semicorchea permanecen paralelas.

- **Web (mantenimiento)**: extraídas la autocorrelación del afinador y las conversiones frecuencia/MIDI a un módulo puro, con pruebas de tono sintético decreciente, silencio, entradas inválidas, afinación de concierto y recorrido MIDI→frecuencia→MIDI.

- **Web (mantenimiento)**: extraídas las envolventes de piano/guitarra y la liberación segura de voces retenidas a un módulo probado con nodos Web Audio falsos, eliminando dos implementaciones duplicadas y cubriendo también fuentes ya detenidas.

- **Web (mantenimiento)**: encapsuladas la descarga, decodificación y caché de samples en un cargador inyectable; las pruebas verifican una sola carga concurrente, normalización exclusiva del metrónomo y conservación de resultados parciales ante fallos de red.

- **Web (mantenimiento)**: extraídos el catálogo de samples y los cálculos puros de selección de raíz, transposición y normalización de buffers; la nueva suite usa `AudioContext` y buffers falsos sin alterar el desbloqueo por gesto, la caché ni el ciclo de reproducción del navegador.

- **Web (mantenimiento)**: encapsulada la salida Web MIDI en un controlador inyectable y probado con dispositivo falso, cubriendo note on/off temporizado, notas retenidas, liberación total, velocidad, ausencia de salida y Program Change de piano/guitarra; el perfil web descubre ahora automáticamente todas las suites `*.test.js`.

- **Web (mantenimiento)**: extraídos filtro, alias, normalización por octavas y correspondencia MIDI-etiqueta de escalas a un módulo puro con pruebas de deduplicación, transposición inicial y nombres localizados.

- **Web (mantenimiento)**: extraída la resolución de armaduras mayores, menores y modales a un módulo puro, con pruebas para tonalidades con sostenidos/bemoles, empates enarmónicos, relativos modales y sufijos menores.

- **Web (mantenimiento)**: extraídos los patrones documentados y la resolución de digitaciones de piano a un módulo puro, con pruebas para acordes, escalas mayores, cromáticas, cruces de dedo y ausencia explícita de fallback cuando no existe referencia.

- **Web (mantenimiento)**: extraídos nombres, cálculo y melodías mnemotécnicas de intervalos a un módulo puro; las pruebas cubren unísono, octava, dirección, traducciones, intervalos consecutivos y alineación de silencios con duraciones.

- **Web (mantenimiento)**: extraídas la teoría diatónica y la geometría pura del círculo de quintas a un módulo sin DOM ni estado, con pruebas directas de orden, armaduras, relativos, grados y tríadas mayores y menores.

- **Web (mantenimiento)**: extraídas las tablas y conversiones puras de notación musical —nombres de notas, tónicas, alteraciones, armaduras y pitch classes— a un módulo con pruebas JavaScript directas.

- **Web (mantenimiento)**: el build, la comprobación de sintaxis y el chequeo de salud descubren ahora automáticamente todos los JS/CSS locales enlazados desde `app.html`; añadir otro módulo ya no requiere mantener listas paralelas de assets en varios scripts Python.

- **Web (mantenimiento)**: extraída la configuración de ayuda contextual por modo a un módulo declarativo; la suite JavaScript comprueba que todos los callouts tengan selector y texto disponible en español e inglés, y el bundle y la salud de producción validan el nuevo asset.

- **Web (mantenimiento)**: añadida una suite JavaScript nativa, sin dependencias npm, que ejecuta los catálogos extraídos y comprueba paridad ES/EN, cobertura única de las 52 variantes, textos de inversiones e inmutabilidad de sus puntos de entrada dentro del perfil web de CI.

- **Web (mantenimiento)**: separados los textos generales de interfaz ES/EN en un catálogo dedicado con prueba de paridad de claves; el build y el chequeo de producción versionan y validan también este script antes de cargar la SPA.

- **Web (mantenimiento)**: extraídos de la SPA el catálogo bilingüe de ayuda teórica, la agrupación de variantes y los textos de inversiones a un script dedicado y probado; el bundle y el chequeo de producción versionan y validan también esta nueva dependencia.

- **Móvil (mantenimiento)**: separados los constructores de las páginas de Detección, Generación, Círculo de quintas, Escalas, Intervalos, Metrónomo y Afinador en una extensión privada dedicada, reduciendo el contexto de `main.dart` sin duplicar el estado de la pantalla.

- **Móvil (mantenimiento)**: extraído a un módulo puro y probado el cálculo de tamaños, proporción y scroll del teclado de piano, separándolo de la construcción de widgets en `main.dart`.

- **Móvil (mantenimiento)**: movidos los painters privados de pentagrama, metrónomo y afinador desde `main.dart` a un `part` dedicado, conservando sus símbolos y comportamiento mientras se reduce el tamaño de la pantalla principal.

- **Móvil (mantenimiento)**: extraídas de `main.dart` la generación y detección local de acordes, inversiones, spelling y generación de escalas a un servicio puro con tests directos de comportamiento.

- **Móvil (mantenimiento)**: extraído de `main.dart` el catálogo declarativo de acordes, escalas, traducciones e inversiones a un módulo puro con tests de integridad, reduciendo el contexto necesario para modificar la UI móvil.

- **Mantenimiento / CI**: añadido un comando unificado de verificación con perfiles para Python, web y Flutter, junto con un workflow de GitHub Actions que ejecuta tests, análisis estático, sintaxis JavaScript y build web en cada pull request; saneados además los avisos previos del analyzer de Flutter para que el nuevo control parta en verde.

### Corregido

- **Escritorio (generación de intervalos)**: añadido el selector Piano/Guitarra y la representación del intervalo sobre el diapasón, con la nota inicial en verde, la segunda en amarillo y la nota reproducida en azul.

- **Móvil (pentagrama de intervalos)**: las dos notas se distribuyen ahora en columnas melódicas separadas para que intervalos cercanos, como la tercera menor, no parezcan un acorde con las cabezas apiladas.

- **Móvil (preferencias)**: al volver a abrir la aplicación se restaura también Generación de intervalos cuando fue la última pantalla utilizada, en lugar de descartarla por pertenecer al modo añadido más recientemente.

- **Escritorio (generación de intervalos)**: la primera columna de la tabla actualiza ahora sus categorías al idioma configurado, incluso cuando el panel ya se había construido en otro idioma.

- **Ayuda contextual**: las explicaciones del piano y la guitarra en los modos de generación los presentan ahora como vistas del resultado y remiten a los botones de reproducción, sin describirlos incorrectamente como instrumentos interactivos.

- **Web (generación de intervalos)**: el piano y la guitarra reservan ahora una columna real para los botones de instrumento, evitando que el contenido se extienda por debajo o se solape con ellos.

- **Escritorio (generación de intervalos)**: las categorías de la tabla respetan ahora el idioma configurado y muestran Diminished, Minor, Major, Perfect y Augmented en inglés.

- **Escritorio (generación de intervalos)**: al pulsar una celda de la tabla se inicia una sola secuencia de reproducción; la primera nota ya no se reataca dos veces rápidamente por la propagación duplicada del clic entre la etiqueta y su contenedor.

- **Web (generación / círculo de quintas)**: el botón ▶ vuelve a resaltar durante la reproducción las teclas exactas del piano y las posiciones del acorde sobre la guitarra; instrumento y pentagrama se repintan al iniciar, sustituir y limpiar el resaltado tanto con audio como con MIDI out.

- **Móvil (piano / scroll por modo)**: Generación, Círculo y Escalas solo se centran en su primera apertura de la sesión; al cambiar de modo o alternar con la guitarra se guarda y restaura el último desplazamiento propio de cada modo.

- **Móvil (generación / guitarra)**: al tocar una nota del acorde en el pentagrama, la posición correspondiente vuelve a resaltarse temporalmente en el diapasón, igual que ya ocurría en el piano.

- **Móvil (generación / piano)**: al entrar en Generación de acordes o volver desde la guitarra, el teclado se recentra en el Do de la mano derecha en lugar de conservar el desplazamiento anterior hacia la mano izquierda.

- **Móvil (pentagrama interactivo)**: la reproducción al tocar una nota del pentagrama se extiende de Escalas a Detección, Generación de acordes, Círculo de quintas e Intervalos; en los modos de acordes la selección se refleja también en el instrumento.

- **Móvil (escalas / guitarra)**: el diapasón adopta la misma jerarquía de colores que escritorio: nota activa azul, tónica inicial naranja, demás tónicas amarillas y el resto de grados blancos.

- **Móvil (escalas / pentagrama)**: las notas del pentagrama vuelven a responder al toque, reproducen su sonido y reflejan temporalmente la selección en el piano o la guitarra.

- **Escritorio (escalas / piano)**: al pulsar por segunda vez una nota retenida, el nuevo ataque vuelve a resaltarse correctamente en el piano además de sonar.

- **Escritorio (escalas / piano)**: una nota retenida en audio tras soltar la tecla vuelve a producir un ataque al pulsar de nuevo esa misma tecla; ya no se reactiva únicamente el resaltado sin que suene.

- **Móvil (escalas)**: al soltar una nota pulsada manualmente deja de mantenerse como selección actual en el piano, la guitarra, el pentagrama y la armadura. La liberación MIDI también limpia correctamente la selección aunque la nota mostrada esté trasladada de octava.

- **Escritorio (escalas / piano)**: al soltar una tecla, deja de resaltarse inmediatamente en el piano, el pentagrama y la armadura. La retención de audio existente hasta la siguiente pulsación ya no se confunde con el estado visual de una tecla físicamente pulsada; el pedal de sustain sí conserva el resaltado mientras corresponda.

- **Escritorio (ayuda de acordes)**: el diálogo teórico ajusta ahora su altura al contenido, elimina el gran espacio vacío inferior, recupera los márgenes alrededor del contenido y coloca **Cerrar** debajo del texto, alineado en la parte inferior derecha.

- **Móvil (Flutter, cierre/tests)**: la limpieza de MIDI durante `dispose()` ya no intenta ejecutar `setState` ni relanzar detección mientras el árbol de widgets se está desmontando. Se corrige además el import obsoleto del smoke test y se fija un viewport horizontal representativo, de modo que la suite Flutter completa vuelve a ejecutarse correctamente.

- **Escritorio (Qt)**: en **Metrónomo**, los botones +/- de **Minutos** y **Segundos** del temporizador no funcionaban de forma persistente: el número mostrado cambiaba al pulsar, pero cualquier otro refresco de la UI (volumen, BPM, compás, activar/desactivar el temporizador...) lo devolvía al valor anterior. Causa: `Spinbox` en el shim Qt (`midichords/qt/ttk_compat.py`) ignoraba el parámetro `command` (y `increment`) del constructor — las flechas nativas de Qt cambiaban el valor mostrado pero nunca avisaban al resto de la app, así que `self.metronome_timer_minutes`/`seconds` (los valores reales que usa el temporizador) nunca se actualizaban. Ahora `command` se conecta a `valueChanged` y se dispara en cada cambio, igual que en Tk.

- **Escritorio (Qt)**: en **Metrónomo**, tras el fix anterior seguía sin poder pulsarse el botón ▲ de Minutos/Segundos: el clic caía sobre el número (lo seleccionaba, como un doble clic de texto) en vez de incrementar. Causa: el estilo nativo **"windows11"** de Qt calcula mal la geometría de los botones +/- de `QSpinBox` — el área del campo de texto se solapa con la del botón ▲ (confirmado midiendo `subControlRect`: solapamiento de ~30px independientemente del ancho del widget), así que los clics en la posición visual de la flecha en realidad activan el campo de texto. Probar el estilo Fusion en su lugar arreglaba el clic pero introducía un problema nuevo: la paleta oscura se perdía en algún punto posterior del ciclo de vida del widget (flechas negras sobre negro, invisibles) y no se consiguió fijar de forma fiable con `QPalette` ni `QSS`. **Solución final**: sustituir el `QSpinBox` de Minutos/Segundos por los mismos botones −/+ redondos (canvas dibujado a mano) que ya usan Volumen/Tempo/Pulsos en el mismo panel — evita el bug de estilo nativo por completo en vez de perseguirlo.

- **Escritorio (Qt)**: en **Metrónomo**, los checkboxes **Temporizador** y **Acentuar inicio de compás**, al marcarse, no mostraban el recuadro alrededor del check (solo el símbolo ✓ flotando sin caja) — con el estilo nativo "windows11" y también con Fusion; ni `QPalette` ni QSS con `border`/`background-color` explícitos en `QCheckBox::indicator:checked` lo arreglaban. Se sustituyen ambos por canvas dibujados a mano (mismo patrón que los botones −/+), con caja completa en ambos estados (marcado en color de acento, sin marcar con el borde neutro habitual).

- **Escritorio (Windows)**: al arrancar, la barra de tareas mostraba el icono genérico de `python.exe` en vez del logo de la app (la barra de título de la ventana ya usaba el logo correcto). Causa: sin un **AppUserModelID** propio, Windows usa el icono del ejecutable para el botón de la barra de tareas aunque la ventana ya tenga su icono fijado con `setWindowIcon`. Se fija `SetCurrentProcessExplicitAppUserModelID("MIDIChords.Desktop")` al arrancar, antes de crear la `QApplication`/ventana.

- **Escritorio (Qt)**: en **Configuración**, los radio buttons de **Idioma** y **Salida de sonido** no mostraban el punto de la opción marcada, y el checkbox **Mostrar nombres de notas en teclado** tampoco mostraba el recuadro al marcarse — mismo bug de estilo nativo "windows11" que en el temporizador del Metrónomo (ver más arriba). Se sustituyen por los mismos canvas dibujados a mano: nuevo helper `OverlaysMixin._build_radio_row()` / `_build_checkbox_row()`, reutilizando `_draw_radio_indicator()` / `_draw_metronome_checkbox()` de `metronome_mixin.py`. La sincronización reactiva de "Salida de sonido" (se cambia solo a MIDI al conectar una entrada MIDI) se mantiene vía `trace_add` sobre el mismo `StringVar`, sin el `setChecked()` manual que hacía falta con `ttk.Radiobutton`.

- **Escritorio (Qt)**: en **Escalas**, los radio buttons de **Digitación** ("Sin", "Mano Izquierda", "Mano Derecha") se veían con un color oscuro que parecía deshabilitado incluso con **piano** seleccionado (donde sí están activos y se pueden pulsar). Causa: `Radiobutton` en el shim Qt (`midichords/qt/tk_compat.py`) capturaba `fg`/`font`/`cursor` del constructor en `**kwargs` pero nunca los aplicaba al `QRadioButton` interno, que se quedaba con la paleta por defecto de Qt (texto oscuro) en vez del color claro de texto de la app. Ahora se aplican en el constructor y en `configure()`, con una regla `:disabled` explícita para no perder el atenuado nativo cuando de verdad está deshabilitado (modo guitarra).

- **Escritorio (Qt, pendiente de verificar en macOS — ver `TODO_MACOS_VERIFICATION.md`)**: en modo **Detección de Acordes**, el texto de ayuda del panel derecho ("Pulsa notas en piano/guitarra...") se recortaba en vez de ajustarse a 2 líneas. Causa: el cálculo de `wraplength` en `ui_mixin.py` (`_refresh_right_panel_wraplengths`) usaba por error el ancho del panel izquierdo (`staff_canvas`) en lugar del propio panel derecho (`chord_panel`); se añadieron `winfo_width()`/`winfo_height()` (getters puros) a la clase base `Widget` del shim Qt (`midichords/qt/tk_compat.py`) para que la lectura del ancho del panel derecho funcione.

- **Escritorio (Qt)**: mismo recorte de texto que en Detección de Acordes, pero en **Detección de Intervalos** ("Pulsa dos notas..."). El label tenía un `wraplength=800` fijo, creado bajo demanda al entrar por primera vez en el modo, sin ningún mecanismo que lo recalculara. Ahora se registra en `_refresh_right_panel_wraplengths` (igual que `detection_help_label`) y se refresca nada más crearse el panel.

- **Escritorio (Qt)**: en modo **Detección de Intervalos**, el panel del pentagrama ya no muestra el texto de ayuda "Mantén Shift para mantener las teclas pulsadas" (pensado para Detección de Acordes; Shift no aplica al modo de intervalos).

- **Escritorio (Qt, pendiente de verificar en macOS)**: en modo **Generación de Acordes**, las filas de **Notas** e **Intervalos** podían recortarse por abajo cuando el texto necesitaba más líneas de las que caben en el alto fijo (160px) del bloque de resultado — más probable en macOS, donde las fuentes del sistema (Avenir Next/SF Pro) son más altas que en Windows. Ahora el alto del bloque crece dinámicamente (`_refresh_generation_result_height`, enganchado a los `StringVar` de notas/intervalos vía `trace_add`) según el alto real que pide el contenido (`winfo_reqheight`, nuevo en la clase base `Widget` del shim Qt, basado en `sizeHint()`).

- **Escritorio (Qt, reportado en macOS)**: en modo **Círculo de quintas**, el círculo no cabía en el panel derecho y el texto de los acordes del anillo interior se salía de sus sectores (más notorio con la vista de guitarra activa). Causa: `circle_canvas` se creaba con `width=480, height=480`, que en el shim Qt se traduce en un **tamaño mínimo forzado** — el panel derecho es a menudo más estrecho/bajo que 480px, así que el canvas se salía de sus límites, y como las fuentes/radios del dibujo se calculan proporcionalmente al ancho reportado (forzado a 480 aunque el espacio real fuera menor), el texto salía sobredimensionado. Se reduce a `width=260, height=260` (mismo suelo que ya usaba `_circle_redraw_canvas` como mínimo), dejando que el canvas se ajuste al espacio real disponible.

- **Escritorio (Qt)**: en el **Círculo de quintas**, además del fix de tamaño del canvas, algunas etiquetas de acorde menor largas (p. ej. "Sol#m", "La#m", "Re#m") podían salirse de su sector porque el tamaño de fuente se calculaba de forma proporcional al ancho del canvas sin tener en cuenta la longitud del texto — el anillo menor tiene menos ancho disponible por sector que el mayor al mismo ángulo, y el sufijo "m" añade un carácter más. Ahora cada etiqueta (nombre mayor, menor, y los casos especiales de la 7ª disminuida/ii°) calcula su propio tamaño de fuente encogido si no cabe en el ancho disponible de su sector (`_fit_font_size_for_slice` en `midichords/ui/circle_of_fifths.py`). El primer intento estimaba el ancho por número de caracteres (heurístico pensado para texto en cursiva, no en **negrita** como estas etiquetas) y seguía sin ser suficiente; se cambió a medir el ancho real con `QFontMetrics`.

- **Escritorio (escalas)**: al arrancar, el selector de **Digitación** vuelve a marcar la última mano elegida en la configuración (`Sin`, `Mano I.` o `Mano D.`) en lugar de quedarse visualmente en `Sin`.

- **Escritorio (escalas)**: al arrancar con digitación activa o al cambiar la mano de digitación, el panel inferior del piano reserva solo la altura necesaria para las bandas de dedos y para la barra horizontal; muestra también la franja descendente sin dejar un hueco grande ni quedar recortada por el scroll.

- **Escritorio (escalas)**: las digitaciones de piano vuelven a mostrarse en escalas básicas que no tenían tabla en el core de escritorio, como **Pentatónica mayor**, **Pentatónica menor / blues**, **Tono entero** y **Cromática**.

- **Escritorio (configuración)**: los combos de **Entrada MIDI** y **Salida de audio** muestran ahora `<no seleccionado>` como primera opción visible, también tras refrescar dispositivos, en lugar de una entrada en blanco.

- **Escritorio (configuración)**: la ventana de ajustes ya no usa una geometría fija; se ajusta al tamaño real de sus controles, queda bloqueada contra redimensionado manual y muestra **Guardar** y **Cancelar** como botones separados con recuadro redondeado.

- **Escritorio (configuración)**: los selectores de **Sonido de piano** y **Sonido de guitarra** usan el mismo estilo de combo que **Entrada MIDI** y **Salida de audio**.

- **Escritorio (Qt)**: los desplegables de los combos se abren debajo del control, con el mismo ancho y bordes redondeados, en lugar de aparecer como una caja rectangular sobre el selector.

- **Web (desarrollo local)**: eliminadas las configuraciones obsoletas de VS Code **HTTPS + Backend**, el servidor proxy `serve_https.py` y la guía `HTTPS_SETUP.md`. El flujo local queda unificado en `python launch.py web`, con nueva opción `--https` para arrancar el mismo Worker con HTTPS nativo de Wrangler.

- **Web (MIDI + audio)**: si la entrada MIDI se reactiva automáticamente antes de cualquier gesto del usuario, las notas MIDI ya no intentan arrancar WebAudio hasta que Chrome permita reanudar el `AudioContext`; la detección visual sigue funcionando y el audio se desbloquea con el primer clic o tecla en la página.

- **Web (MIDI)**: el arranque ya no muestra siempre el modal de activación. Si el navegador conserva el permiso MIDI y el usuario no lo había desactivado, la entrada MIDI se reactiva automáticamente; también se respeta la última salida elegida (`Audio` / `MIDI out`) desde `localStorage`.

- **Web (front page)**: la landing prioriza ahora la **detección de intervalos** en metadatos, hero y tarjeta de la app web; se elimina la referencia visible al **afinador** en la franja de features y textos promocionales.

- **Web (detección de intervalos)**: ajustadas varias melodías mnemotécnicas (`Tiburón`, `Smoke on the Water`, `When the Saints Go Marching In`, `Here Comes the Bride`, `Maria`, `Star Wars`, `Love Story`, `My Way`, `Somewhere`, `Take On Me` y `Somewhere Over the Rainbow`) con nuevas transcripciones, anacrusas, silencios, tresillos, tempos específicos y control por melodía de ligadura previa o límite de resaltado. El pentagrama permite además mostrar la melodía completa, acentos y reproducir/resaltar temporalmente una nota concreta al pulsarla.

- **Escritorio (Qt)**: el selector **Diestro / Zurdo** usa los mismos parámetros que el `<select id="guitarHandedness">` de la web (`style.css`: altura **38px**, radio **10px**, fondo **#17273a**, borde **#4a6180**, texto **#e8effa**, negrita). La flecha se pinta en **`HandednessComboBox.paintEvent`** con **`assets/ui/combo_arrow_down.png`** (QSS `image:` en `::down-arrow` no es fiable en macOS).

- **Escritorio (Qt)**: fila **Acorde:** + nombre (generación / círculo) — de nuevo **dos** `tk.Label`; el marco usa **borde + padding** en **una** hoja QSS (`setStyleSheet` en el `Frame`, sin `highlightthickness`) para que el trazo no quede tapado y el texto no se salga. El **`QLabel`** conserva **`fg`** al redimensionar (`configure(wraplength=…)`), para que el nombre del acorde no vuelva a **blanco** y use el color **accent** (dorado del botón Piano).

- **Escritorio (generación / círculo de quintas, piano)**: al pulsar **play**, el audio solo sonaba las notas de la **clave de sol**; ahora incluye también la **clave de fa** (misma lógica que el pentagrama: una octava abajo).

- **Web (círculo de quintas)**: la armadura del pentagrama seguía la **raíz del acorde diatónico** (p. ej. tras Mayús+clic); ahora usa la **tonalidad del anillo** (`circleTonicPc` + modo mayor/menor), alineado con la teoría y con Flutter. Pista breve en el staff; al alternar **piano/guitarra** se redibuja el pentagrama sin esperar a tocar notas.

- **Web (pentagrama)**: las claves de sol y fa recuperan el mismo margen que en escalas/generación; las armaduras empiezan más a la derecha para evitar solapamientos sin sacar las claves del pentagrama.

- **Web (escalas)**: el selector de octavas en piano añade la segunda octava hacia la izquierda (grave) y reserva la tercera para extender hacia la derecha (agudo).

- **Escritorio (Windows, audio)**: al pulsar teclas del piano, la guitarra, los botones de reproducir o el círculo de quintas, el sonido tardaba en salir (lag perceptible). Causa: `PianoAudioEngine.start()` usaba siempre `blocksize=1024, latency="high"` (ajuste pensado para CoreAudio en macOS); en Windows, el host API por defecto de PortAudio es **MME**, que trata los hints de texto (`"high"`/`"low"`) de forma muy laxa y acababa negociando ~213ms de latencia real. Pasar un valor numérico de latencia en segundos hace que MME lo respete de forma mucho más literal: se probó `128/0.01` (~10.7ms reales) pero producía cortes de audio audibles (underruns) bajo carga pesada (acordes de muchas notas con `grand_sample`); el valor final `blocksize=512, latency=0.03` mide ~32ms reales y no mostró ningún underrun en pruebas de estrés repetidas (acordes de 13 notas simultáneas, reintentos rápidos). macOS no se ve afectado y mantiene su ajuste original.

- **Web (escalas)**: los círculos de notas sobre el piano usan ahora la escritura diatónica de la escala generada (por ejemplo, `Si#` en Sol#) en lugar del nombre cromático enarmónico (`Do`).

- **Web (escalas)**: la lista de notas del panel de resultado ya no muestra el número de octava al final de cada nota.

- **Detección / Generación / Escalas (escritorio y web)**: los intervalos ahora se muestran de forma incremental (distancias entre notas consecutivas) en lugar de acumulativa desde la raíz, con base siempre en 0. Ejemplo: `0 +4 +3` (Do, +4 semitonos a Mi, +3 semitonos a Sol) en lugar de `60 +4 +7`. Más intuitivo y educativo para teoría musical.

- **Web (escalas)**: revisadas las digitaciones de piano con tablas documentadas para escalas mayores, menores naturales, armónicas, melódicas, pentatónicas, cromática y tono entero. **Blues Pentatonic** usa la digitación de pentatónica menor (su patrón real en la app) y se eliminan las digitaciones genéricas sin referencia para modos/exóticas o blues mayor. **Blues menor** solo muestra digitación cuando hay referencia documentada.

- **Web (CI)**: Tras **`wrangler pages deploy`**, el edge puede tardar en aplicar **`_worker.js`** y **`_routes.json`** en el dominio personalizado (`/api/meta` en **404** vacío hasta entonces). El workflow **Deploy Cloudflare (Production)** espera **120 s** antes del smoke test (y **120 s** tras un redeploy de retry); **web-production-health** espera **120 s** post-deploy y **120 s** tras autocuración antes del segundo chequeo.

### Android (Google Play — prueba cerrada)

- **1.0.1 (7)**: App Bundle de release; `versionCode` **7** en `pubspec.yaml` para **Google Play** (incluye wakelock renovado con MIDI en detección y resto de cambios recientes en `main`).
- **1.0.1 (6)**: `versionCode` **6** para prueba cerrada (el **5** ya estaba usado en la consola).

### Móvil (Flutter)

- **`wakelock_plus`**: en **detección** con **MIDI On**, cada **note on/off** renueva una ventana de **3 minutos** sin reposo de pantalla (equivalente práctico a reiniciar el temporizador de inactividad mientras tocas); se cancela al salir de detección, desactivar MIDI o cerrar la app.

### Escritorio / Web (MIDI detección)

- **Escritorio (Tk)**: módulo **`midichords/core/midi_idle_inhibit.py`** — cada nota MIDI en **detección** renueva **~3 min** sin apagar pantalla / suspender (Windows: `SetThreadExecutionState`; macOS: `caffeinate -di`). Se cancela al cambiar de modo fuera de detección o al cerrar.
- **Web**: **Screen Wake Lock API** en **detección** con MIDI activo (HTTPS/localhost); misma ventana de **3 min** renovada con cada note on/off; al cambiar de modo o desactivar MIDI se libera; al volver a la pestaña se reintenta si aún aplica.

### Añadido

- **Todas las plataformas (escalas / pentagrama)**: al pulsar manualmente una nota alterada o alcanzarla durante la reproducción con **▶**, el sostenido o bemol correspondiente se resalta también en la armadura, tanto en clave de sol como en clave de fa. Escritorio admite además varias alteraciones resaltadas simultáneamente al tocar varias notas por MIDI.

- **Todas las plataformas (detección de acordes)**: nuevo botón **?** inmediatamente a la derecha de **Reproducir**. Cuando se reconoce un acorde, abre la misma ayuda teórica disponible en Generación, con su fórmula, explicación y la descripción de la posición fundamental o inversión detectada.

- **Web, escritorio (Qt) y móvil (Flutter; generación de acordes)**: nuevo botón **?** a la derecha de **play** que abre una ayuda teórica específica para la variante seleccionada. El diálogo muestra su fórmula interválica y una explicación en español o inglés para las 52 variantes disponibles; un segundo párrafo dinámico describe la posición fundamental o inversión seleccionada, identificando correctamente el grado que queda en el bajo incluso en acordes suspendidos, alterados y extendidos. El selector organiza todas las variantes mediante cabeceras no seleccionables siguiendo la clasificación de AutoChords (**Tríadas, Séptimas, Sextas, Add y Extensiones**) y añade **Dominantes alterados** y **Extensiones alteradas** para clasificar las 20 variantes propias que no aparecen en esa página sin perder ninguna. Escritorio y móvil consumen el mismo catálogo de teoría versionado en `assets/chord_variant_theory.json` (incluido como asset Flutter) y una prueba impide que ambas copias diverjan.

- **Repo / comunicación**: nuevo documento **`docs/product/competitions.md`** para centralizar candidaturas, borradores y materiales de premios/concursos de FreeMIDIChords.

- **Web**: nuevo modo **Detección de intervalos** en la SPA (`apps/web/static/app.js`, `app.html`, `style.css`) con captura de las dos últimas notas desde teclado o MIDI, nombre del intervalo, semitonos, reproducción ascendente/descendente y modo **Recordar** con melodías mnemotécnicas dibujadas y reproducidas en el pentagrama. La landing (`apps/web/index.html`) y la documentación (`apps/web/README.md`) reflejan la nueva funcionalidad.

- **Móvil (Flutter)**: pestaña **Círculo de quintas** (`circle_of_fifths.dart`) — canvas, grados diatónicos y armadura del pentagrama alineados con la web; tour de ayuda; reordenación de pestañas (Escalas y Metrónomo a índices posteriores cuando el afinador está activo).

- **Escritorio (Tk)**: modo **Círculo de quintas** (`circle_fifths_mixin`, `ui/circle_of_fifths`) — pestaña y canvas alineados con web/móvil; integración en `main_app` y pentagrama.

- **Web (deploy)**: `prepare_web_pages_dist` en **`launch.py`** y script **`scripts/build_web_pages_dist.py`** — en el bundle de Pages, **`app.js`** y **`style.css`** pasan a nombres con **hash de contenido** y se actualiza **`index.html`**, para que el dominio personalizado no siga sirviendo JS/CSS viejos cacheados en `/static/app.js` ignorando cabeceras.
- **CI / empaquetado**: workflow **Build Installers** — `workflow_dispatch` con **`checkout_ref`** y **`msix_revision`** (cuarto segmento de la versión MSIX para reenvíos a Microsoft Store sin cambiar el semver del tag); el job Debian calcula la versión del `.deb` desde el mismo tag/ref que Windows/macOS en dispatch.
- **Web (CI)**: workflow **`web-production-health.yml`** (cron horario, UTC) ejecuta **`scripts/check_production_web_health.py`** contra producción: HTML, CSS, `app.js` y **`GET /api/meta`**. El script resume el patrón **404 en `/static/*?v=…` con OK sin query** con un mensaje accionable. Si **falla el primer chequeo**, el workflow intenta **autocuración**: construye el bundle (`build_web_pages_dist.py`), **`wrangler pages deploy`** desde **`main`** (secrets **`CLOUDFLARE_API_TOKEN`**, **`CLOUDFLARE_ACCOUNT_ID`**, variable **`CLOUDFLARE_PAGES_PROJECT`**), espera propagación y **vuelve a ejecutar** el chequeo. Tras cualquier fallo del 1er chequeo, correo vía **Resend** con asunto explícito: **`[RESUELTO]`** si el 2º chequeo pasa, **`[ACCIÓN REQUERIDA]`** si bundle, deploy o 2º chequeo fallan (`RESEND_API_KEY`; destinatario por defecto **aortega98@gmail.com**, **`WEB_HEALTH_ALERT_TO`**). Aviso si falta **`RESEND_API_KEY`**. El paso de correo usa **`continue-on-error`** e imprime errores de Resend en el log. **`User-Agent`** en la API Resend. Envío en **`scripts/send_resend_health_alert.py`** (`--mail-kind resolved|action_required`, opcional **`--second-log`**). Ver `apps/web/README.md`.
- **Web (CI)**: **`web-production-health`** también se dispara al **terminar con éxito** el workflow **Deploy Cloudflare (Production)** (`workflow_run`), espera **120 s** antes del chequeo, y usa **`concurrency`** para no solaparse con el cron horario.
- **Web (CI)**: workflows **`deploy-cloudflare-on-tag.yml`** y **`deploy-cloudflare-preview.yml`** comprueban que el bundle incluye **`_worker.js`**, **`_routes.json`** y **`include: ["/*"]`** antes de desplegar.
- **Web (Worker)**: respuestas **HEAD** en **`/api/health`** y **`/api/meta`** (200 sin cuerpo, útil para monitorización); CORS permite **HEAD**.
- **Web (herramientas)**: **`check_production_web_health.py`** — reintentos ante HTTP transitorios (**`WEB_HEALTH_RETRIES`**, p. ej. 4 en Actions) y mensajes más accionables si fallan estáticos o **`/api/meta`**.

- **Web**: favicon e **apple-touch-icon** en pestañas y al guardar en pantalla de inicio (`/static/favicon.png` desde el logo del proyecto).
- **Web (SEO)**: `index.html` con **meta description**, **canonical**, **Open Graph**, **Twitter Card**, **JSON-LD** (`WebApplication`); **`robots.txt`** y **`sitemap.xml`** en la raíz del bundle (workflows de Cloudflare + `launch.py deploy-web`); imagen social **`/static/og-image.png`**. **`app.js`** actualiza `document.documentElement.lang`, título y metas al cambiar idioma (**`applySeoMeta()`**).
- **Web**: modo **círculo de quintas** — canvas de tónicas (clic / Mayús+clic diatónico, mayor o menor relativa, numeración y colores, ▶ sobre el círculo). Documentado en **`apps/web/README.md`**, **`AGENTS.md`** y **`PROJECT_SPEC.md`**.
- **Web (SEO)**: `index.html` (description, OG, Twitter), JSON-LD y **`SEO_META`** en **`app.js`** mencionan círculo de quintas / circle of fifths; comentario en **`robots.txt`** y **`sitemap.xml`**.

- **Flatpak / Flathub**: `com.freemidichords.MIDIChords.flathub.yml` usa el tag **`v1.0.1`**; `metainfo.xml` declara release **1.0.1** (2026-03-21). Guía `FLATHUB.md` alineada a ese tag de ejemplo.

- **Repo**: `.gitignore` ignora `.venv-build-dmg/` (venv local opcional para scripts de build DMG).
- macOS App Store: plantilla **`scripts/mas-env.example`**, script **`scripts/build_mas_store.sh`** (carga `signing/local/mas.env` y llama a `build_mas_pkg.sh` con red/archivos y opcionalmente **`--skip-tk-check`** para builds Qt sin Tcl/Tk 8.6), y flag **`--skip-tk-check`** en **`scripts/build_mas_pkg.sh`**.
- `.gitignore`: ignora capturas de depuración UI en `assets/` (patrones tipo `generation_full_*.png`, `overlay_mode_*.png`, `*_smoke.png`, …) y carpeta `assets/ui-debug-captures/` con `README.md` para uso local.
- Escritorio: modo trazas **`/verbose`**, **`--verbose`** o **`-v`** en `launch.py desktop` (y equivalente **`MIDICHORDS_VERBOSE=1`**); salida en **stderr** centrada en **audio** y **MIDI**. La configuración **Desktop: MIDIChords** en `.vscode/launch.json` arranca con `/verbose`.

### Documentado

- **Web**: `README.md` (raíz) — puntero a la documentación de frontend en `apps/web/README.md`.
- **Web**: `apps/web/README.md` — si el **dominio personalizado** sirve **JS/CSS antiguos** mientras **`*.pages.dev`** está al día (caché del zona / reglas de caché); `launch.py deploy-web` recuerda purgar o revisar reglas. Tras el deploy con **fingerprint** de `app.js`/`style.css`, el HTML apunta a URLs nuevas en cada release.
- **Web**: `apps/web/README.md` — guía **Google Search Console** (alta de propiedad, verificación, envío de `sitemap.xml`, cobertura, rendimiento/consultas y comprobaciones con `curl`).
- **Flatpak / Flathub**: `FLATHUB.md` — build local: **`appstream-compose`** con Debian (SDK 24.08 + `flatpak-builder` antiguo) vía **`org.flatpak.Builder`**; no usar `--command=flatpak-builder` (el wrapper fija `FLATPAK_USER_DIR`); remoto **`flathub` en modo `--user`**; backports o `appstream-compose: false` en copia local.
- macOS App Store: `signing/README.md` y `README.md` — flujo **`mas.env`** + **`./scripts/build_mas_store.sh`**; ejemplo manual de `build_mas_pkg.sh` con **`--skip-tk-check`**.
- Escritorio (macOS): script **`scripts/build_mac_test_dmg.sh`** — genera **`MIDIChords-macos-test.dmg`** y `.app` para probar en un Mac sin certificado Developer ID; documentado en `README.md`.
- Repo: reglas de agente Cursor — **`release-changelog-agent.mdc`** (analizar diff, **CHANGELOG** Unreleased por app, `commit`/`push`; invocable con `@release-changelog-agent`) y **`github-update-triggers.mdc`** (`alwaysApply`, reacciona a «actualiza cambios», «commit y push», etc.); script manual `scripts/document_release_changes.py`; ver `AGENTS.md`.
- Móvil (Flutter): inventario operativo de dispositivos de prueba, ids confirmados de iPhone/iPad y tablet Android, y guía para arrancar simuladores/emuladores iOS y Android desde `apps/mobile_flutter/README.md`.
- Móvil (Flutter): nuevo script `scripts/select_mobile_emulator.py` para listar simuladores/emuladores disponibles en macOS y arrancar el elegido desde terminal.
- Móvil (Flutter): el selector de emuladores muestra por defecto solo los simuladores iOS documentados; `--all-ios` enseña el resto, y los AVD Android rotos ahora fallan con un mensaje claro antes de intentar arrancar.
- Móvil (Flutter): el selector interactivo añade la opción `m` para expandir la lista iOS sin reinvocar el comando.
- Móvil (Flutter): el selector añade la opción `d` y el modo `--devices` para listar dispositivos físicos móviles y lanzar la app directamente con `launch.py mobile -d <id>`.
- macOS App Store: guía MAS actualizada con los nombres reales de certificados usados en este proyecto, nota sobre `--skip-store-validation` en entornos no interactivos, necesidad de subir con `build-number` nuevo tras un rechazo, y advertencia sobre bundles previos creados por `root`.
- macOS App Store: la subida recomendada se documenta ahora con la app **Transporter** en modo manual (arrastrar `.pkg` y pulsar **Deliver**); `xcrun iTMSTransporter` queda como alternativa secundaria de diagnóstico.

### Corregido

- **macOS (MAS / PyInstaller + Qt)**: **`build_mas_pkg.sh`** comprueba **`libqcocoa.dylib`** tras PyInstaller; si falta (p. ej. **`--collect-all PySide6`** sin efecto), ejecuta **`scripts/mas_embed_pyside6_bundle.py`** para copiar **PySide6** y **shiboken6** al `.app` y **aborta** si el plugin sigue ausente — evita **cierre inmediato en TestFlight/sandbox** sin crash claro. Añadido **`--collect-submodules PySide6`**; **`bootstrap_mas_build_env.sh`** instala **`pyinstaller-hooks-contrib`** junto a PyInstaller. Tras incrustar Qt, se **eliminan** del bundle los **`.app` anidados** (Assistant/Designer/Linguist) que trae **PySide6** (en **`Frameworks`** y **`Resources`**), para que **`codesign --verify --deep --strict`** no falle por symlinks rotos en sub-bundles.

- **macOS (MAS / TestFlight)**: **Qt WebEngine** (`QtWebEngineProcess.app` dentro de **`QtWebEngineCore.framework`**) provoca rechazo **90885** (ejecutable anidado con **application identifier** pero **sin provisioning profile** MAS). La app de escritorio **no usa WebEngine**; **`build_mas_pkg.sh`** añade **`--exclude-module`** para **QtWebEngine\*** / **QtWebView** / **QtWebChannel** y **borra** frameworks **`.so`** / **`.app`** anidados restantes antes de firmar. También se eliminan **`PySide6/Qt/libexec`** (rcc, uic, …) y **ejecutables Mach-O** en la raíz de **PySide6** (lupdate, qmllint, …), firmados por **`codesign --deep`** sin perfil embebido, y el plugin **`Qt/plugins/webview`**.

- **macOS (MAS / App Review 2.5.1)**: el plugin **`Qt/plugins/sqldrivers/libqsqlodbc.dylib`** enlaza símbolos **ODBC** que Apple considera **API no pública** en revisión. MIDIChords **no usa QtSql**; **`build_mas_pkg.sh`** añade **`--exclude-module PySide6.QtSql`** y **elimina** la carpeta **`Qt/plugins/sqldrivers`** del bundle antes de firmar.

- **Escritorio (detección)**: el botón **play** del panel de detección a veces no sonaba o quedaba deshabilitado al **soltar el MIDI** (o sin notas “en vivo”): se guarda el **último conjunto de notas reproducible** y se usa para habilitar el transport y reproducir al mantener pulsado aunque ya no haya teclas pulsadas (se limpia al **Limpiar** o al resetear entrada).

- **Escritorio (detección / audio)**: el **`note_off`** del transport solo afecta notas en **`_detection_preview_owned_notes`**. Si **todas** eran duplicadas (acorde ya sonando), se hace **note_off** + **note_on** por nota para re-atacar. Al **soltar** play solo se ajusta **`sounding_notes`** (sin **`_refresh_sounding_notes`** en ese momento) para no disparar un **segundo** ataque al soltar.

- **macOS (MAS / build)**: tras quitar módulos Qt, **`build_mas_pkg.sh`** elimina **symlinks rotos** bajo el `.app` antes de firmar; evita que **`codesign --verify --deep --strict`** falle con *No such file or directory* apuntando al bundle. Si la verificación sigue fallando, el script lista enlaces rotos y sale con error.

- **macOS (Mac App Store / Qt)**: arranque empaquetado — búsqueda amplia de plugins Qt (`libqcocoa.dylib`), `QT_QPA_PLATFORM_PLUGIN_PATH`, log **`mas_bootstrap_last.txt`** en Application Support; **`build_mas_pkg.sh`** usa **`--collect-all PySide6`** para no omitir plugins en el bundle (síntoma típico en revisión: app en Dock y cierre sin ventana ni crash log).

- **Web (CI)**: **`web-production-health`** — el **`wrangler pages deploy`** de autocuración incluye **`--commit-hash`**, **`--commit-message`** ASCII y **`--commit-dirty=true`** para evitar el fallo de la API de Cloudflare *Invalid commit message … valid UTF-8* en GitHub Actions.

- **Web (CI / salud)**: **`check_production_web_health.py`** — reintentos configurables (**`WEB_HEALTH_RETRIES`**, por defecto 2; el workflow horario usa **4**) ante **404/5xx** transitorios en el edge; mensajes más claros si **`/api/meta`** devuelve **404 vacío** (worker no enruta) o falta un **CSS/JS con hash**. **Worker**: **`HEAD`** en **`/api/health`** y **`/api/meta`**. Deploy **Pages** (producción y preview): paso que exige **`_worker.js`**, **`_routes.json`** y `include: ["/*"]` en el bundle.

- **Escritorio (Qt / Windows)**: combo **Diestro / Zurdo** en **generación** (vista guitarra) — estilo oscuro alineado con Ajustes (**QComboBox** con texto claro y fondo de tarjeta; antes el tema nativo dejaba texto negro sobre gris).

- **Web (Cloudflare Pages)**: **`_routes.json`** en el bundle de deploy (`"include": ["/*"]`) para que **`/api/*` no se resuelva como estático** en dominios personalizados donde el worker no se invocaba (síntoma: **404 vacío** en `/api/meta`, app cargada pero sin datos). Documentado en `apps/web/README.md`.

- **Escritorio (Qt)**: **teclado** — ancho mínimo por tecla blanca (~28 px, alineado con la web) con **scroll horizontal** si no cabe; con **nombres de notas** activados, las etiquetas también en **teclas negras** (colores tipo web). El ancho visible se toma del **viewport** del `QScrollArea`, no del canvas ensanchado.
- **Escritorio (Qt)**: **canvas** — anclas de texto **`n`** y **`s`** respectan la coordenada **x** (antes `AlignHCenter` usaba todo el ancho del canvas y desplazaba etiquetas, p. ej. nombres en teclas negras al centro del teclado).
- **Escritorio (Qt)**: **teclado** — redondeo inferior de teclas alineado a la web (`border-radius` ~8px en blancas; negras con esquinas inferiores redondeadas proporcionalmente, antes casi rectas en Qt).
- **Escritorio (Qt)**: **teclado (blancas)** — cromado como la web: fondo **#e8ecf2**, marco **#3a4558**, borde de tecla **#7b8798** (y tonos **#2b6da6** / **#c8772f** en estados azul/naranja), rendija fina entre teclas y texto de etiqueta **#10243a**.

- **Escritorio (detección / audio)**: menos **clics y ruido** al **arrastrar** en el teclado — la UI sigue al instante pero el audio se actualiza como máximo ~**80 Hz**; el sintético **no reinicia** una nota que ya suena, ataque algo más suave y **release** un poco más largo (preset por defecto). **Grand sample**: un nuevo `note_on` de la misma nota acelera la cola de la muestra anterior.

- **Escritorio (audio)**: al soltar teclas **MIDI**, menos **clic** en el piano sintético: envolvente de **release** desde un pico fijado al `note_off` (sin sustain×release), `release` algo más lento y cola más suave en **grand_sample** al cortar la muestra.

- **Escritorio (pentagrama)**: **clave de sol** y **clave de fa** más grandes y alineadas con la web (tamaño proporcional al espacio entre líneas; anclas verticales como en `app.js`); si hay PNG en `assets/`, se escalan al alto objetivo. **Sostenidos, bemoles y becuadros** también escalan con el pentagrama (armadura y notas), con separación horizontal ajustada.

- **Web (piano)**: nombres de nota en las teclas — tipografía algo menor, **#** / **♭** pegados al nombre (sin hueco de kerning) y teclas negras más compactas, para que etiquetas como **Sol#** no se corten en anchos estrechos.

- **Web (worker)**: respuestas de **`/`**, HTML y **`/static/*`** envían también **`CDN-Cache-Control: no-store`** y se quita **`Age`** heredado, para que el edge respete mejor el no-cache frente a reglas antiguas del zona; el síntoma típico era **JS nuevo en `*.pages.dev`** y **JS viejo en el dominio personalizado** (`cf-cache-status: HIT` con `max-age` largo).

- **Web / escritorio**: en **generación** y **escalas**, si dos armaduras enarmónicas tienen el **mismo número** de alteraciones, la armadura del pentagrama sigue el selector **# / ♭**. En **detección**, el pentagrama usa la **misma convención que el nombre del acorde** (menos alteraciones; empate → **bemoles**), aunque el selector esté en **#**.
- **Web**: el criterio **# / ♭** para empates y las peticiones API leen **`#accidental` del DOM** (`accidentalPreferFlatFromUi` / `currentAccidentalValue`) y se sincroniza `state.accidental` al arranque, para que no quede en **sharp** por defecto si el desplegable muestra **♭**.
- **Web**: **`applyFlatKeySigIfUiFlatAndTie`** (generación, escalas y **detección**) fuerza armadura **bemol** si el desplegable es **♭** y la tónica tiene **empate enarmónico**; **`root_pc` en detección** acepta cualquier número finito (no solo entero).
- **Web**: **armadura en el pentagrama** — sostenidos con **MIDI + `midiToTrebleY` / `midiToBassY`** (misma geometría que las notas) y **`textBaseline: middle`** (equivalente al anclaje centrado de Tk). Bemoles siguen offsets de `render_mixin.py`. Corrige el primer ♯ de Sol mayor en **Fa** (antes el canvas con baseline alfabético lo desplazaba hacia **Sol**).
- **Web**: en detección (y resto de superficies que no son pentagrama), los **nombres de nota en piano/guitarra** y controles afines siguen el selector **# / ♭** (`state.accidental`), no la armadura inferida del acorde en el pentagrama (el pentagrama sigue usando la escritura armónica vía `noteNameFromPcStaff`).
- **Web (worker)**: en detección, el campo **Notas** del panel usa **`noteName` con `preferFlat`** según el selector; ya no **`spellByDegree`** para esas etiquetas, de modo que con **♭** se muestran bemoles coherentes con la configuración.
- **Escritorio (detección)**: el **nombre del acorde** (tónica y bajo en slash) usa la misma convención armónica que **API/web** (`_chord_symbol_prefer_flat`: menos alteraciones; empate enarmónico → **bemoles**). El selector **# / ♭** sigue gobernando solo las **etiquetas de notas** del panel, no el símbolo del acorde.

- **Móvil (Flutter)**: **detección** y **pentagrama** alineados con la web/worker — nombre del acorde con **menos alteraciones** (misma regla que `chordSymbolPreferFlat`); lista **Notas** según el selector **# / ♭**; **armadura** dibujada en clave de sol y fa; al cambiar **# / ♭** se refrescan **detección** y, si aplica, **acorde** o **escala** ya generados.

- **Web (Cloudflare Pages)**: el HTML ya no añade `?v=<sha>` en el despliegue (workflow y `launch.py deploy-web`). El worker responde **307** a `GET`/`HEAD` de `/static/*` con `?` o `#`, redirigiendo al recurso sin query (fiable frente a **404** de `ASSETS.fetch` con cache-bust antiguo en CDN/HTML cacheado). `Cache-Control: no-store` en esa respuesta y en estáticos/HTML (`_headers` + worker).

- **CI / Flatpak**: el workflow **Validate Flatpak** solo se ejecuta con **Run workflow** (`workflow_dispatch`); se quitaron los disparadores automáticos en `main`, tags `v*` y PRs mientras no se publique en Flathub.

- **Flatpak**: el manifiesto instalaba dependencias Python del generador salvo **PySide6**; la app de escritorio importa Qt y fallaba con `ModuleNotFoundError`. Añadido módulo **`pyside6.json`** (wheels PyPI 6.10.2, x86_64 y aarch64) en los YAML de empaquetado; **`requirements.txt`** fija `PySide6==6.10.2`. El PR a Flathub debe incluir **`pyside6.json`** en la raíz (documentado en `FLATHUB.md`). **`pyside6.json`**: `pip` exige nombres de wheel válidos (PEP 427); se quitan `dest-filename` cortos y se instala con globs (`shiboken6-*.whl`, …).
- **CI / Flatpak**: workflow **Validate Flatpak** — `flatpak remote-add` usa **`--user`** y URL `dl.flathub.org` (en GitHub Actions el remoto de sistema fallaba con *ConfigureRemote not allowed*); `appstreamcli validate` con **`--no-net`** para evitar falsos positivos de URL desde los runners; `.desktop` con **`Categories=AudioVideo;Audio;Music;`** (requisito de `desktop-file-validate`). _(En **Unreleased** arriba: disparadores automáticos desactivados.)_
- **Flatpak / Flathub**: guía `FLATHUB.md` y comentarios del manifiesto — en el PR de nueva app los archivos van en la **raíz** de la rama (requisito Flathub para `detect-appid`); presentación Flathub [#8160](https://github.com/flathub/flathub/pull/8160) (PR [#8089](https://github.com/flathub/flathub/pull/8089) anterior cerrado por revisores). Manifiesto: sin `finish-args` de filesystem innecesarios (linter Flathub); fuente git con **`commit`** además del tag (documentado en `FLATHUB.md`). `python-deps.json`: **setuptools-scm** desde wheel PyPI (evita fallo del sdist con setuptools del SDK); **metainfo** con `<screenshots>` (URL en GitHub) para el linter de repo Flathub. **`appstream-compose: true`** para generar el catálogo AppStream y evitar `appstream-missing-appinfo-file` en el build de Flathub; CI instala **`appstream-compose`**. Iconos en **48/128/256/512** px bajo `hicolor` para que `appstreamcli compose` no falle con `icon-not-found`.
- macOS App Store: `build_mas_store.sh` **omite por defecto** `installer -store` (`MAS_SKIP_STORE_VALIDATION` por defecto `1`); aviso en `build_mas_pkg.sh` si se ejecuta y se queda colgado.
- macOS App Store: `scripts/build_mas_pkg.sh` usa **`$PYTHON_BIN -m PyInstaller`** en lugar del comando `pyinstaller` en PATH; mensaje claro si falta el módulo.
- macOS App Store / **Escritorio (Qt)**: arranque del `.app` PyInstaller — se fija **`QT_PLUGIN_PATH`** antes de importar PySide6 (`apps/desktop/darwin_frozen_bootstrap.py`) y **`PROJECT_ROOT`** usa **`sys._MEIPASS`** en binario `frozen` para localizar `assets/`; evita el cierre inmediato en Dock sin crash log que suele dar Qt sin plugins en bundle firmado/sandbox.
- Móvil (Flutter): **Generación** (piano) — digitación de acordes alineada al escritorio: tríada mano derecha **1-3-5** y mano izquierda **5-3-1** (notas ordenadas de grave a agudo); antes se asignaban dedos por índice (1-2-3 / 5-4-3).
- macOS App Store: `scripts/build_mas_pkg.sh` limpia atributos `com.apple.quarantine` también en `assets/` y en los recursos empaquetados del `.app` antes de firmar, evitando rechazos de App Store Connect como `code 91109`.
- macOS release env: `scripts/validate_macos_release_env.sh` detecta de forma más robusta las identidades válidas del llavero.
- Escritorio (Qt): **Ajustes** — al refrescar la lista de dispositivos al abrir el combo de **entrada MIDI** o **salida de audio**, el otro combo parecía perder la selección: tras `clear()`/`addItems()` el `QComboBox` no se re-sincronizaba con el `StringVar` (solo existía enlace combo→var). `ttk.Combobox.configure(values=…)` vuelve a aplicar `setCurrentText` desde la variable si el valor sigue en la lista; el refresco de Ajustes usa la config como respaldo si la var va vacía.
- Escritorio (Qt): **Metrónomo** — fila **Temporizador** en dos líneas (checkbox + título / minutos y segundos) para que etiquetas y spinboxes no se pisen en paneles estrechos; figuras con **tresillo** dibujan el **"3"** en una franja superior y el rectángulo de color por debajo (sin invadir el borde del botón).
- Escritorio (Qt): **Metrónomo** — la fila del play y el botón de sonido MIDI dejaban de lado a lado y se solapaban; la fila usa `grid` con columna extensible (como los sliders de volumen/tempo) en lugar de `pack` en un `QHBoxLayout` poco fiable aquí.
- Escritorio: **Escalas** (piano) — al tocar con MIDI, la nota se marcaba en el teclado pero no en el pentagrama: `staff_pressed_scale_notes` solo se actualizaba con clic en teclado/pentagrama. Tras cada refresco de notas activas se sincroniza el pentagrama con MIDI/ratón/sostenido (sin interferir mientras se arrastra en el pentagrama).
- Escritorio: **Generación** — al mantener notas por MIDI (o varias a la vez), el resaltado en teclado/pentagrama dejaba de mostrarse o solo quedaba una nota: `_update_generation_preview()` trataba cualquier `generated_playing_notes` como “reproducir acorde” y llamaba a `_stop_generated_playback()` al refrescar la vista previa (p. ej. al actualizar combos en Qt). Solo se interrumpe ahora el play mantenido con botón o barra espaciadora; añadidas salidas tempranas si raíz/variante/inversión no cambian.
- Escritorio (Qt): **Ajustes** — el combo de entrada MIDI podía quedar vacío aunque el teclado sonara: el refresco en segundo plano usaba un probe MIDI por subprocess donde `sys.gettrace()` no refleja el depurador, fallaba y vaciaba la lista; el listado de puertos pasa a hacerse siempre con `mido.get_input_names()` en proceso. El `Combobox` Qt ahora ejecuta `postcommand` al desplegar (como Tk), para refrescar al abrir la lista.
- Escritorio (Qt / Windows): diálogo **Configuración** — el estilo nativo de `QComboBox`/`QLabel` dejaba texto oscuro sobre fondo gris poco legible frente al panel oscuro; se aplica una hoja de estilo al formulario de ajustes usando los mismos colores que el resto de la UI (`color_surface_alt`, `color_text`, etc.).
- Escritorio: modo **Detección** — el conmutador **# / ♭** ya no cambia la armadura ni las alteraciones del **pentagrama** (siguen la convención del acorde detectado, como en generación/escalas). En el panel, la **lista de notas activas** usa la preferencia cromática (# → p. ej. `Re#` en lugar de `Mi♭` para la misma altura); el **nombre del acorde** sigue con escritura por grados respecto a la tónica detectada.
- Escritorio (Qt): panel derecho del **metrónomo** — el contenido iba a parar recortado en ventanas bajas o con muchos controles; ahora va dentro de un **área con desplazamiento** (`QScrollArea`, mismo patrón que otros paneles). **Temporizador**: fila de minutos/segundos en un submarco para evitar solapamientos. **Acentuar inicio de compás**: checkbox sin texto + etiqueta con `wraplength` según el ancho del panel.
- Escritorio (Qt): **metrónomo** — el panel del **piano** inferior dejaba mucho margen gris: se anula el `minimumHeight` heredado del modo guitarra, el teclado pasa a **124 px** de alto en metrónomo (156 en el resto), menos holgura en `_fit_instrument_panel_height` y padding del `RoundedPanel` del instrumento `(12,8,12,4)`. El dibujo del teclado usa el alto real del canvas, no un mínimo fijo de 156.
- Escritorio (Qt): **metrónomo** — el carácter de tempo (p. ej. *Moderato*) va entre paréntesis en la **misma línea** que el valor BPM, debajo del slider, en lugar de una segunda fila.
- Escritorio (Qt): **metrónomo** (panel derecho) — texto y controles nativos (`QLabel`, temporizador con `QCheckBox`/`QSpinBox`) ya no quedan en **negro sobre gris**: QSS concatenado al contenido del scroll y fondo del viewport/`QScrollArea`, alineado con el tema del panel.
- Escritorio (Qt): **metrónomo** — **Volumen**, **Tempo** y **Pulsos** van en la **misma fila** que sus sliders (etiqueta a la izquierda), ganando altura vertical en el panel. Cadena `label_metronome_meter`: **«Pulsos»** / **«Beats»** (antes «Pulsos por compás» / «Beats per bar»). **Web**: `app.js` e `index.html` alineados con la etiqueta corta del compás.
- Escritorio (Qt): **metrónomo** — las `ttk.Label` del panel pasan **`fg=color_text`** (el shim Qt solo pinta el `QLabel` si hay `fg`; el QSS global no bastaba). Etiquetas de **Volumen/Tempo/Pulsos** con **`sticky=nse`** en la celda de dos filas para **centrarlas en vertical** con la fila del slider.
- Escritorio (Qt): **Detección** y **metrónomo** — el botón **Reproducir / Silenciar entrada MIDI** ya no ocupa todo el ancho del panel: `GrayRoundedButton` admite **`shrink_to_text`** (ancho según el texto); en metrónomo el **stretch** del grid pasa a una columna vacía a la derecha.
- Escritorio: **Configuración** — **Mostrar notas en teclas blancas** queda **marcada por defecto** (`DEFAULT_CONFIG` / `show_keyboard_note_labels: true`); perfiles antiguos con `false` en `config.json` no se modifican solos.
- Escritorio (Qt): **metrónomo** — botones de **clicks por pulso**: `sticky=ew` en lugar de `nsew` para que **no estiren la altura** al agrandar la ventana (siguen repartiendo el ancho).
- Escritorio (Qt): **metrónomo** — **Volumen/Tempo/Pulsos**: la etiqueta va solo en la **fila del slider** (`sticky=e`, sin `rowspan=2`) para alinearla con **−** y el control; **Temporizador** y **Acentuar compás**: checkbox con `sticky=w` (centrado vertical en el shim) en lugar de `nw`, sin `pady` que lo subiera respecto al texto.
- Escritorio (Qt): **Escalas** — el slider de BPM entre **−** y **+** no se veía: con `sticky="ew"` el grid Qt usaba una alineación que dejaba el canvas al ancho mínimo (1 px). Sticky `ew` / `ns` (relleno) ahora usa alineación 0 para estirar a la celda (afecta a otros sliders con el mismo patrón).
- Escritorio (Qt): sliders del **metrónomo** (tempo, volumen, compás) y similares — `QtCanvas` ya no usa `setFixedSize` con `width`+`height` (solo tamaño mínimo), de modo que la franja entre **−** y **+** puede ocupar todo el ancho del panel.
- Escritorio: en **Generación**, al mantener pulsada una tecla MIDI el resaltado del teclado ya no desaparece a los ~520 ms; solo se quita al **soltar** la nota (`note_off`). Los clics en teclado/pentagrama siguen usando el timeout corto.
- Escritorio: en **Generación** con MIDI, al pulsar varias notas del acorde se resaltan y suenan **todas** a la vez (cada una hasta su `note_off`); el ratón sigue sustituyendo la vista previa y envía `note_off` en piano a las notas que dejan de mostrarse.
- Escritorio (migración Qt): aviso `QObject::startTimer: Timers can only be used with threads started with QThread` — `after()` y el refresco de dispositivos en **Configuración** ya no crean `QTimer` desde hilos `threading` (se reenvía al hilo GUI con `run_on_main_thread`).
- Escritorio (migración Qt): el shim `place()` ahora respeta `x` / `y` / `width` / `height` como Tk, de modo que los paneles izquierdo y derecho sobre el canvas superior vuelven a posicionarse y mostrarse (antes solo se usaba `relx`/`relwidth`).
- Escritorio (migración Qt): `pack_forget` quita el widget del `QLayout` del padre (no solo `hide()`); pestañas de modo no empaquetadas se ocultan al inicio para que no tapen el panel derecho; `RoundedPanel` expone `sizeHint`/`minimumSizeHint` para que el panel inferior (piano) reciba altura en el `QVBoxLayout`.
- Escritorio (migración Qt): `QtCanvas.itemconfigure` aplica `width`/`height` a ventanas de `create_window` (panel de resultados de detección); `Label` aplica `fg`/`font` y tamaño mínimo (icono ⚙); se ocultan al inicio los canvas de afinador/guitarra que no están en `pack` para no tapar el teclado.
- Escritorio (migración Qt): `QtCanvas.create_arc` y constantes `tk.PIESLICE`/`ARC`/`CHORD` para dibujar el teclado (`redraw_keyboard`).
- Escritorio (migración Qt): clics en canvas alineados con Tk (`<ButtonPress-1>` / `<ButtonRelease-1>`) y `mouseReleaseEvent` vuelve a notificar para teclado/pentagrama/guitarra.
- Escritorio (migración Qt): play de detección sin `command` al soltar (evita segundo `_start_detection_hold` con `PlayTransportButton`).
- Escritorio (migración Qt): `tk.Label` enlaza `textvariable` (`StringVar`) con el `QLabel` para notas/intervalos/acorde en detección (y similares).
- Escritorio (migración Qt): botones #/♭ de la barra superior centrados y altura 40 px alineada al selector de modo; `Widget` respeta `<ButtonPress-1>` si está enlazado antes que `<Button-1>`.
- Escritorio (migración Qt): botones personalizados (`RoundedChoiceButton`, `GrayRoundedButton`, `GreenRoundedButton`) usan `ui_font_family` y tamaños alineados al resto de la UI; #/♭ en barra superior a **12 pt bold** como `widgets.py` (Tk); `GreenRoundedButton` dibuja **♭** compuesto como en Tk.
- Escritorio (migración Qt): `pack(padx=…/pady=…)` usa huecos por widget (`addSpacing` / `insertSpacing`) en lugar de `setSpacing` global, y los widgets Qt (`widgets_qt`) respetan `padx`; corrige separación #/♭ y el margen antes de ⚙.
- Escritorio (migración Qt): panel derecho — `tk.Label` aplica `configure(wraplength=…)` (antes ignorado), alinea `anchor`/`justify`, y el tamaño mínimo con texto multilínea usa `TextWordWrap` (evita métricas de una sola línea enormes). Textos de resultados en **Generación** y **Escalas** unificados a **13 pt** como **Detección**. `ttk` usa `qt_pack_attach` para `pack`; `Combobox`, `Spinbox` y `Checkbutton` respetan `font=(familia, tamaño…)`.
- Escritorio (migración Qt): fila **Detección** (play / Limpiar / Reproducir entrada MIDI) — `pack(fill=X)` en la fila, botón MIDI con `expand_h` + `pack(fill=X, expand=True)` para repartir el ancho; `pack(anchor=…)` en vertical respeta alineación (`AlignLeft`, etc.). Misma idea en la fila play + MIDI del **metrónomo** (`sticky=ew`).
- Escritorio (migración Qt): panel derecho más legible — títulos **20 pt**, ayuda **15 pt**, resultado acorde **38 pt**, notas/intervalos **15 pt** (mono); menos `pady` entre bloques, `RoundedPanel` derecho con padding vertical **8**; generación/escalas alineados al mismo criterio.
- Escritorio (migración Qt): icono **⚙** — el `QLabel` interno ya no intercepta el ratón (`WA_TransparentForMouseEvents`); `bind_all('<ButtonPress-1>')` se despacha vía `QApplication.installEventFilter`; `_is_widget_inside` sube por `parentWidget` y `Widget.master` para cerrar overlays al pulsar fuera.
- Escritorio (migración Qt): selector de modo — `tk.Frame` aplica `bg` y borde `highlightthickness`/`highlightbackground` con `WA_StyledBackground` + `stylesheet`; `tk.Label` reenvía esas opciones al `Widget` para que el panel modal y las tarjetas tengan fondo visible (no solo iconos/texto).
- Escritorio (migración Qt): `ttk.Frame(..., padding=…)` — el shim ya no pasa `padding` a `QWidget`; se traduce a `setContentsMargins` del `pack`/`grid` interno (p. ej. diálogo de ajustes).
- Escritorio (migración Qt): selector de modo en canvas — `QtCanvas.coords()` actualiza posición de ítems `text`/`line`/`rect`/`oval`/`image` (antes solo ventanas; la flecha quedaba en x=0 y no se veía). Dibujo de texto con anclaje tipo Tk (`w`/`e`/…) vía `drawText(QRectF, flags)` + centrado vertical; fuente Tk con tamaño negativo → `setPixelSize`. Flecha **▼** y texto del modo a **15 pt bold**.
- Escritorio (migración Qt): **Configuración (⚙)** — el `eventFilter` de la app despacha `bind_all('<ButtonPress-1>')` por cada ancestro del widget pulsado; tras abrir el overlay, el siguiente receptor era el `Frame` padre del icono y `_on_global_click_press` cerraba el diálogo al instante. Se ignora el cierre automático durante ~0,28 s tras abrir (`_settings_overlay_opened_ts`), como el selector de modo.
- Escritorio (migración Qt): selector de modo (rejilla) — `rowconfigure` solo en filas con tarjetas (4 modos ya no dejan una fila vacía estirada abajo); icono y texto con `anchor="center"` y `pack(anchor="center")` para igualar el centrado de Tk y no pegar el glifo a la izquierda.

## [1.0.0] - 2026-03-14

Primera versión 1.x publicada del proyecto.

> Nota (trazabilidad iOS): esta etiqueta `v1.0.0` apunta al commit con el que se subió a App Store Connect la build de iOS **1.0.0 (2)**.

Disponible en:

- App Store en iOS
- Mac App Store en escritorio macOS
- Google Play en Android

### Añadido

- Aplicación Flutter para tablet con detección, generación de acordes, escalas y metrónomo.
- Modo ayuda contextual en móvil con zonas interactivas por pantalla y por control.
- Flujo documentado de despliegue web en Cloudflare Pages.

### Mejorado

- Resaltado del pentagrama en generación de acordes para respetar mejor la mano activa.
- Comportamiento del metrónomo y del audio nativo iOS en iPhone/iPad.
- Ayudas contextuales y distribución visual en iPad.

### Corregido

- Envío del formulario de comentarios en producción web.
- Verificación del despliegue de producción web para detectar estados rotos donde faltaba `/api/meta`.
- Varios problemas de enlace y configuración del proyecto iOS Flutter.

## [1.0.1] - 2026-02-20

Cambios respecto a `v1.0.0` (iOS **1.0.0 (2)**).

### iOS (Flutter)

- Audio del piano menos “cortado” al soltar la tecla (release más natural).
- Reducción de saturación/clipping percibido en iOS (atenuación de ganancia, especialmente en piano).
- Build de iOS: **1.0.1 (3)** / **1.0.1 (4)**.

### Android (Flutter)

- Corregido el panel izquierdo del metrónomo en Android 14 (ej. UMIDIGI G9C).

### Web (Cloudflare Pages)

- Nuevo panel **Descargas** (PC/Mac y móvil) con ventana/modal y enlaces actualizados.
- Enlaces de descarga directos para artefactos en GitHub (`/releases/latest/download/...`).
- Endurecimiento del despliegue para evitar caché de CSS/JS:
  - `Cache-Control: no-store` para HTML y `/static/*`.
  - Se añadió cache-busting con `?v=${GITHUB_SHA}` en estáticos; **más tarde se retiró** (provocaba 404 en Pages; ver corrección en **Unreleased** arriba).
- Ajuste de responsive: mantener **3 columnas** del panel inferior hasta 700px.

### CI / Releases (desktop)

- Firma y notarización de macOS en CI (opcional vía `SIGN_MACOS=true`) con import de certificado, keychain y `notarytool`.
- Fixes de creación de DMG en macOS CI (`hdiutil` “Resource busy” y nombre temporal `.tmp.dmg`).
- Deploy de Cloudflare producción solo con **tags `v*`** (no en cada push a `main`).
- Publicación de instaladores en GitHub Releases y sincronización al repo público `FreeMIDIChords_Releases`.
- Notificación por correo al mantener cuando falla un workflow (Resend).

### Repo / mantenimiento

- Eliminado el submódulo roto `flathub-submission` y añadido a `.gitignore` como carpeta local.

## [Unreleased] - Cambios desde [1.0.1]

_(Próximos cambios.)_

### Corregido

- Escritorio (migración Qt): variaciones de guitarra cacheadas ahora se filtran/reordenan para que acordes como **SolM** no dibujen una cejilla con notas por delante (mezcla incoherente con cuerdas abiertas).
- Escritorio (migración Qt): en **Escalas**, el panel derecho de “Notas/Intervalos” ahora muestra correctamente el subpanel (el shim ajusta también la altura del `create_window` interno del `scale_result_canvas`).
- Escritorio (migración Qt): en **Generación** (modo guitarra) el panel inferior ya no recorta el `guitar_canvas`; `_fit_instrument_panel_height()` ajusta correctamente la altura en Qt (usa `self.height()` y fija el alto del panel).

[1.0.0]: https://github.com/aortegaCampanillas/MIDIChords/releases/tag/v1.0.0
[1.0.1]: https://github.com/aortegaCampanillas/MIDIChords/releases/tag/v1.0.1
