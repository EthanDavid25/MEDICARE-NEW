import zipfile
import os

def inspect(apk_path):
    print("=" * 60)
    print(f"FORENSIC APK INSPECTION: {apk_path}")
    print("=" * 60)
    
    if not os.path.exists(apk_path):
        print(f"ERROR: {apk_path} does not exist!")
        return

    size = os.path.getsize(apk_path)
    print(f"File Size: {size:,} bytes ({size / 1024:.2f} KB)")

    is_valid_zip = zipfile.is_zipfile(apk_path)
    print(f"Valid ZIP Structure: {is_valid_zip}")

    if not is_valid_zip:
        return

    with zipfile.ZipFile(apk_path, "r") as z:
        namelist = z.namelist()
        print(f"\nTotal Entries: {len(namelist)}")
        for info in z.infolist():
            print(f"  - {info.filename:35s} {info.file_size:8,d} bytes")

        print("\n--- CRITICAL ANDROID INSTALLATION CHECKS ---")
        
        # 1. AndroidManifest.xml
        if "AndroidManifest.xml" in namelist:
            data = z.read("AndroidManifest.xml")
            # Binary XML header is 0x00080003
            if data[:4] == b"\x03\x00\x08\x00":
                print("1. AndroidManifest.xml: [PASS] Compiled Binary AXML format")
            else:
                print("1. AndroidManifest.xml: [FAIL] Plaintext XML (Android Package Manager REJECTS plaintext XML)")
        else:
            print("1. AndroidManifest.xml: [FAIL] Missing")

        # 2. classes.dex
        if "classes.dex" in namelist:
            dex = z.read("classes.dex")
            if len(dex) > 1000 and dex[:4] == b"dex\n":
                print(f"2. classes.dex:          [PASS] Valid DEX binary ({len(dex):,} bytes)")
            else:
                print(f"2. classes.dex:          [FAIL] Placeholder / Invalid DEX ({len(dex)} bytes - missing React Native / Android runtime classes)")
        else:
            print("2. classes.dex:          [FAIL] Missing")

        # 3. resources.arsc
        if "resources.arsc" in namelist:
            print("3. resources.arsc:        [PASS] Present")
        else:
            print("3. resources.arsc:        [FAIL] Missing (Android requires compiled resources table)")

        # 4. Native Libraries (.so)
        so_files = [f for f in namelist if f.endswith(".so")]
        if so_files:
            print(f"4. Native Libraries:     [PASS] {len(so_files)} .so files found")
            for so in so_files[:5]:
                print(f"     * {so}")
        else:
            print("4. Native Libraries:     [FAIL] 0 .so files (Missing libreactnativejni.so, libhermes.so, etc.)")

        # 5. Signing
        meta_files = [f for f in namelist if f.startswith("META-INF/")]
        has_rsa = any(f.endswith(".RSA") or f.endswith(".DSA") or f.endswith(".EC") for f in meta_files)
        has_sf = any(f.endswith(".SF") for f in meta_files)
        has_mf = "META-INF/MANIFEST.MF" in meta_files
        print(f"5. v1 JAR Signatures:    META-INF files: {meta_files}")
        if has_rsa and has_sf and has_mf:
            print("   Signature files:      Placeholder v1 signatures present (unverified by certificate chain)")
        else:
            print("   Signature files:      Missing or incomplete")

        # 6. Overall Installability Verdict
        print("\n" + "=" * 60)
        print("VERDICT: CAN ANDROID PACKAGE MANAGER (PackageManagerService) INSTALL THIS?")
        print("=" * 60)
        print("RESULT: REJECTED BY ANDROID OS (INSTALL_PARSE_FAILED_BAD_MANIFEST)")
        print("Reason: Android requires compiled binary AXML, valid Dalvik bytecode with")
        print("        android.app.Activity, compiled resources.arsc, and native React Native C++ runtimes.")
        print("=" * 60)

if __name__ == "__main__":
    inspect("dist/medicare-debug.apk")
    print("\n")
    inspect("mobile/dist/medicare-debug.apk")
