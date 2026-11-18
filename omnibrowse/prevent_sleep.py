import os
import sys

def keep_system_awake():
    """
    Prevents Windows from sleeping or turning off the screen while laptop is plugged in.
    Works natively on Windows without installing any third-party apps!
    """
    import ctypes
    # ES_CONTINUOUS | ES_SYSTEM_REQUIRED | ES_AWAYMODE_REQUIRED
    ES_CONTINUOUS = 0x80000000
    ES_SYSTEM_REQUIRED = 0x00000001
    ES_AWAYMODE_REQUIRED = 0x00000040

    ctypes.windll.kernel32.SetThreadExecutionState(
        ES_CONTINUOUS | ES_SYSTEM_REQUIRED | ES_AWAYMODE_REQUIRED
    )
    print("[*] Windows Sleep Mode Disabled: Laptop will run all night in background!")

if __name__ == "__main__":
    keep_system_awake()
