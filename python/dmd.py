from load_dlpc350 import DLPC350
import time

obj = DLPC350()
obj.connectDLP()
print(obj.getHardwareStatus())

obj.loadImage(0)

for i in range(10):
    obj.loadImage(i)
    time.sleep(1)