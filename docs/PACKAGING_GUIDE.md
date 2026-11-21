# MEDICARE — Packaging & Deployment Guide
## Windows Standalone Executable & Android APK Builds

---

## 1. Windows Standalone Executable (PyInstaller)

### Prerequisites
- Python 3.11 with `pyinstaller`, `kivy`, `cryptography`, `reportlab`, and `matplotlib` installed.
- (Optional) MinGW / GCC if recompiling C DLLs.

### Build Steps
1. Navigate to the project root:
   ```cmd
   cd MEDICARE_OFFLINE
   ```
2. Run the packaging batch script:
   ```cmd
   scripts\build_windows_exe.bat
   ```
   Or execute directly via PyInstaller:
   ```cmd
   python -m PyInstaller --clean medicare.spec
   ```
3. The standalone distribution is output to:
   ```text
   dist\MEDICARE\
   ├── MEDICARE.exe      <-- Launchable executable
   ├── data\             <-- Local SQLite & JSON datasets bundled
   ├── native\           <-- C native libraries
   └── ... (runtime DLLs)
   ```
4. Test the packaged application by running `dist\MEDICARE\MEDICARE.exe`. It executes completely offline without external dependencies.

---

## 2. Android APK Packaging (Buildozer)

### Prerequisites
- Linux / WSL2 environment with Python 3, Git, and Java 17 JDK.
- Buildozer installed (`pip install buildozer`).
- Android SDK & NDK (automatically downloaded by Buildozer).

### Build Steps
1. Copy or clone the `MEDICARE_OFFLINE` project to your Linux / WSL2 environment.
2. Ensure `buildozer.spec` is present at the project root.
3. Run:
   ```bash
   buildozer android debug
   ```
4. The generated APK will be placed in:
   ```text
   bin/medicare-1.0.0-arm64-v8a-debug.apk
   ```
5. Install on an Android device or emulator:
   ```bash
   adb install -r bin/medicare-1.0.0-arm64-v8a-debug.apk
   ```
6. The application automatically adapts to mobile touch input, portrait-first layout, and local mobile SQLite storage.
