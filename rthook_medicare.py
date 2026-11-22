"""
PyInstaller runtime hook for MEDICARE.
Adds sys._MEIPASS (onefile) or the exe directory (folder build) to sys.path
so that 'app.*' imports resolve correctly from frozen code.
Also sets KIVY_HOME to a writable location beside the user-data directory.
"""
import sys
import os
from pathlib import Path

# --- sys.path fixup ---
if hasattr(sys, "_MEIPASS"):
    meipass = sys._MEIPASS
    if meipass not in sys.path:
        sys.path.insert(0, meipass)
else:
    # Folder build: exe lives in dist/MEDICARE/; app code is in dist/MEDICARE/_internal/
    exe_dir = Path(sys.executable).parent
    if str(exe_dir) not in sys.path:
        sys.path.insert(0, str(exe_dir))

# --- KIVY_HOME: redirect to writable location so Kivy can write its config ---
if "KIVY_HOME" not in os.environ:
    import tempfile
    candidates = []
    localappdata = os.environ.get("LOCALAPPDATA", "")
    if localappdata:
        candidates.append(os.path.join(localappdata, "MEDICARE", ".kivy"))
    appdata = os.environ.get("APPDATA", "")
    if appdata:
        candidates.append(os.path.join(appdata, "MEDICARE", ".kivy"))
    candidates.append(os.path.join(tempfile.gettempdir(), "MEDICARE", ".kivy"))

    chosen_kivy_home = None
    for cand in candidates:
        try:
            os.makedirs(cand, exist_ok=True)
            test_f = os.path.join(cand, ".test_write.tmp")
            with open(test_f, "w") as f:
                f.write("ok")
            os.remove(test_f)
            chosen_kivy_home = cand
            break
        except Exception:
            continue

    if not chosen_kivy_home:
        chosen_kivy_home = os.path.join(tempfile.gettempdir(), "MEDICARE", ".kivy")
        try:
            os.makedirs(chosen_kivy_home, exist_ok=True)
        except Exception:
            pass

    os.environ["KIVY_HOME"] = chosen_kivy_home
