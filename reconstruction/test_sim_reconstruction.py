"""
Partial reconstruction code
based on paper by Chen et al
Eric Hall

Python port of test_sim_reconstruction.m
"""
import os

import cv2
import matplotlib.pyplot as plt
import numpy as np

from cos_grating import cos_grating

# Resolve image paths relative to this file (same convention as capture.py)
FILE_DIR = os.path.dirname(os.path.abspath(__file__))


# ---------------------------------------------------------------------------
# Helpers replicating MATLAB Image Processing Toolbox functions
# ---------------------------------------------------------------------------
def imread(path: str, flags: int = cv2.IMREAD_UNCHANGED) -> np.ndarray:
    """cv2.imread, but raise instead of silently returning None."""
    image = cv2.imread(path, flags)
    if image is None:
        raise FileNotFoundError(f"Could not read image at {path}.")
    return image


def rgb2gray(image: np.ndarray) -> np.ndarray:
    """
    MATLAB rgb2gray. Expects an OpenCV-loaded image (BGR or BGRA channel
    order) and uses MATLAB's exact luminance weights. Integer inputs are
    rounded back to their original dtype, as MATLAB does.
    """
    if image.ndim == 2:
        return image  # already single-channel
    b = image[:, :, 0].astype(np.float64)
    g = image[:, :, 1].astype(np.float64)
    r = image[:, :, 2].astype(np.float64)  # any alpha channel (index 3) is ignored
    gray = 0.298936021293775 * r + 0.587043074451121 * g + 0.114020904255103 * b

    if np.issubdtype(image.dtype, np.integer):
        info = np.iinfo(image.dtype)
        return np.clip(np.round(gray), info.min, info.max).astype(image.dtype)
    return gray


def mat2gray(a: np.ndarray) -> np.ndarray:
    """MATLAB mat2gray: linearly rescale to [0, 1] as float64."""
    a = np.asarray(a, dtype=np.float64)
    a_min, a_max = a.min(), a.max()
    if a_max == a_min:
        return np.clip(a, 0.0, 1.0)  # MATLAB's behaviour for a constant image
    return np.clip((a - a_min) / (a_max - a_min), 0.0, 1.0)


def imtranslate(a: np.ndarray, translation) -> np.ndarray:
    """
    MATLAB imtranslate(a, [tx ty]) with default 'same' output view and zero
    fill. Positive tx shifts right (columns), positive ty shifts down (rows).
    Works on real or complex arrays.
    """
    tx, ty = float(translation[0]), float(translation[1])

    # Whole-pixel shift: exact copy with zero fill (MATLAB's fast path).
    if tx.is_integer() and ty.is_integer():
        tx, ty = int(tx), int(ty)
        h, w = a.shape[:2]
        out = np.zeros_like(a)
        if abs(tx) >= w or abs(ty) >= h:
            return out
        src_r = slice(max(0, -ty), h - max(0, ty))
        src_c = slice(max(0, -tx), w - max(0, tx))
        dst_r = slice(max(0, ty), h - max(0, -ty))
        dst_c = slice(max(0, tx), w - max(0, -tx))
        out[dst_r, dst_c] = a[src_r, src_c]
        return out

    # Sub-pixel shift: bilinear interpolation (MATLAB default 'linear').
    # OpenCV has no complex support, so real and imaginary parts are shifted
    # separately.
    h, w = a.shape[:2]
    shift_mat = np.float64([[1, 0, tx], [0, 1, ty]])

    def _shift(real_part):
        return cv2.warpAffine(real_part.astype(np.float64), shift_mat, (w, h),
                              flags=cv2.INTER_LINEAR,
                              borderMode=cv2.BORDER_CONSTANT,
                              borderValue=0)

    if np.iscomplexobj(a):
        return _shift(a.real) + 1j * _shift(a.imag)
    return _shift(a)


def fft2c(a: np.ndarray) -> np.ndarray:
    """fftshift(fft2(a))"""
    return np.fft.fftshift(np.fft.fft2(a))


def ifft2c(a: np.ndarray) -> np.ndarray:
    """ifft2(ifftshift(a))"""
    return np.fft.ifft2(np.fft.ifftshift(a))


# ---------------------------------------------------------------------------
# Main script
# ---------------------------------------------------------------------------
plt.close("all")

gray_duck = rgb2gray(imread(os.path.join(FILE_DIR, "duck.png")))
gray_duck = mat2gray(gray_duck[:, :-30])
duck_fft = fft2c(gray_duck)
perfect_reconstruct = imread(os.path.join(FILE_DIR, "perfect_reconstruct.png"))

# The frequency-domain mask below is hard-coded for a 220 x 220 image
# (meshgrid(-110:109)), exactly as in the MATLAB version.
assert gray_duck.shape == (220, 220), (
    f"Expected a 220x220 image after cropping, got {gray_duck.shape}. "
    "The meshgrid range and centre index (110, 110) assume 220x220."
)

# %% 3 Angles with 3 phases

phases = np.array([0, 2 * np.pi / 3, 4 * np.pi / 3])

I_0 = 1
cos_0 = 0.5

M_array = np.array([
    [I_0, cos_0 * np.exp(-1j * phases[0]), cos_0 * np.exp(1j * phases[0])],
    [I_0, cos_0 * np.exp(-1j * phases[1]), cos_0 * np.exp(1j * phases[1])],
    [I_0, cos_0 * np.exp(-1j * phases[2]), cos_0 * np.exp(1j * phases[2])],
])

M_inverse = np.linalg.inv(M_array)

cos_wavelength = 11
approximate_transfer = 220 / cos_wavelength

H_function = np.ones(gray_duck.shape)

x, y = np.meshgrid(np.arange(-110, 110), np.arange(-110, 110))

H_function[np.sqrt(x ** 2 + y ** 2) > approximate_transfer] = 0
positive_overlap = H_function + imtranslate(H_function, [approximate_transfer, 0])
positive_overlap[positive_overlap < 2] = 0
positive_overlap[positive_overlap > 0] = 1

negative_overlap = H_function + imtranslate(H_function, [-approximate_transfer, 0])
negative_overlap[negative_overlap < 2] = 0
negative_overlap[negative_overlap > 0] = 1

weight_filter = (H_function
                 + imtranslate(H_function, [approximate_transfer, 0])
                 + imtranslate(H_function, [-approximate_transfer, 0]))

freq_support = weight_filter.copy()  # .copy(): numpy assignment is by reference
freq_support[freq_support > 0] = 1
weight_filter[weight_filter == 0] = 1

# %%
# 0 deg

angle_0_phase_0 = cos_grating(0, gray_duck.shape, cos_wavelength, phases[0]) * gray_duck
angle_0_phase_120 = cos_grating(0, gray_duck.shape, cos_wavelength, phases[1]) * gray_duck
angle_0_phase_240 = cos_grating(0, gray_duck.shape, cos_wavelength, phases[2]) * gray_duck

test = (angle_0_phase_0 - gray_duck
        + angle_0_phase_120 - gray_duck
        + angle_0_phase_240 - gray_duck)

angle_0_phase_0_fft = fft2c(angle_0_phase_0) * H_function
angle_0_phase_120_fft = fft2c(angle_0_phase_120) * H_function
angle_0_phase_240_fft = fft2c(angle_0_phase_240) * H_function

# MATLAB M_inverse(r,c) -> numpy M_inverse[r-1, c-1]
S_0 = 2 * (M_inverse[0, 0] * angle_0_phase_0_fft
           + M_inverse[0, 1] * angle_0_phase_120_fft
           + M_inverse[0, 2] * angle_0_phase_240_fft)
S_P_1 = 2 * (M_inverse[1, 0] * angle_0_phase_0_fft
             + M_inverse[1, 1] * angle_0_phase_120_fft
             + M_inverse[1, 2] * angle_0_phase_240_fft)
S_P_1 = imtranslate(S_P_1, [approximate_transfer, 0])
S_N_1 = 2 * (M_inverse[2, 0] * angle_0_phase_0_fft
             + M_inverse[2, 1] * angle_0_phase_120_fft
             + M_inverse[2, 2] * angle_0_phase_240_fft)
S_N_1 = imtranslate(S_N_1, [-approximate_transfer, 0])

# %% We cannot add the structures just yet. We need phase shift
# MATLAB (111,111) is the DC term after fftshift -> numpy [110, 110]

phase_shift_P = np.angle(S_P_1[110, 110]) - np.angle(S_0[110, 110])
S_P_1 = np.abs(S_P_1) * np.exp(1j * (np.angle(S_P_1) - phase_shift_P))

phase_shift_n = np.angle(S_N_1[110, 110]) - np.angle(S_0[110, 110])
S_N_1 = np.abs(S_N_1) * np.exp(1j * (np.angle(S_N_1) - phase_shift_n))

S_all = S_0 + S_P_1 + S_N_1
S_weighted = S_all / weight_filter

fft_weighted = mat2gray(np.abs(S_weighted))


# %% Reconstruct

reconstruction = np.abs(ifft2c(S_weighted))
blurry = np.abs(ifft2c(S_0))

# imshowpair(..., "montage") scales each image independently to [0, 1]
# and places them side by side.
plt.figure()
plt.imshow(np.hstack([mat2gray(blurry), mat2gray(reconstruction)]),
           cmap="gray", vmin=0, vmax=1)
plt.title("Blurry (left) vs Partial Reconstruction")
plt.axis("off")

# MATLAB imshow on a double image clips to [0, 1]; vmin/vmax reproduce that,
# so scale_factor saturates bright values exactly as in the original.
plt.figure()
scale_factor = 30
plt.subplot(1, 3, 1)
plt.imshow(mat2gray(np.abs(S_0)) * scale_factor, cmap="gray", vmin=0, vmax=1)
plt.title("Blurry FFT")
plt.axis("off")

plt.subplot(1, 3, 2)
plt.imshow(fft_weighted * scale_factor, cmap="gray", vmin=0, vmax=1)
plt.title("Weighted Reconstruction FFT")
plt.axis("off")

plt.subplot(1, 3, 3)
test_diff = np.abs(S_weighted) - np.abs(duck_fft)
plt.imshow(mat2gray(np.abs(duck_fft - S_0)) * scale_factor, cmap="gray", vmin=0, vmax=1)
plt.title("Comparison. Center Should be near zero")
plt.axis("off")

plt.show()
