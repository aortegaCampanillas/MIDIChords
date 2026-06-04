# Configuración HTTPS para pruebas de Web MIDI

## Descripción

Algunas características de la web requieren HTTPS, incluyendo la **Web MIDI API con permisos persistentes**. Este documento explica cómo configurar el entorno para probar estas características.

## ¿Por qué HTTPS?

- Los navegadores requieren conexiones seguras (HTTPS) para acceder a APIs de hardware como MIDI
- Los permisos deben ser concedidos por el usuario y persisten en navegadores modernos
- Esto aplica tanto en desarrollo como en producción

## Configuración

### 1. Certificados SSL (ya están generados)

Los certificados auto-firmados están en `.certs/`:
- `cert.pem` - Certificado SSL
- `key.pem` - Clave privada

Si necesitas regenerarlos:
```bash
mkdir -p .certs
openssl req -x509 -newkey rsa:2048 -keyout .certs/key.pem -out .certs/cert.pem -days 365 -nodes -subj "/CN=localhost"
```

### 2. Usar VS Code para lanzar HTTPS

En VS Code, abre la paleta de comandos (`Cmd+Shift+D` o `Ctrl+Shift+D`) y selecciona:
- **"Web: MIDIChords (HTTPS)"**

Esto lanzará:
```
🔒 HTTPS Server iniciado
   URL: https://localhost:8443
```

### 3. Probar en el navegador

1. Abre [`https://localhost:8443`](https://localhost:8443)
2. El navegador mostrará una advertencia de certificado auto-firmado
3. Haz clic en "Avanzado" o "Continuar de todas formas" para aceptar
4. Ya puedes usar MIDI y los permisos persistirán

### 4. Línea de comandos (alternativa)

También puedes lanzar el servidor manualmente:
```bash
python serve_https.py --port 8443
```

## Características de `serve_https.py`

- ✅ Sirve `apps/web/static` con HTTPS
- ✅ Soporta CORS para todas las rutas
- ✅ Recarga automática de archivos (sin hot-reload, necesita F5)
- ✅ Certificados auto-firmados (sin validación externa)
- ✅ Compatible con Windows y macOS/Linux

## Prueba del cambio de MIDI

Con la configuración HTTPS, ahora puedes:

1. Activar MIDI en la aplicación (clic en botón MIDI)
2. Conceder permisos cuando el navegador lo pida
3. **Recargar la página** - Ya NO pedirá permisos de nuevo

Esto funciona porque:
- La app ahora usa `navigator.permissions.query()` para verificar permisos previos
- Los navegadores modernos persistem los permisos de MIDI
- No hay popup cada vez que recargas

## Notas importantes

⚠️ **Certificados auto-firmados**
- Solo para desarrollo local
- El navegador mostrará advertencias de seguridad
- En producción (https://midichordsapp.com) se usan certificados válidos

🔒 **HTTPS solo en localhost**
- Los permisos de MIDI requieren HTTPS o localhost en HTTP
- Esto es una restricción de seguridad del navegador

📝 **Diferencias entre servidores**
- `Web: MIDIChords` - Servidor HTTP tradicional en puerto 8000 (sin MIDI persistente)
- `Web: MIDIChords (HTTPS)` - Servidor HTTPS en puerto 8443 (con MIDI persistente)

## Solución de problemas

### "Connection refused"
- Verifica que el puerto 8443 no esté en uso
- Usa `--port 9000` para cambiar el puerto

### Certificado no encontrado
- Ejecuta el comando de generación de certificados arriba
- Asegúrate de que estás en el directorio raíz del proyecto

### Permisos aún piden confirmación
- Limpia el historial/cookies del navegador
- Abre DevTools (F12) → Application → Cookies y elimina `localhost`
- Recarga la página

## Lectura adicional

- [Web MIDI API - MDN](https://developer.mozilla.org/en-US/docs/Web/API/Web_MIDI_API)
- [Permissions API - MDN](https://developer.mozilla.org/en-US/docs/Web/API/Permissions_API)
- [HTTPS requirements - Chrome Developers](https://developer.chrome.com/articles/https-upgrades/)
