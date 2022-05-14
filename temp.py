import numpy as np
import random
import json
import cv2

class TransferFunctionGenerator:

    # BINS -> 3 - 30
    # DROPOUT -> 0.0 - 0.3
    # POWER -> 2 - 10

    def __init__(self, max_opacity=0.3, min_value=100) -> None:
        self.max_opacity = max_opacity
        self.min_value = min_value

        self.bins = None
        self.dropout = None
        self.power = None
        self.feature_vector = None

    def generateFeature(self):
        pass

    def generateRandom(self, tf_index, bins):
        self.bins = bins 
        self.dropout = random.uniform(0.0, 0.3)
        self.power = random.randint(1, 5) * 2

        self.feature_vector = np.array([
            self.bins,
            self.dropout,
            self.power])

        transfer_function = {}

        step = 256 / self.bins
        for bin_index in range(self.bins):
            edge_min = int(step * bin_index)
            edge_max = int(step * (bin_index + 1))

            x = (edge_min + edge_max) / 2

            rgb = self.HSV2RGB(
                self._getHue(), 
                self._getSaturation(), 
                self._getValue(x))
            alpha = self._getOpacity(x, bin_index)

            print(self._getOpacity(x, bin_index))

            transfer_function[bin_index] = {
                "edge_min": edge_min,
                "edge_max": edge_max,
                "rgb": rgb,
                "alpha": alpha }

        vpt_tf_json = []
        for bin_index in range(self.bins):
            tf_bin = transfer_function[bin_index]
            edge_min = tf_bin["edge_min"]
            edge_max = tf_bin["edge_max"]
            color = tf_bin["rgb"]
            opacity = tf_bin["alpha"]
            size = 1 / 255
            for i in range(edge_min, edge_max):
                position = i / 255
                vpt_bump = self._VPTform(position, size, color, opacity)
                vpt_tf_json.append(vpt_bump)          

        with open("tf_{}.json".format(tf_index), 'w') as file:
            json.dump(vpt_tf_json, file)   

        print("{}: [{}, {}, {}]".format(tf_index, self.bins, self.dropout, self.power))

    def _VPTform(self, position, size, color, opacity):
        form = {
            "position": { "x": position, "y": position },
            "size": { "x": size, "y": 1 },
            "color": {
                "r": color[0] / 255,
                "g": color[1] / 255,
                "b": color[2] / 255,
                "a": opacity / 255 }}
        return form

    def HSV2RGB(self, hue, saturation, value):
        hsv = np.array([[[hue, saturation, value]]], dtype=np.uint8)
        rgb = cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR).flatten()
        return rgb

    def _getSaturation(self):
        return 255

    def _getHue(self):
        return random.randint(0, 255)

    def _getValue(self, x):
        fx = (((x / 255) - 1) ** self.power) * 255
        return max(fx, 100)

    def _getOpacity(self, x, bin_index):
        fx = ((x / 255) ** self.power) * 255
        if random.uniform(0, 1) < self.dropout:
            return 0
        elif bin_index == 0 or x <= 0.05: # IGNORE BACKGROUND NOISE
            return 0
        return min(fx, self.max_opacity * 255) 

TFG = TransferFunctionGenerator()

bins = 3
for tf_index in range(9):
    TFG.generate(tf_index, bins)
    bins += 3