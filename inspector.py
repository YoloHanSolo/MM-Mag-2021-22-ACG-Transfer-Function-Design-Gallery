import numpy as np
import cv2
import math
import random

class TransferFunctionGenerator:

    def __init__(self, path, dtype=np.uint8, dimensions=None) -> None:
        self.path = path
        self.dtype = dtype
        self.dimensions = dimensions
        self.volume = None
        self.transfer_function = None
        self.histogram = None
        self.edges = None
        self.features = None    
        
    def loadVolume(self):
        print(self.path)
        print("Volume Loading...")
        volume = np.fromfile(self.path, dtype=self.dtype)
        volume = np.reshape(volume, self.dimensions[::-1])
        volume = np.moveaxis(volume, [0, 2], [2, 0])
        self.mean_x = np.mean(volume, axis=0).astype(np.uint8)
        self.mean_y = np.mean(volume, axis=1).astype(np.uint8)
        self.mean_z = np.mean(volume, axis=2).astype(np.uint8)
        self.max_x = np.amax(volume, axis=0).astype(np.uint8)
        self.max_y = np.amax(volume, axis=1).astype(np.uint8)
        self.max_z = np.amax(volume, axis=2).astype(np.uint8)
        self.volume = volume
        print("Volume Loaded!")

    def setDimensions(self, dimensions=None):
        if dimensions:
            self.dimensions = dimensions
        else:
            dimensions_string = self.path.split("_")[1]
            self.dimensions = tuple(map(int, dimensions_string.split("x")))
        print(f"Dimensions: {self.dimensions[0]}x{self.dimensions[1]}x{self.dimensions[2]}")

    def getRgbRandom(self):
        return np.random.randint(0, 255, (3), dtype=np.uint8)

    def getRgbRange(self, min_val=0, max_val=255):
        if max_val == 0:
            max_val = 1
        if min_val >= max_val:
            min_val = max_val-1
        return np.random.randint(
            max(min_val, 0),
            min(max_val, 255),
            (3), dtype=np.uint8)

    def getHSVColor(self, h, s, v):
        return cv2.cvtColor(np.array([[[h, s, v]]], dtype=np.uint8), cv2.COLOR_HSV2BGR).flatten()

    """
    render
    """

    def renderZ(self):
        for z in range(self.dimensions[2]):    
            layer_z = self.volume[:, :, z]      
            image = np.ndarray((self.dimensions[0], self.dimensions[1], 3), dtype=np.uint8)
            for ix in range(self.dimensions[0]):
                for iy in range(self.dimensions[1]):
                    pixel = layer_z[ix, iy]
                    image[ix, iy, :] = self.transfer_function[pixel]     

            cv2.imshow("z-layer", cv2.resize(image, (self.dimensions[0], self.dimensions[1])))
            cv2.waitKey(1)

    def renderX(self):
        for x in range(self.dimensions[0]):    
            layer_x = self.volume[x, :, :]      
            image = np.ndarray((self.dimensions[1], self.dimensions[2], 3), dtype=np.uint8)
            for iy in range(self.dimensions[1]):
                for iz in range(self.dimensions[2]):
                    pixel = layer_x[iy, iz]
                    image[iy, iz, :] = self.transfer_function[pixel]                          
            cv2.imshow("x-layer", cv2.resize(image, (512, 512)))
            cv2.waitKey(1)

    def renderMean(self):
        cv2.imshow("mean_x", cv2.resize(self.mean_x, (self.dimensions[0], self.dimensions[1])))
        cv2.imshow("mean_y", cv2.resize(self.mean_y, (self.dimensions[0], self.dimensions[1])))
        cv2.imshow("mean_z", cv2.resize(self.mean_z, (self.dimensions[0], self.dimensions[1])))
        cv2.waitKey(0)

    """
    TF
    """
    
    def generateRangeTF(self):
        transfer_function = {}
        for intensity in range(0, 256, 32):
            color = self.getRgbRange(intensity, intensity + 32)
            for each in range(intensity, intensity + 32):
                transfer_function[each] = color 
        return transfer_function   

    def generateHistogramTF(self, bins):
        print("Generating hist TF...")

        #histogram = np.bincount(self.volume.flatten()) # calculate histogram
        histogram, edges = np.histogram(self.volume, bins=256)
        histogram = np.log(histogram + 1)
        histogram = histogram / np.max(histogram)
        histogram = (histogram * 255).astype(np.uint8) # cast to uint8

        if (histogram[0] == 255):
            histogram[0] = 0

        #import matplotlib.pyplot as plt
        #x = list(range(0, 256))
        #plt.plot(x, histogram, 'o')
        #plt.show()

        print(histogram)

        transfer_function = {}
        for bin_index, bin_value in enumerate(histogram):
            color = self.getHSVColor(bin_index, bin_value, bin_value)
            transfer_function[bin_index] = color

        self.transfer_function = transfer_function

    def generateRandomTF(self):
        transfer_function = {}
        for intensity in range(0, 256):
            transfer_function[intensity] = self.getRgbRandom()
        return transfer_function    

    def generatePreview(self):
        image = np.ndarray((self.dimensions[0], self.dimensions[1], 3), dtype=np.uint8)
        for iy in range(self.dimensions[0]):
            for iz in range(self.dimensions[1]):
                pixel = self.mean_z[iy, iz]
                image[iy, iz, :] = self.transfer_function[pixel]                          
        cv2.imshow("preview_z", image)
        cv2.waitKey(1)
        image = np.ndarray((self.dimensions[0], self.dimensions[1], 3), dtype=np.uint8)
        for iy in range(self.dimensions[0]):
            for iz in range(self.dimensions[1]):
                pixel = self.max_z[iy, iz]
                image[iy, iz, :] = self.transfer_function[pixel]                          
        cv2.imshow("preview_mz", image)
        cv2.waitKey(1)

        image = np.ndarray((self.dimensions[0], self.dimensions[1], 3), dtype=np.uint8)
        for iy in range(self.dimensions[0]):
            for iz in range(self.dimensions[1]):
                pixel = (self.max_z[iy, iz] + self.mean_z[iy, iz]) // 2
                image[iy, iz, :] = self.transfer_function[pixel]                          
        cv2.imshow("preview_gz", image)
        cv2.waitKey(1)

#filename = "raw/body_512x512x226_1x1x1_uint8.raw"
#filename = "raw/engine_256x256x256_1x1x1_uint8.raw"
#filename = "raw/mri_ventricles_256x256x124_1x1x1_uint8.raw"
filename = "raw/brain_512x512x230_5x5x9_uint8.raw"




TFG = TransferFunctionGenerator(filename)
#TFG.setDimensions((256,256,124))
TFG.setDimensions()
TFG.loadVolume()
#TFG.renderMean()
#TFG.generateRandomTF()
TFG.generateHistogramTF(256)
TFG.generatePreview()
TFG.renderZ()
#TFG.renderX()  


