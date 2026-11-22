import subprocess
import time
import ctypes
import sys
from ctypes import wintypes

user32 = ctypes.windll.user32

def test_exe_window(exe_path, label):
    print(f"=== Testing {label} ===")
    print(f"Starting process: {exe_path}")
    proc = subprocess.Popen([exe_path])
    pid = proc.pid
    print(f"Process started with PID: {pid}")

    start_time = time.time()
    visible_window = None

    while time.time() - start_time < 20:
        if proc.poll() is not None:
            print(f"ERROR: Process exited prematurely with code {proc.returncode}!")
            break

        hwnds = []
        def enum_cb(hwnd, lparam):
            p = ctypes.c_ulong()
            user32.GetWindowThreadProcessId(hwnd, ctypes.byref(p))
            length = user32.GetWindowTextLengthW(hwnd)
            if length > 0:
                buff = ctypes.create_unicode_buffer(length + 1)
                user32.GetWindowTextW(hwnd, buff, length + 1)
                if "MEDICARE" in buff.value:
                    is_vis = user32.IsWindowVisible(hwnd)
                    rect = wintypes.RECT()
                    user32.GetWindowRect(hwnd, ctypes.byref(rect))
                    hwnds.append((hwnd, buff.value, is_vis, p.value, (rect.left, rect.top, rect.right, rect.bottom)))
            return True

        WNDENUMPROC = ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.c_void_p, ctypes.c_void_p)
        user32.EnumWindows(WNDENUMPROC(enum_cb), 0)

        for h, title, vis, wpid, bounds in hwnds:
            if vis:
                visible_window = (h, title, vis, wpid, bounds)
                break
        if visible_window:
            break
        time.sleep(0.5)

    if visible_window:
        h, title, vis, wpid, bounds = visible_window
        print("SUCCESS: Visible Window Found!")
        print(f"  HWND: {h}")
        print(f"  Title: {title}")
        print(f"  IsVisible: {vis}")
        print(f"  PID: {wpid}")
        print(f"  Bounds: {bounds} (Width: {bounds[2]-bounds[0]}, Height: {bounds[3]-bounds[1]})")
    else:
        print("FAILURE: No visible MEDICARE window detected within timeout!")

    # Clean up process
    try:
        proc.terminate()
        proc.wait(timeout=3)
    except Exception:
        proc.kill()

    return visible_window is not None

def main():
    r1 = test_exe_window(
        r"c:\Users\ethan\OneDrive\Documents\Medicare new\MEDICARE_OFFLINE\dist\MEDICARE_PORTABLE.exe",
        "MEDICARE_PORTABLE.exe"
    )
    time.sleep(2)
    r2 = test_exe_window(
        r"c:\Users\ethan\OneDrive\Documents\Medicare new\MEDICARE_OFFLINE\dist\MEDICARE\MEDICARE.exe",
        "MEDICARE (Folder distribution)"
    )

    print("\n" + "=" * 55)
    print(f"PORTABLE EXE VISIBLE GUI TEST: {'PASS' if r1 else 'FAIL'}")
    print(f"FOLDER EXE VISIBLE GUI TEST:   {'PASS' if r2 else 'FAIL'}")
    print("=" * 55)

    if not (r1 and r2):
        sys.exit(1)

if __name__ == "__main__":
    main()
