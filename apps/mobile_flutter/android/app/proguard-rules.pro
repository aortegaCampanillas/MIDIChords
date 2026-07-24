# flutter_midi_command usa reflexión/JNI para su bridge de MIDI; mantener sus clases evita
# que R8 elimine o renombre símbolos que el plugin resuelve dinámicamente.
-keep class com.invisiblewrench.flutter_midi_command.** { *; }

# MethodChannel propio (midichords/platform) en MainActivity: mantener el nombre de clase y
# los métodos públicos usados desde Dart vía MethodChannel.setMethodCallHandler.
-keep class com.FPAlanTuring.FreeMIDIChords.** { *; }
