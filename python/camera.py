import os
import numpy as np
import cv2
from datetime import datetime

from thorlabs_tsi_sdk.tl_camera import TLCameraSDK

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

#!TODO: Finish image capture function and make a module
# def capture_image() -> np.ndarray:
#     with TLCameraSDK() as sdk:
#         if len(sdk.discover_available_cameras()) < 1:

# Following code adapted from example code. 

with TLCameraSDK() as sdk:
    available_cameras = sdk.discover_available_cameras()
    if len(available_cameras) < 1:
        print("no cameras detected")

    with sdk.open_camera(available_cameras[0]) as camera:
        camera.exposure_time_us = 14000
        camera.frames_per_trigger_zero_for_unlimited = 0  # start camera in continuous mode
        camera.image_poll_timeout_ms = 1000  # 1 second polling timeout

        camera.arm(2)

        camera.issue_software_trigger()

        frame = camera.get_pending_frame_or_null()
        if frame is not None:
            print("frame #{} received!".format(frame.frame_count))
            image_buffer_copy = np.copy(frame.image_buffer)
            numpy_shaped_image = image_buffer_copy.reshape(camera.image_height_pixels, camera.image_width_pixels)
            nd_image_array = np.full((camera.image_height_pixels, camera.image_width_pixels), 0, dtype=np.uint16)
            nd_image_array[:,:] = numpy_shaped_image
            filename = "capture_" + datetime.now().strftime("%y-%m-%d_%H-%M-%S") + ".tif"
            im_path = os.path.join(CAPTURE_DIR, filename)
            cv2.imwrite(im_path, nd_image_array)

        else:
            print("Unable to acquire image, program exiting...")
            exit()
            
        cv2.waitKey(0)
        camera.disarm()

#  Because we are using the 'with' statement context-manager, disposal has been taken care of.

print("program completed")