import os
import numpy as np
import cv2
from datetime import datetime

from thorlabs_tsi_sdk.tl_camera import TLCamera

def init_camera(camera           : TLCamera,
                exposure_time_us : int  = 14000, 
                timeout_ms       : int  = 1000):
    camera.exposure_time_us = exposure_time_us # Default 14 ms exposure time
    camera.frames_per_trigger_zero_for_unlimited = 0  # start camera in continuous mode
    camera.image_poll_timeout_ms = timeout_ms  # Default 1 second polling timeout
    camera.arm(2)
    camera.issue_software_trigger()


def capture_image(camera     : TLCamera, 
                  shift_left : bool = False) -> np.ndarray:
    frame = camera.get_pending_frame_or_null()
    if frame is not None:
        image_buffer_copy = np.copy(frame.image_buffer)
        numpy_shaped_image = image_buffer_copy.reshape(camera.image_height_pixels, camera.image_width_pixels)
        nd_image_array = np.full((camera.image_height_pixels, camera.image_width_pixels), 0, dtype=np.uint16)
        nd_image_array[:,:] = numpy_shaped_image

        if shift_left: 
            nd_image_array = nd_image_array << 6
            print("Max:", np.max(nd_image_array))

        return nd_image_array
                            

def save_image(input : np.ndarray, 
               capture_dir) -> str:
    try:
        filename = "capture_" + datetime.now().strftime("%y-%m-%d_%H-%M-%S-%f") + ".tif"
        im_path = os.path.join(capture_dir, filename)
        cv2.imwrite(im_path, input)
        return im_path
    except: 
        raise Exception(f"Failed to write to {capture_dir}. Double check that this is a valid filepath?")