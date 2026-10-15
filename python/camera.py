import os
import numpy as np
import cv2
from datetime import datetime

from thorlabs_tsi_sdk.tl_camera import TLCameraSDK

def capture_image(exposure_time_us : int  = 14000, 
                  timeout_ms       : int  = 1000, 
                  auto_contrast    : bool = False) -> np.ndarray:
    with TLCameraSDK() as sdk:
        available_cameras = sdk.discover_available_cameras()
        if len(available_cameras) < 1:
                raise Exception("no cameras detected")
        with sdk.open_camera(available_cameras[0]) as camera:
                # Configure camera
                camera.exposure_time_us = exposure_time_us # Default 14 ms exposure time
                camera.frames_per_trigger_zero_for_unlimited = 0  # start camera in continuous mode
                camera.image_poll_timeout_ms = timeout_ms  # Default 1 second polling timeout
                camera.arm(2)
                camera.issue_software_trigger()

                frame = camera.get_pending_frame_or_null()
                if frame is not None:
                    image_buffer_copy = np.copy(frame.image_buffer)
                    numpy_shaped_image = image_buffer_copy.reshape(camera.image_height_pixels, camera.image_width_pixels)
                    nd_image_array = np.full((camera.image_height_pixels, camera.image_width_pixels), 0, dtype=np.uint16)
                    nd_image_array[:,:] = numpy_shaped_image

                    if auto_contrast: 
                         print("#!TODO: Implement auto contrast")

                    return nd_image_array
                            

def save_image(input : np.ndarray, 
               capture_dir) -> str:
    try:
        filename = "capture_" + datetime.now().strftime("%y-%m-%d_%H-%M-%S") + ".tif"
        im_path = os.path.join(capture_dir, filename)
        cv2.imwrite(im_path, input)
        return im_path
    except: 
        raise Exception(f"Failed to write to {capture_dir}. Double check that this is a valid filepath?")

# Following code adapted from example code. 

# with TLCameraSDK() as sdk:
#     available_cameras = sdk.discover_available_cameras()
#     if len(available_cameras) < 1:
#         print("no cameras detected")

#     with sdk.open_camera(available_cameras[0]) as camera:
#         camera.exposure_time_us = 14000
#         camera.frames_per_trigger_zero_for_unlimited = 0  # start camera in continuous mode
#         camera.image_poll_timeout_ms = 1000  # 1 second polling timeout

#         camera.arm(2)

#         camera.issue_software_trigger()

#         frame = camera.get_pending_frame_or_null()
#         if frame is not None:
#             print("frame #{} received!".format(frame.frame_count))
#             image_buffer_copy = np.copy(frame.image_buffer)
#             numpy_shaped_image = image_buffer_copy.reshape(camera.image_height_pixels, camera.image_width_pixels)
#             nd_image_array = np.full((camera.image_height_pixels, camera.image_width_pixels), 0, dtype=np.uint16)
#             nd_image_array[:,:] = numpy_shaped_image
#             filename = "capture_" + datetime.now().strftime("%y-%m-%d_%H-%M-%S") + ".tif"
#             im_path = os.path.join(CAPTURE_DIR, filename)
#             cv2.imwrite(im_path, nd_image_array)

#         else:
#             print("Unable to acquire image, program exiting...")
#             exit()
            
#         cv2.waitKey(0)
#         camera.disarm()

# print("program completed")

save_image(capture_image())