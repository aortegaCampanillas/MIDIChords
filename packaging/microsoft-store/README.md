# Microsoft Store – MIDIChords

Notas para publicar MIDIChords en la Microsoft Store.

## La pregunta al crear la app: ¿EXE o MSIX?

Al crear la app en Partner Center te preguntan si el paquete es **EXE/MSI** o **MSIX**. Esa elección define el **flujo de envío** (qué tipo de archivo acepta la página Paquetes en el primer envío).

- **Si elegiste MSIX:** en Paquetes solo tendrás que subir tu `.msix` (por ejemplo **MIDIChords-windows-x64.msix**).
- **Si elegiste EXE (o MSI):** la página Paquetes está pensada para instaladores clásicos. Aun así **puedes pasar a MSIX** sin crear otra app: en un **nuevo envío** (por ejemplo una actualización) quita el paquete EXE/MSI anterior y **sube el archivo .msix**. Cuando ese envío se apruebe, la Store repartirá la app en MSIX a partir de entonces. No hay opción en el menú para “cambiar el tipo”; el cambio se hace subiendo el MSIX en ese envío.

## Cómo indicar que la aplicación usa MSIX

En la Store el tipo lo define **qué archivo subes** en cada envío (submission), no una casilla aparte.

### Pasos en Partner Center

1. Entra en [Partner Center](https://partner.microsoft.com/dashboard) y abre tu aplicación.
2. Crea un **nuevo envío** o edita el envío en borrador (por ejemplo, una actualización).
3. Ve a la página **Paquetes** (Packages) del envío.
4. **Si antes subiste un instalador EXE/MSI:**
   - Quita ese paquete (Remove) del envío.
5. **Sube el paquete MSIX:**
   - Arrastra el archivo **MIDIChords-windows-x64.msix** (el que genera el workflow en el Release) al área de carga, o usa “Examinar” para seleccionarlo.
   - La Store acepta `.msix`, `.msixupload`, `.msixbundle` (y equivalentes .appx). Para Windows 10 y posteriores, Microsoft recomienda `.msixupload` si lo generas con Visual Studio; un `.msix` generado con MakeAppx también es válido.
6. Completa el resto del envío (disponibilidad, listado, etc.) y envía a revisión.

A partir de ese envío, la Store entregará la aplicación en formato MSIX a los usuarios que la instalen o actualicen. No hay una opción aparte para “marcar” la app como MSIX: el tipo lo define el paquete que subes en la página **Paquetes**.

### Parámetros del instalador (instalación silenciosa)

En el envío, el campo **“Parámetros del instalador”** / *Installer parameters* pide los modificadores para instalación silenciosa (por ejemplo `/s` en algunos EXE).

**Para paquete MSIX:** la instalación es silenciosa por defecto y **no usa modificadores**. Puedes dejar el campo en blanco o escribir, por ejemplo:

- *El instalador se ejecuta en modo silencioso y no requiere modificadores.*

No hace falta indicar ningún parámetro tipo `/s` ni equivalente.

### Validación del paquete MSIX

Si la Store rechaza el paquete al subirlo:

- **MinVersion:** la Store no acepta paquetes con `MinVersion` ≤ 10.0.17134.0. El workflow genera el manifest con `MinVersion="10.0.17763.0"` para cumplir el requisito.
- **PublisherDisplayName:** debe coincidir **exactamente** con el nombre del anunciante en Partner Center (como aparece en tu perfil de desarrollador). Si falla la validación, revisa en Partner Center cómo está escrito y ajústalo en el workflow si hace falta.
- **Identidad de paquete (Store):** el manifest debe usar la **identidad asignada por la Store** a tu app, no valores genéricos:
  - **Identity Name:** el que indica Partner Center (p. ej. `Antonioortega.FreeMIDIPianoGuitarChords`).
  - **Publisher:** el CN que asigna la Store (p. ej. `CN=E70C548D-768A-4F80-B0D6-41DB1F7A402F`), no tu nombre real.
  - **DisplayName:** un nombre para mostrar que tengas **reservado** en la ficha de la app (si la Store dice que "MIDIChords" no está reservado, reserva ese nombre en la identidad de la app o usa el que sí tengas reservado, p. ej. "Free MIDI Piano Guitar Chords"). El workflow usa los valores que la Store indicó en la validación; si cambias la identidad en Partner Center, actualiza `.github/workflows/build-installers.yml` (paso "Build MSIX package") para que coincidan.
- **runFullTrust:** si aparece una advertencia de que la funcionalidad restringida `runFullTrust` requiere aprobación, suele bastar con declararla en el envío (en la sección de capacidades/declaraciones del paquete) y aceptar la revisión. Para apps de escritorio es habitual que la aprueben.

### Resumen

| Dónde | Qué hacer |
|-------|-----------|
| **Partner Center → Tu app → Envío → Paquetes** | Quitar el .exe (instalador) si lo tenías y subir **MIDIChords-windows-x64.msix** |
| Mismo listado, misma ficha de la app | Solo cambia el archivo que subes; la ficha (nombre, descripción, capturas) sigue siendo la misma. |

---

## Firma de código (opcional)

Para cumplir la directiva de la Store sobre firma de código (y reducir avisos de SmartScreen), ver [TRUSTED_SIGNING.md](TRUSTED_SIGNING.md). Requiere suscripción de Azure de pago.
