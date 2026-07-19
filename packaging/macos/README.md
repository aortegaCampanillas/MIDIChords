# Empaquetado macOS

Este directorio contiene configuración declarativa para los paquetes macOS:

- `entitlements.developerid.plist`: firma y notarización Developer ID.
- `entitlements.mas.plist`: referencia base para Mac App Store.
- `mas-env.example`: plantilla de credenciales locales; copiarla a
  `signing/local/mas.env` y no versionar el archivo resultante.

Los comandos públicos permanecen en `scripts/` para conservar los flujos
documentados. Los entitlements generados durante el build se escriben también
aquí y están ignorados por Git.
