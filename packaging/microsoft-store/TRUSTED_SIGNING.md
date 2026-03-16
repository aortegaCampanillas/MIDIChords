# Firma de confianza (Microsoft Trusted Signing)

Guía para firmar el ejecutable de MIDIChords con **Azure Trusted Signing** (Firma de confianza de Microsoft) y cumplir la directiva 10.2.9 de la Microsoft Store.

**Nota:** Esta opción **requiere una suscripción de Azure de pago** (~10 USD/mes). El proyecto no la usa por defecto; la guía se mantiene por si en el futuro se decide activar la firma de código.

## Requisitos

- **Suscripción de Azure** (de pago; no sirve Free/Trial).
- **Identidad verificada**: documento (DNI/pasaporte) para desarrollador individual, o documentos de la empresa para organización.
- **Aproximadamente 10 USD/mes** (SKU Basic).

## 1. Registrar el proveedor de recursos

```bash
az login
az provider register --namespace Microsoft.CodeSigning
# Esperar 2-3 minutos
az provider show --namespace Microsoft.CodeSigning --query "registrationState"
# Debe mostrar "Registered"
```

## 2. Crear la cuenta de Trusted Signing

**Portal (recomendado):**

1. [Azure Portal](https://portal.azure.com) → Crear un recurso → buscar **"Trusted Signing"** o **"Artifact Signing"**.
2. Crear cuenta:
   - **SKU:** Basic.
   - **Región:** la más cercana (ej. West Europe, East US).
   - **Nombre de cuenta:** único (ej. `midichords-signing`).
   - **Grupo de recursos:** crear uno (ej. `midichords-signing-rg`).
3. En **Overview** de la cuenta, anota el **Endpoint** (ej. `https://wus2.codesigning.azure.net/` o `https://eus.codesigning.azure.net/`). Lo necesitarás en el workflow.

**CLI:**

```bash
az group create --name midichords-signing-rg --location westeurope
az trustedsigning create \
  --resource-group midichords-signing-rg \
  --account-name midichords-signing \
  --location westeurope \
  --sku-name Basic
```

## 3. Validar identidad

Solo se puede hacer desde el **Portal**:

1. En la cuenta de Trusted Signing → **Identity validation** → Add.
2. Tipo: **Individual** (o Organization si es empresa).
3. Rellenar datos y subir documento (carné o pasaporte) y selfie si lo pide.
4. Enviar y esperar aprobación (suele ser 1–3 días laborables para individual). Recibirás un correo cuando esté aprobado.

## 4. Crear perfil de certificado

Cuando la identidad esté **Approved**:

1. En la cuenta → **Certificate profiles** → Add.
2. **Certificate type:** Code Signing.
3. **Identity validation:** la que aprobaron.
4. **Profile type:** **Public Trust** (necesario para evitar avisos de SmartScreen).
5. **Profile name:** ej. `MIDIChords-CodeSigning`.
6. Crear y anotar el nombre exacto (sensible a mayúsculas).

## 5. Asignar rol de firma (para ti o para CI)

**Para firmar desde tu PC:**

1. Cuenta Trusted Signing → **Access control (IAM)** → Add role assignment.
2. Rol: **Trusted Signing Certificate Profile Signer**.
3. Miembro: tu usuario de Azure AD.
4. Guardar.

Luego inicia sesión con ámbito de codesigning:

```bash
az logout
az login --use-device-code --scope "https://codesigning.azure.net/.default"
```

**Para GitHub Actions (service principal):**

Necesitas **Owner** o **User Access Administrator** en la suscripción.

```bash
# Sustituir YOUR_SUBSCRIPTION_ID y el scope por tu resource group y cuenta
az ad sp create-for-rbac \
  --name "MIDIChords-GitHubActions" \
  --role "Trusted Signing Certificate Profile Signer" \
  --scopes /subscriptions/YOUR_SUBSCRIPTION_ID/resourceGroups/midichords-signing-rg/providers/Microsoft.CodeSigning/codeSigningAccounts/midichords-signing \
  --json-auth
```

Guarda la salida (clientId, clientSecret, tenantId, subscriptionId). **El clientSecret no se puede volver a ver**; guárdalo en un gestor de contraseñas.

## 6. Secrets y variables en GitHub

En el repositorio: **Settings → Secrets and variables → Actions.**

**Secrets (crear):**

| Nombre | Valor |
|--------|--------|
| `AZURE_CLIENT_ID` | clientId del service principal |
| `AZURE_CLIENT_SECRET` | clientSecret del service principal |
| `AZURE_TENANT_ID` | tenantId del service principal |
| `AZURE_SUBSCRIPTION_ID` | subscriptionId (ID de la suscripción de Azure) |

**Variables (opcional; si no usas variables, pon los valores en el workflow):**

| Nombre | Valor | Ejemplo |
|--------|--------|--------|
| `TRUSTED_SIGNING_ENDPOINT` | URL del endpoint de tu región | `https://wus2.codesigning.azure.net/` |
| `TRUSTED_SIGNING_ACCOUNT_NAME` | Nombre de la cuenta | `midichords-signing` |
| `TRUSTED_SIGNING_PROFILE_NAME` | Nombre del perfil de certificado | `MIDIChords-CodeSigning` |

Si integras la firma en un workflow (p. ej. `.github/workflows/build-installers.yml`), puedes usar estas variables o sustituir por valores fijos.

El workflow de instaladores **no incluye** actualmente pasos de Trusted Signing. Si en el futuro quieres activarlos, añade después del paso de PyInstaller: login con `azure/login@v2` y firma con `Azure/trusted-signing-action` (ver [documentación](https://github.com/Azure/trusted-signing-action)).

## Solución de problemas

### "La cuenta no tiene los permisos de Identidad de Microsoft Entra necesarios para registrar una aplicación"

Si al crear un **registro de aplicaciones** (App registration) en Azure te sale un error indicando que tu cuenta (p. ej. `aortega98@gmail.com`) no tiene permisos en el espacio empresarial (tenant) `9188040d-6c67-4c5b-b112-36a304b66dad`, suele deberse a una de estas situaciones:

1. **Estás en un inquilino de organización (empresa/educación)**  
   Has iniciado sesión en un directorio que no es el tuyo (por ejemplo una cuenta de trabajo o invitado). En ese inquilino solo un administrador puede darte permiso para registrar aplicaciones.

2. **Qué puede hacer el administrador del inquilino** (en [Azure Portal](https://portal.azure.com) con ese tenant):
   - **Identidad de Microsoft Entra** → **Roles y administradores** → asignarte el rol **Desarrollador de aplicaciones** (*Application developer*).
   - O bien: **Identidad de Microsoft Entra** → **Configuración del usuario** → activar **Registros de aplicaciones** para que los usuarios puedan registrar apps.
   - Si eres **usuario invitado**: **Identidad de Microsoft Entra** → **Configuración del usuario** → **Colaboración externa** → activar que los invitados tengan el mismo acceso que los miembros (o la opción que permita registros).

3. **Usar tu propio inquilino (recomendado para desarrollo individual)**  
   Si la suscripción de Azure y la cuenta de desarrollador de la Store son personales, conviene trabajar en el **directorio por defecto** de tu cuenta Microsoft, no en el de una organización. Cómo encontrar el selector de directorio en [Azure Portal](https://portal.azure.com):

   **Opción A – Barra superior derecha**
   - Arriba a la **derecha** verás tu **nombre/avatar** o un icono de **cuenta**.
   - Haz clic ahí: se abre un menú donde suele aparecer **"Cambiar directorio"** o **"Switch directory"**.
   - Elige el directorio de tu cuenta personal (p. ej. "Directorio predeterminado" o el que no sea el de una empresa).

   **Opción B – Configuración del portal**
   - Arriba a la derecha, haz clic en el icono de **engranaje (⚙ Configuración)**.
   - En el panel que se abre, busca **"Directorios y suscripciones"** / **"Directories + subscriptions"**.
   - Ahí verás la lista de directorios; pulsa **"Cambiar"** en el que quieras usar (tu directorio personal).

   Después de cambiar, crea el registro de aplicaciones y los recursos de Trusted Signing en **ese** directorio (no en el de la organización).

   **Si en "Todos los directorios" sale "No se encontró ningún directorio":** solo tienes un inquilino asociado a tu cuenta. No puedes cambiar a otro a menos que un administrador te invite a otro directorio.

   **Si en el directorio actual sale "No hay ninguna suscripción en el directorio":** necesitas crear o asociar una suscripción de Azure en ese directorio (por ejemplo "Prueba gratuita" o una suscripción de pago) desde el mismo portal. Sin suscripción no podrás crear recursos como Trusted Signing ni registrar aplicaciones con servicio asociado.

[Más información sobre asignación de roles en Microsoft Entra](https://learn.microsoft.com/en-us/entra/identity/role-based-access-control/how-to-assign-role).

## Referencias

- [Azure Trusted Signing](https://azure.microsoft.com/products/trusted-signing)
- [Quickstart: Artifact Signing](https://learn.microsoft.com/en-us/azure/trusted-signing/quickstart)
- [Trusted Signing Action (GitHub)](https://github.com/Azure/trusted-signing-action)
