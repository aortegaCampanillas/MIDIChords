# MIDIChords Integration Roadmap

> Documento histórico de junio de 2026; gran parte de estas integraciones ya
> existe. El backlog vigente está en [`../ROADMAP.md`](../ROADMAP.md).

## Overview

Este documento detalla las integraciones pendientes para completar las características implementadas en el plan de sincronización cross-platform.

**Estado actual:**
- Web: 11/11 (100%)
- Desktop: 9/11 (81.8%)
- Mobile: 9/11 (81.8%)

## Desktop (Python/Tkinter)

### 1. MIDI Output Toggle - Integración de Wrapper Methods ✓ DONE
**Status:** Completo
- [x] `play_note()` y `stop_note()` implementados en main_app.py
- [x] Reemplazados 16+ calls en scales_mixin, generation_mixin, input_detection_mixin
- [x] Funcionalidad Audio/MIDI completamente operativa

### 2. Piano Fingerings - Integración de UI
**Status:** Infraestructura lista, UI pendiente
- [x] `scale_fingering_hand` state agregado en main_app.py
- [ ] Agregar botones de selector RH/LH en ui_mixin.py (línea ~2900)
- [ ] Conectar `getFingeringForScale()` en render_mixin.py para mostrar números de dedos
- **Effort:** 2-3 horas

### 3. Scale Octaves - Integración de UI ✓ DONE
**Status:** Completo
- [x] Botones de octavas (1, 2, 3) en ui_mixin.py
- [x] `_get_scale_notes_for_octaves()` en scales_mixin.py
- [x] Rendering actualizado para mostrar octavas expandidas

### 4. MIDI Highlighting en Generación - Integración de Rendering
**Status:** State listo, rendering pendiente
- [x] `generation_midi_held_notes` state agregado
- [x] Tracking de notas (add/remove en input_detection_mixin)
- [ ] Actualizar render_mixin.py para resaltar notas sostenidas con color diferente
- **Effort:** 1-2 horas

## Mobile (Flutter)

### 1. MIDI Output Toggle - Integración Completa
**Status:** State y wrappers listos, integración pendiente
- [x] `_soundOutput` state agregado
- [x] `playNote()` y `stopNote()` métodos creados con TODO comments
- [ ] Reemplazar todas las llamadas de reproducción de audio con `playNote()/stopNote()`
- [ ] Conectar MIDI output a `_midiCommand` cuando `_soundOutput == 'midi'`
- **Effort:** 3-4 horas
- **TODOs:** 
  - Línea 9199: Send MIDI note_on
  - Línea 9204: Integrate actual note playback logic
  - Línea 9210: Send MIDI note_off
  - Línea 9215: Integrate actual note stop logic

### 2. Piano Fingerings - Integración de UI
**Status:** Tablas en fingerings.dart, UI pendiente
- [x] `fingerings.dart` con todas las tablas TomPlay
- [x] `getFingeringForScale()` función exportada
- [ ] Agregar state `_scaleFingerings` para almacenar digitaciones computadas
- [ ] Conectar método `getFingeringForScale()` en scales tab
- [ ] Mostrar números de dedos en el widget piano
- **Effort:** 3-4 horas

### 3. Scale Octaves - Integración de UI ✓ DONE
**Status:** Completo
- [x] `_scaleOctaves` state agregado
- [x] `_getScaleNotesForOctaves()` helper implementado
- [x] Buttons/UI para seleccionar octavas (pendiente verificación)

### 4. MIDI Highlighting en Generación - Integración Completa
**Status:** State listo, integración pendiente
- [x] `_generationMidiHeldNotes` state agregado
- [ ] Agregar tracking en MIDI input handler (cuando se reciben note_on/off en generation)
- [ ] Actualizar rendering del piano para resaltar notas sostenidas
- **Effort:** 2-3 horas

## Features Web-Only (No aplican a Desktop/Mobile)

### 1. Detección de Intervalos Melódicos
- Requiere base de datos de canciones de referencia
- Lógica compleja de identificación de intervalo por audio
- **Esfuerzo:** No aplica a desktop/mobile (arquitectura web específica)

### 2. Landing Page
- Específica de sitio web
- Galería de capturas y descargas
- **Esfuerzo:** No aplica a desktop/mobile

## Sequence de Integración Recomendada

### Fase 1: Desktop (Prioridad Alta) - ~4-5 horas
1. Piano Fingerings UI (2-3h)
2. MIDI Highlighting en Rendering (1-2h)

### Fase 2: Mobile (Prioridad Media) - ~8-10 horas
1. MIDI Output Toggle Completo (3-4h)
2. Piano Fingerings UI (3-4h)
3. MIDI Highlighting en Rendering (2-3h)

## Testing Checklist

### Desktop
- [ ] Digitaciones RH/LH se muestran correctamente
- [ ] Números de dedos están en posiciones correctas
- [ ] MIDI highlighting se activa/desactiva con notas sostenidas
- [ ] Audio/MIDI toggle funciona end-to-end

### Mobile
- [ ] Audio/MIDI toggle se persiste en preferencias
- [ ] Notas se reproducen/silencian según `_soundOutput`
- [ ] Digitaciones RH/LH se muestran en scales tab
- [ ] MIDI highlighting funciona en generación

## Notas Técnicas

### Desktop: Piano Fingerings Rendering
- Ubicación: `render_mixin.py` líneas ~700-800
- Necesita: Dibujar números de dedos (1-5) sobre las teclas relevantes
- Datos disponibles: `scale_preview_notes`, `scale_fingering_hand`
- Función: `get_fingering_for_scale(scale_type, tonic_pc, hand, count)`

### Mobile: MIDI Output Integration
- Ubicación: main.dart líneas 9199, 9210
- Usar: `_midiCommand.sendMessage()` o similar API
- Considerar: MidiPacket structure, velocity handling

### Desktop: MIDI Highlighting Colors
- Usar color diferente (quizá amarillo o verde) para notas sostenidas
- `generation_midi_held_notes` contiene las notas sostenidas
- Renderizar en mismo lugar que notas activas (piano + staff)

## Métricas Finales Esperadas

Con todas las integraciones completadas:
- **Desktop:** 9/11 → Sin cambio (pianolas ya 100%, MIDI highlighting es visual)
- **Mobile:** 9/11 → Sin cambio (misma lógica que desktop)

Los 2 features faltantes (intervalos melódicos, landing page) quedan web-only
permanentemente por ser específicos de su arquitectura.

**Paridad final esperada:** 9/11 (81.8%) en ambas plataformas es el máximo
realista sin reimplementar features completamente web-specific.
