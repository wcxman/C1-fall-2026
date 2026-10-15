import camera
import os
import numpy as np
import cv2

from load_dlpc350 import DLPC350


# Loads DLLs from C1-FALL-2026/dlls. For more information, consult the README.
FILE_DIR = os.path.dirname(os.path.abspath(__file__))
DLL_DIR = os.path.join(FILE_DIR, "..", "dlls")
CAPTURE_DIR = os.path.join(FILE_DIR, "..", "captures")
os.makedirs(CAPTURE_DIR, exist_ok=True)

try:
    os.add_dll_directory(DLL_DIR)
    print(f"DLL directory found at {DLL_DIR}.")

except Exception as e:
    print("DLL directory was not successfully found. There may be unexpected results. Please follow one-time setup instructions in the README ")
    print(f"Error: {e}")

dmd = DLPC350()
dmd.connectDLP()
print(dmd.getHardwareStatus())

for i in range(10):
    dmd.loadImage(i)
    camera.save_image(camera.capture_image())