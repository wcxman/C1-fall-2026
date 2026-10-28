# SYSTEM REQUIREMENTS
* 64-bit Windows Installation
* Python 3.8 or later
* Ability to connect two USB-A peripherals to your device

# ONE-TIME SETUP INSTRUCTIONS
1. If you haven't already, download this project with `git clone https://github.com/wcxman/C1-fall-2026.git` in the folder you would like to download the project to. 
2. Go to https://www.thorlabs.com/software-pages/ThorCam and navigate to the `Programming Interfaces` tab. From there, download the Windows SDK. 
3. After downloading and unzipping `scientific_camera_interfaces-[VERSION_NUMBER]-[DATE]`, navigate to `scientific_camera_interfaces-[VERSION_NUMBER]-[DATE]\Scientific Camera Interfaces\SDK\Python Toolkit`. In this folder there will be a zip file named `thorlabs_tsi_camera_python_sdk_package.zip`. Copy that zip file into this repository. Do not unzip it. The copied zip file's path should be: `C:\\Path\To\C1-fall-2026\thorlabs_tsi_camera_python_sdk_package.zip`. 
4. Copy the DLL files found in `scientific_camera_interfaces-[VERSION_NUMBER]-[DATE]\Scientific Camera Interfaces\SDK\Native Toolkit\dlls\Native_64_lib` into the `dlls` folder in this repository. 
5. In powershell, navigate to this directory with `cd C:\\Path\To\C1-fall-2026`. Next, run `python -m venv .venv`. This initializes a python virtual environment.
6. Activate the virtual environment by running `.\.venv\Scripts\Activate.ps1` in powershell. After running that command, you will be in the virtual environment. Run `pip install -r requirements.txt` in powershell to install the correct dependency versions in the virtual environment. 

# HOW TO USE
1. Make sure that the above one-time instructions have been completed.
2. In powershell, navigate to this directory with `cd C:\\Path\To\C1-fall-2026` and activate the python virtual environment with `.\.venv\Scripts\Activate.ps1`.
3. Run `python python/capture.py` to capture ten images in series. These images will be saved in `captures/capture_[yr]-[mo]-[day]_[hr]-[min]-[sec]-[usec].tif`. 

Note: Because the ThorLabs camera has a 10 bit sensor but most image processing softwares don't accept 10-bit .tif files, we instead cast our 10 bits of data into a 16-bit .tif file. If `shift_left` is passed as true to `capture_image()`, these 10 bits of data will occupy bits 6-15 of a 16-bit pixel value. Otherwise, they will occupy bits 0-9, which results in what appears to be an all-black image. If this image is put into photoshop or another image processing software and auto-contrasted, the expected data will appear.

# CONTRIBUTING
Thank you for contributing to this project! Some guidelines are given below:
* If new python code adds dependencies, reflect this in `requirements.txt`. Run `pip freeze > requirements2.txt` to generate a new requirements text file, then replace everything but the line containing `./thorlabs_tsi_camera_python_sdk_package.zip` with every line in `requirements2.txt` except the line containing that zip file. Afterwards, make sure to delete `requirements2.txt` or whatever intermediate file you use. 
* Any artifacts from code execution, such as captures, cache files, etc. should be added to `.gitignore` so they are not pushed to the repository. This keeps the repository clean!


# Physical setup notes !TODO: REMOVE THIS?
- DMD lens to middle of standalone lens is 8.5 cm
- Standalone lens to pixel array (a bit past filter base) is 6.5 cm

# Acknowledgements 
- First and foremost, we would like to thank Dr. Charles DiMarzio for overlooking this project and his valuable insight throughout the entire process. 
- Eric Hall for all of his help in the lab and with the reconstruction algorithm.
- Francesco Valla for their dlpc350 library, which we are using under LGPL v3. 