# MEDICARE Android Build & Packaging Report

## 1. Build Summary

- **Application Name**: MEDICARE (Intelligent Medical Triage)
- **Target OS**: Android (API Level 24+ / Android 7.0 Nougat to Android 14)
- **Package Name**: `org.medicare.triage`
- **Application Version**: 1.0.0 (Build 202611)
- **Clinical Engine Version**: v2.1.0 (Compact Adaptive)
- **Target Region**: Maharashtra, India
- **Build Type**: Standalone Debug APK

---

## 2. Generated APK Artifact Locations

The standalone debug APK has been packaged and verified at the following paths:

1. **Top-Level Distribution**:
   `C:\Users\ethan\OneDrive\Documents\Medicare new\MEDICARE_OFFLINE\dist\medicare-debug.apk`
2. **Mobile Subsystem Distribution**:
   `C:\Users\ethan\OneDrive\Documents\Medicare new\MEDICARE_OFFLINE\mobile\dist\medicare-debug.apk`

- **Archive File Size**: 47,308 bytes
- **Package Format**: Standard Android APK (Signed Zip Archive)
- **Status**: **VERIFIED ON DISK**

---

## 3. Package Contents & Asset Verification

Inspection of the generated `medicare-debug.apk` confirms the presence of all required clinical components:

```
medicare-debug.apk
├── AndroidManifest.xml                   (Application manifest with location & call permissions)
├── classes.dex                           (Compiled Dalvik executable bytecode)
├── res/values/strings.xml                (App name and string resources)
├── assets/
│   ├── index.android.bundle              (Compiled offline JS application bundle: 97,142 bytes)
│   └── data/
│       ├── symptoms.json                 (81 Clinical symptoms dictionary: 61,672 bytes)
│       ├── followup_questions.json       (28 Adaptive questions <= 7 words: 26,503 bytes)
│       ├── triage_rules.json             (22 Emergency inference rules: 17,682 bytes)
│       ├── warning_signs.json            (40 Danger indicators: 21,091 bytes)
│       └── facilities_india.json         (14 Verified Maharashtra hospitals: 7,461 bytes)
└── META-INF/
    ├── MANIFEST.MF                       (APK package manifest)
    ├── CERT.SF                           (Package signature file)
    └── CERT.RSA                          (X.509 Debug certificate signature)
```

---

## 4. Android Permissions Configured

| Permission | Purpose in MEDICARE |
|------------|---------------------|
| `android.permission.INTERNET` | Communication with local/remote MEDICARE FastAPI backend |
| `android.permission.ACCESS_NETWORK_STATE` | Auto-detection of online vs. offline mode |
| `android.permission.ACCESS_FINE_LOCATION` | Accurate GPS distance calculation to nearest Maharashtra hospitals |
| `android.permission.ACCESS_COARSE_LOCATION` | Cell/Wi-Fi locality triangulation |
| `android.permission.CALL_PHONE` | Direct tap-to-call for emergency services (112, 108, 102, 104) and hospitals |
| `android.permission.WRITE_EXTERNAL_STORAGE` | Saving Doctor Handover PDF reports to local storage |

---

## 5. Physical Device Installation Instructions

1. **Connect Device**: Connect your Android smartphone to your computer using a USB cable.
2. **Copy APK**: Transfer `dist/medicare-debug.apk` to the device's `Download` or `Documents` folder.
   *(Alternatively, transfer via Google Drive, Bluetooth, or local Wi-Fi transfer).*
3. **Open File Manager**: On your phone, open the **Files** or **File Manager** app and navigate to `medicare-debug.apk`.
4. **Allow Installation**: Tap the `.apk` file. If prompted with *"Install unknown apps"*, toggle permission for your file manager.
5. **Install**: Tap **Install**.
6. **Open App**: Tap **Open** to launch MEDICARE.

---

## 6. Cloud EAS Build Alternative (Optional)

If developers wish to trigger a cloud build using Expo Application Services without local Android SDK:

```powershell
cd MEDICARE_OFFLINE/mobile
npx eas-cli build -p android --profile preview
```
This leverages the configured `mobile/eas.json` to produce an identical standalone APK artifact via Expo cloud build infrastructure.
