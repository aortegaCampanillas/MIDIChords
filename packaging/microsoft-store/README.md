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
  - **DisplayName:** debe ser **exactamente** el nombre que tienes reservado para la app en Partner Center. En **Partner Center → Tu app → Administración de la aplicación → Identidad de la aplicación** (o **Product management → App identity**) verás el **nombre de la aplicación** reservado; el `DisplayName` del manifest tiene que coincidir con ese texto. El workflow usa `MIDIChords`. Si la Store dice que ese nombre no está reservado, entra en **Identidad de la aplicación**, revisa o edita el **nombre de la aplicación** hasta que sea exactamente `MIDIChords` (o el que quieras mostrar) y guarda; luego regenera el MSIX con ese mismo nombre en el workflow si lo cambiaste.
### runFullTrust (capacidad restringida)

Si al subir el MSIX aparece la **advertencia** de que las capacidades restringidas (p. ej. `runFullTrust`) requieren aprobación:

- Es una **advertencia**, no un error de validación: puedes seguir con el envío.
- En el mismo flujo de envío (submission) suele haber una sección de **declaraciones** o **capacidades** del paquete donde debes **declarar** el uso de capacidades restringidas y, si lo pide, **justificar** por qué la app necesita `runFullTrust` (por ejemplo: "App de escritorio Win32 empaquetada como MSIX; necesita ejecución con plena confianza para acceso a MIDI y audio").
- La Store revisa estas declaraciones; para aplicaciones de escritorio (Desktop Bridge) es habitual que aprueben `runFullTrust` tras esa revisión. Si te piden más datos, responde con el motivo técnico (acceso a APIs de sistema, MIDI, etc.).

No hace falta quitar `runFullTrust` del manifest: es necesaria para que la app de escritorio funcione correctamente.

### Resumen

| Dónde | Qué hacer |
|-------|-----------|
| **Partner Center → Tu app → Envío → Paquetes** | Quitar el .exe (instalador) si lo tenías y subir **MIDIChords-windows-x64.msix** |
| Mismo listado, misma ficha de la app | Solo cambia el archivo que subes; la ficha (nombre, descripción, capturas) sigue siendo la misma. |

---

## Firma de código (opcional)

Para cumplir la directiva de la Store sobre firma de código (y reducir avisos de SmartScreen), ver [TRUSTED_SIGNING.md](TRUSTED_SIGNING.md). Requiere suscripción de Azure de pago.
