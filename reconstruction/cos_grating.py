"""
Python port of cos_grating.m

Generates a rotated cosine grating, center-cropped to a requested size.
"""
import math

import cv2
import numpy as np


def _imrotate_nearest_loose(image: np.ndarray, angle: float) -> np.ndarray:
    """
    Equivalent of MATLAB's imrotate(image, angle) with its defaults:
    nearest-neighbour interpolation, 'loose' bounding box (output grows to
    hold the whole rotated image), zero fill. Positive angle = counterclockwise.
    """
    # MATLAB special-cases multiples of 90 degrees with rot90 (exact, no
    # interpolation). np.rot90 is also counterclockwise for positive k.
    if angle % 90 == 0:
        return np.rot90(image, k=int(angle // 90) % 4).copy()

    h, w = image.shape[:2]
    theta = math.radians(angle)
    cos_t, sin_t = abs(math.cos(theta)), abs(math.sin(theta))

    # Size of the 'loose' bounding box (small tolerance guards against
    # floating-point error pushing ceil() up by one pixel).
    new_w = int(math.ceil(w * cos_t + h * sin_t - 1e-9))
    new_h = int(math.ceil(w * sin_t + h * cos_t - 1e-9))

    # Rotate about the image centre, then shift so the result is centred in
    # the enlarged output canvas.
    center = ((w - 1) / 2.0, (h - 1) / 2.0)
    rot_mat = cv2.getRotationMatrix2D(center, angle, 1.0)
    rot_mat[0, 2] += (new_w - 1) / 2.0 - center[0]
    rot_mat[1, 2] += (new_h - 1) / 2.0 - center[1]

    return cv2.warpAffine(image, rot_mat, (new_w, new_h),
                          flags=cv2.INTER_NEAREST,
                          borderMode=cv2.BORDER_CONSTANT,
                          borderValue=0)


def _center_crop(image: np.ndarray, output_size) -> np.ndarray:
    """
    Equivalent of imcrop(image, centerCropWindow2d(size(image), output_size)).
    output_size is (rows, cols), the same order as numpy's .shape.
    """
    out_h, out_w = int(output_size[0]), int(output_size[1])
    in_h, in_w = image.shape[:2]
    if out_h > in_h or out_w > in_w:
        raise ValueError(f"Crop size {(out_h, out_w)} is larger than image size {(in_h, in_w)}.")

    top = (in_h - out_h) // 2
    left = (in_w - out_w) // 2
    return image[top:top + out_h, left:left + out_w]


def cos_grating(angle: float,
                output_size,
                grating_wavelength: float,
                phase_shift: float) -> np.ndarray:
    """
    Parameters
    ----------
    angle              : grating rotation in degrees (counterclockwise)
    output_size        : (rows, cols) of the returned image, e.g. image.shape
    grating_wavelength : period of the grating in pixels
    phase_shift        : phase offset of the grating in radians

    Returns
    -------
    float64 array of shape output_size with values in [0, 1]
    """
    n = 5000

    # MATLAB's index = 1:5000 is 1-based; keep it 1-based so the grating
    # phase at every pixel matches the MATLAB output exactly.
    index = np.arange(1, n + 1)
    i_cos = 0.5 + 0.5 * np.cos((2 * np.pi * index) / grating_wavelength + phase_shift)

    # Every row is the same 1-D cosine profile (replaces the MATLAB for-loop).
    i_full = np.tile(i_cos, (n, 1))

    i_rotated = _imrotate_nearest_loose(i_full, angle)
    return _center_crop(i_rotated, output_size)
