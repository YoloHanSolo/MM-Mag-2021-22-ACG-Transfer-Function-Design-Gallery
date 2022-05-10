import numpy as np
import cv2
import math

class TransferFunctionGenerator:

    def __init__(self, path, bytes=1, dimensions=None) -> None:
        self.path = path
        self.bytes = bytes
        self.dimensions = dimensions
        self.volume = None
        self.transfer_function = None
        
    def loadRawVolume(self):
        volume = np.fromfile(self.path, dtype=np.uint8)
        volume = np.reshape(volume, self.dimensions[::-1])
        volume = np.moveaxis(volume, [0, 2], [2, 0])
        return volume

    def readDimensions(self):
        if self.dimensions:
            return self.dimensions
        dimensions_string = self.path.split("_")[1]
        return list(map(int, dimensions_string.split("x")))

    def getRgbRandom(self):
        return np.random.randint(0, 255, (3), dtype=np.uint8)

    def getRgbRange(self, min_val=0, max_val=255):
        return np.random.randint(
            max(min_val, 0),
            min(max_val, 255),
            (3), dtype=np.uint8)

    def generateRangeTF(self):
        transfer_function = {}
        for intensity in range(0, 256, 32):
            color = self.getRgbRange(intensity, intensity + 32)
            for each in range(intensity, intensity + 32):
                transfer_function[each] = color 
        return transfer_function   

    def generateHistogramTF(self, histogram):
        transfer_function = {}
        for index in range(len(histogram)-1):
            min_val = histogram[index]
            max_val = histogram[index+1]
            for value in range(min_val, max_val):
                transfer_function[value] = [histogram[index], histogram[index], histogram[index]]
        transfer_function[255] = [255, 255, 255]
        return transfer_function

    def generateRandomTF(self):
        transfer_function = {}
        for intensity in range(0, 256):
            transfer_function[intensity] = self.getRgbRandom()
        return transfer_function    

    def renderZ(self):
        for z in range(self.dimensions[2]):    
            layer_z = self.volume[:, :, z]      
            image = np.ndarray((self.dimensions[0], self.dimensions[1], 3), dtype=np.uint8)
            for ix in range(self.dimensions[0]):
                for iy in range(self.dimensions[1]):
                    pixel = layer_z[ix, iy]
                    image[ix, iy, :] = self.transfer_function[pixel]                          
            cv2.imshow("z-layer", image)
            cv2.waitKey(1)

    def getHistogram2D(self):
        mean_z = np.mean(self.volume, axis=2).astype(np.uint8)
        cv2.imshow("z-mean", mean_z)
        cv2.waitKey(1)
        histogram, edges = np.histogram(mean_z, bins=12)
        histogram = np.log(histogram)
        density = np.sum(histogram) / histogram
        density = (density - np.min(density)) / (np.max(density) - np.min(density))
        density = (density * 255).astype(np.uint8)
        print(edges)
        print(histogram)
        print(density)
        return density

filename = "raw/body_512x512x226_1x1x1_uint8.raw"
filename = "raw/engine_256x256x256_1x1x1_uint8.raw"

TFG = TransferFunctionGenerator(filename)

TFG.dimensions = TFG.readDimensions()
TFG.volume = TFG.loadRawVolume()
TFG.transfer_function = TFG.generateRandomTF()

histogram = TFG.getHistogram2D()

TFG.transfer_function = TFG.generateHistogramTF(histogram)

TFG.renderZ()    


    