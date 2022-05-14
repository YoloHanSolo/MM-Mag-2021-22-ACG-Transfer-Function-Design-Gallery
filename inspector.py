from cv2 import minEnclosingTriangle
import numpy as np
import cv2
import matplotlib.pyplot as plt
import random
import json


class RGBA:

    def __init__(self, r, g, b, a) -> None:
        self.r = r
        self.g = g
        self.b = b
        self.a = a
        self.color = np.array([r,g,b,a], dtype=np.uint8)

    def get(self):
        return self.color

class TransferFunctionGenerator:

    def __init__(self, path, dtype=np.uint8) -> None:
        self.path = path
        self.dtype = dtype

        self.dimensions = None
        self.volume = None

        self.bins = 256
        self.histogram_raw = None
        self.histogram = None
        self.edges = None

        self.hue_tracker = None

        self.transfer_function = None

    def setDimensions(self, dimensions=None):
        if dimensions:
            self.dimensions = dimensions
        else:
            dimensions_string = self.path.split("_")[1]
            self.dimensions = tuple(map(int, dimensions_string.split("x")))

    def loadVolume(self):
        volume = np.fromfile(self.path, dtype=self.dtype)
        volume = np.reshape(volume, self.dimensions[::-1])
        volume = np.moveaxis(volume, [0, 2], [2, 0])
        self.volume = volume

    def getVolumeStatisticalProperties(self, display=False):
        self.mean_x = np.mean(self.volume, axis=0).astype(np.uint8)
        self.mean_y = np.mean(self.volume, axis=1).astype(np.uint8)
        self.mean_z = np.mean(self.volume, axis=2).astype(np.uint8)
        self.max_x = np.amax(self.volume, axis=0).astype(np.uint8)
        self.max_y = np.amax(self.volume, axis=1).astype(np.uint8)
        self.max_z = np.amax(self.volume, axis=2).astype(np.uint8)
        self.min_x = np.amin(self.volume, axis=0).astype(np.uint8)
        self.min_y = np.amin(self.volume, axis=1).astype(np.uint8)
        self.min_z = np.amin(self.volume, axis=2).astype(np.uint8)
        if display:
            img_mean = np.concatenate((self.mean_x, self.mean_y), axis=1)
            img_mean = np.concatenate((img_mean, self.mean_z), axis=1)
            img_max = np.concatenate((self.max_x, self.max_y), axis=1)
            img_max = np.concatenate((img_max, self.max_z), axis=1)
            img_min = np.concatenate((self.min_x, self.min_y), axis=1)
            img_min = np.concatenate((img_min, self.min_z), axis=1)
            cv2.imshow("mean", img_mean)
            cv2.imshow("max", img_max)
            cv2.imshow("min", img_min)
            cv2.waitKey(0)

    def HSV2RGB(self, hue, saturation, value):
        hsv = np.array([[[hue, saturation, value]]], dtype=np.uint8)
        rgb = cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR).flatten()
        return rgb

    """
    TF
    """

    def getVolumeHistogramRaw(self): # USELESS FIX TODO
        histogram, edges = np.histogram(self.volume, bins=256)
        self.histogram_raw = histogram

    def getVolumeHistogramProcessed(self, bins, display=False):       
        histogram, edges = np.histogram(self.volume, bins=bins) # FIX TODO
        # BG noise cut
        cutoff_limit = np.average(histogram) / 2
        for bin in range(bins-1, 0, -1):
            dy = histogram[bin-1] - histogram[bin]
            if dy > cutoff_limit: 
                histogram[bin-1] = 0
        histogram = np.log(histogram + 1)
        histogram = histogram / np.max(histogram)
        histogram = (histogram * 255).astype(np.uint8)
        self.histogram = histogram
        self.edges = edges
        self.bins = bins
        if display:
            plt.plot(
                list(range(0, bins)),
                histogram, 'o')
            plt.show()

    def getSaturation(self):
        x = random.uniform(0, 1)
        y = (1 / (2*x + 1)) * 255 
        return 255
        #return max(min(255, y), 0)

    def getHue(self):
        scaling = 256 // self.bins
        offset = random.randint(scaling, scaling)
        self.hue_tracker = (self.hue_tracker + offset) % 256 
        return self.hue_tracker

    def getValue(self, value):
        return max((((value / 255) - 1) ** 4) * 255, 100)

    def getOpacity(self, value):
        return min(((value / 255) ** 4) / 1.5, 0.3) * 255

    def get1DTransferFunction(self, display=False):
        transfer_function = {}
        self.hue_tracker = random.randint(0, 255)
        for bin_index, bin_value in enumerate(self.histogram):
            border_min = round(self.edges[bin_index])
            border_max = round(self.edges[bin_index+1]) + 1
            color = self.HSV2RGB(
                self.getHue(), 
                self.getSaturation(), 
                self.getValue(border_max))
            opacity = 0
            if random.uniform(0, 1) > min(0.02 * self.bins, 0.7): # DROPOUT
                opacity = self.getOpacity(border_min)
            rgba = [color[2], color[1], color[0], opacity]
            for pixel_val in range(border_min, border_max):
                transfer_function[pixel_val] = rgba
        self.transfer_function = transfer_function

        if display:
            TF_2D = np.ndarray((256,256,4), dtype=np.uint8)
            for pixel_val in range(256):
                TF_2D[:, pixel_val, 0] = self.transfer_function[pixel_val][2]
                TF_2D[:, pixel_val, 1] = self.transfer_function[pixel_val][1]
                TF_2D[:, pixel_val, 2] = self.transfer_function[pixel_val][0]
                TF_2D[:, pixel_val, 3] = self.transfer_function[pixel_val][3]
            cv2.imshow("TF_2D_rgb", TF_2D[:, :, 0:3])
            cv2.imshow("TF_2D_alpha", TF_2D[:, :, 3])
            cv2.waitKey(1)

    def _vptBumpForm(self, index, color):
        form = {
            "position": { "x": index / 256, "y": index / 256 },
            "size": { "x": 1 / 256, "y": 1 },
            "color": {
                "r": color[0] / 255,
                "g": color[1] / 255,
                "b": color[2] / 255,
                "a": color[3] / 255 }}
        return form

    def saveTransferFunctionVPT(self, name):
        TF_json = []
        prev_val = None
        for pixel_val in range(256):
            TF_json.append(
                self._vptBumpForm(pixel_val, self.transfer_function[pixel_val]))

            prev_val = self.transfer_function[pixel_val]

        with open(name + '.json', 'w') as file:
            json.dump(TF_json, file)

    """
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
    """

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
                    image[ix, iy, :] = self.transfer_function[pixel][0:3]     
            cv2.imshow("z-layer", cv2.resize(image, (self.dimensions[0], self.dimensions[1])))
            cv2.waitKey(1)

#filename = "raw/body_512x512x226_1x1x1_uint8.raw"
filename = "raw/engine_256x256x256_1x1x1_uint8.raw"
#filename = "raw/mri_ventricles_256x256x124_1x1x1_uint8.raw"
#filename = "raw/brain_512x512x230_5x5x9_uint8.raw"

TFG = TransferFunctionGenerator(filename)
TFG.setDimensions() #TFG.setDimensions((256,256,124))
TFG.loadVolume()
TFG.getVolumeStatisticalProperties(display=False)
TFG.getVolumeHistogramRaw()

bins = 3
for tf in range(9):
    TFG.getVolumeHistogramProcessed(bins=bins, display=False)
    TFG.get1DTransferFunction(display=False)
    TFG.saveTransferFunctionVPT(name="transfer_function_{}".format(tf))
    bins = bins + 2

#TFG.generatePreview()
#TFG.renderZ()


"""
bins
dropout 
power?
"""