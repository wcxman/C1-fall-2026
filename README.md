# SYSTEM REQUIREMENTS
* 64-bit Windows Installation
* Python 3.8 or later

# ONE-TIME SETUP INSTRUCTIONS
1. Go to https://www.thorlabs.com/software-pages/ThorCam and navigate to the `Programming Interfaces` tab. From there, download the Windows SDK. 
2. After downloading and unzipping `scientific_camera_interfaces-[VERSION_NUMBER]-[DATE]`, navigate to `scientific_camera_interfaces-[VERSION_NUMBER]-[DATE]\Scientific Camera Interfaces\SDK\Python Toolkit`. In this folder there will be a zip file named `thorlabs_tsi_camera_python_sdk_package.zip`. Copy that zip file into this repository. Do not unzip it. The copied zip file's path should be: `C:\\Path\To\C1-fall-2026\thorlabs_tsi_camera_python_sdk_package.zip`. 
3. Copy the DLL files found in `scientific_camera_interfaces-[VERSION_NUMBER]-[DATE]\Scientific Camera Interfaces\SDK\Native Toolkit\dlls\Native_64_lib` into the `dlls` folder in this repository. 
4. In powershell, navigate to this directory with `cd C:\\Path\To\C1-fall-2026`. Next, run `python -m venv .venv`. This initializes a python virtual environment.
5. Activate the virtual environment by running `.\.venv\Scripts\Activate.ps1` in powershell. After running that command, you will be in the virtual environment. Run `pip install -r requirements.txt` in powershell to install the correct dependency versions in the virtual environment. 

# HOW TO USE
1. Make sure that the above one-time instructions have been completed.
2. In powershell, navigate to this directory with `cd C:\\Path\To\C1-fall-2026` and activate the python virtual environment with `.\.venv\Scripts\Activate.ps1`.
3. Run `python python/camera.py` to capture a single image. This image will be saved in `captures/capture_[yr]-[mo]-[day]_[hr]-[min]-[sec].tif`. 
Note: The image will likely appear to be entirely black. This is because the camera we are using captures with 10-bit depth, but we save into a 16-bit TIFF file. In Photoshop, open the .tif file and use the "Auto Contrast" tool. In other photo editors, you may need to adjust the contrast manually. Keep increasing the contrast until you can see the details of the photo! You may need to increase the contrast *a lot* to see the image. 

# Physical setup notes
- DMD lens to middle of standalone lens is 8.5 cm
- Standalone lens to pixel array (a bit past filter base) is 6.5 cm

# Upcoming Goals: 
- Finalize a schematic
- Finish reconstruction algorithms