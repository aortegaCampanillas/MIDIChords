# sounddevice is a module (sounddevice.py), not a package, so collect_dynamic_libs
# cannot find it. We explicitly bundle the _sounddevice C extension from the same
# directory as sounddevice.py.
import glob
import os

hiddenimports = ["_sounddevice"]
binaries = []

try:
    import sounddevice
    pkg_dir = os.path.dirname(sounddevice.__file__)
    for path in glob.glob(os.path.join(pkg_dir, "_sounddevice*.so")):
        binaries.append((path, "."))
except Exception:
    pass
