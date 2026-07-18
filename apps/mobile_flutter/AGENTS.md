# Instrucciones para `apps/mobile_flutter/`

Estas reglas complementan el `AGENTS.md` de la raíz.

## Arquitectura actual

- `lib/main.dart` concentra todavía gran parte del estado, lógica local, servicios y UI.
- Los módulos ya extraídos en `lib/` son preferibles como destino para lógica pura y componentes acotados.
- La app mantiene implementaciones locales de generación/detección musical para funcionar sin depender de la API web.

## Criterio para nuevas extracciones

1. Extraer primero funciones puras y modelos, con tests.
2. Después extraer servicios con ciclo de vida: audio, MIDI, preferencias y cachés.
3. Extraer painters y widgets sin trasladar estado global innecesario.
4. Finalmente separar páginas/controladores por modo.

No introducir una librería nueva de gestión de estado únicamente para reducir el tamaño de `main.dart`. La separación debe conservar comportamiento, reproducción, MIDI, scroll y ciclo de vida de cada modo.

## Assets compartidos

`assets/guitar_chord_cache.json`, `assets/chord_variant_theory.json`, `assets/changelog.json` y varios samples tienen copias canónicas o equivalentes en la raíz/web. Los tests Python validan su igualdad; consultar `docs/architecture/SOURCE_OF_TRUTH.md` antes de editarlos.

## Verificación

Desde la raíz:

```bash
python scripts/check.py mobile
```

El perfil ejecuta `flutter analyze` y `flutter test` dentro de `apps/mobile_flutter/`. Ejecutar además `python scripts/check.py python` cuando cambien assets o contratos multiplataforma.
