from PyInstaller.utils.hooks import collect_dynamic_libs

# Ensure the C extension for sounddevice (_sounddevice) is bundled correctly
# inside the PyInstaller onefile binary.
hiddenimports = ["_sounddevice"]
binaries = collect_dynamic_libs("sounddevice")

