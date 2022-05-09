import numpy as np
import cv2

filename = "sample.vpt"

typeBytes = 1

dimensions = (128, 128, 64)


values = np.ndarray(dimensions, dtype=np.uint8)

file = open(filename, "rb")
byte = True

i_x, i_y, i_z = 0, 0, 0


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

while byte:
    byte = file.read(typeBytes)

    uint_value = int.from_bytes(byte, byteorder='little') #int(byte, 16)
              
    values[i_x, i_y, i_z] = uint_value
       
    i_x += 1
    if i_x == dimensions[0]:
        i_y += 1
        i_x = 0
        print(f"{i_x} {i_y} {i_z}")
        
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
    
    
    
    