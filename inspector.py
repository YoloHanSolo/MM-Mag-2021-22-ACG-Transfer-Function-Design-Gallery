import numpy as np
import cv2
import math

filename = "sample.vpt"

typeBytes = 1

dimensions = (128, 128, 64)


values = np.ndarray(dimensions, dtype=np.uint8)

file = open(filename, "rb")
byte = True

i_x, i_y, i_z = 0, 0, 0

def getRandomColor(maxv):
    high = maxv+maxv*math.log(maxv)+1
    low = maxv-maxv*math.log(maxv)
    rand = np.random.randint(max(0,low), high=min(255,high), size=(3), dtype=np.uint8)
    return rand

"""
transferFunction = {
    32: [0, 0, 0],
    64: [128, 0, 0],
    92: [255, 0, 0],
    128: [128, 128, 0],
    160: [0, 255, 0],
    192: [0, 128, 128],
    224: [0, 0, 255],
    256: [255, 255, 255],
}
"""

print(getRandomColor(256))

"""
transferFunction = {
    32: getRandomColor(32),
    64: getRandomColor(64),
    92: getRandomColor(92),
    128: getRandomColor(128),
    160: getRandomColor(160),
    192: getRandomColor(192),
    224: getRandomColor(224),
    256: getRandomColor(256)
}
"""
transferFunction = {}
for val in range(1, 255):
    transferFunction[val] = getRandomColor(val)

while byte:
    byte = file.read(typeBytes)

    uint_value = int.from_bytes(byte, byteorder='little') #int(byte, 16)
              
    values[i_x, i_y, i_z] = uint_value
       
    i_x += 1
    if i_x == dimensions[0]:
        i_y += 1
        i_x = 0
        
    if i_y == dimensions[1]:
        i_z += 1
        i_y = 0
        
    if i_z == dimensions[2]:
        break

for i in range(dimensions[2]):    
    zlayer = values[:,:,i]
    
    image = np.ndarray((dimensions[0], dimensions[1], 3), dtype=np.uint8)
 
    for ix in range(dimensions[0]):
        for iy in range(dimensions[1]):
            voxel = zlayer[ix, iy]
            for key, value in transferFunction.items():

                if voxel < key:
                    image[ix, iy, :] = value
                    break
                    
    cv2.imshow("z-layer", image)
    cv2.waitKey(1)
    
    
    
    