import camera
import os
import time
from datetime import datetime
import cv2
from thorlabs_tsi_sdk.tl_camera import TLCameraSDK


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

with TLCameraSDK() as sdk:
        available_cameras = sdk.discover_available_cameras()
        if len(available_cameras) < 1:
                raise Exception("no cameras detected")
        with sdk.open_camera(available_cameras[0]) as tl_camera:
            camera.init_camera(tl_camera)
            # total_start_time = datetime.now()
            for i in range(10):
                dmd.loadImage(i)
                # start_time = datetime.now()
                image = camera.capture_image(tl_camera, shift_left=True)
                # elapsed = datetime.now() - start_time
                # print(f"Time elapsed for capture {i}: {elapsed}")
                cv2.imshow("Captures", image)
                cv2.waitKey(500)
                camera.save_image(image, CAPTURE_DIR)
            # print(f"Total elapsed: {datetime.now() - total_start_time}")