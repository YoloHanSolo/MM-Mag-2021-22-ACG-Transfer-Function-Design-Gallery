import numpy as np
import random
import cv2

class TransferFunctionGenerator:

    def __init__(self, filename, max_opacity = 0.3, min_value = 100):
        self.path = "raw/" + filename
        self.max_opacity = max_opacity
        self.min_value = min_value

        # range 3 -> 30
        # range 0.0 -> 0.3
        # power 2 -> 10

    def exploreTransferFunctions(self, feature_vector):

        origin_bins = feature_vector["bins"]
        origin_dropout = feature_vector["dropout"]
        origin_power = feature_vector["power"]
        origin_level = feature_vector["level"]
        origin_seed = feature_vector["seed"]

        random.seed(origin_seed)
        origin_tf = self.generateRandomTransferFunction(origin_bins, origin_dropout, origin_power, origin_level, origin_seed)

        seeds = []
        for _ in range(8):
            seeds.append(random.randint(0, 255))

        data = [origin_tf]
        for index in range(8):
            seed = seeds[index]
            random.seed(seed)
            bins = origin_bins + random.randint(-10 // origin_level, 10 // origin_level)
            bins = max(2, min(30, bins))
            dropout = origin_dropout + random.uniform(-0.1, 0.1)
            dropout = max(0.0, min(0.5, dropout))
            power = origin_power + random.randint(-4 // origin_level, 4 // origin_level) * 2
            dropout = max(0.0, min(0.5, dropout))
            level = origin_level + 1
            random.seed(seed)
            explore_tf = self.generateRandomTransferFunction(bins, dropout, power, level, seed)   
            data.append(explore_tf)
        return data

    def generateInitialTransferFunctions(self):
        seeds = []
        for _ in range(9):
            seeds.append(random.randint(0, 255))

        data = []
        for index, bins in enumerate(range(3, 30, 3)): 
            seed = seeds[index]
            random.seed(seed) 
            dropout = random.uniform(0.0, 0.3)
            power = random.randint(1, 5) * 2
            level = 1   
            random.seed(seed)   
            random_tf = self.generateRandomTransferFunction(bins, dropout, power, level, seed)
            data.append(random_tf)
        return data

    def generateRandomTransferFunction(self, bins, dropout, power, level, seed):

        feature_vector = {
            "bins": bins,
            "dropout": dropout,
            "power": power,
            "level": level,
            "seed": seed
        }

        transfer_function = {}

        step = 256 / bins
        prev_bin_dropout = False
        for bin_index in range(bins):
            edge_min = int(step * bin_index)
            edge_max = int(step * (bin_index + 1))
            x = (edge_min + edge_max) / 2

            rgb = self.HSV2RGB(
                self._getHue(), 
                self._getSaturation(), 
                self._getValue(x, power))
            alpha = self._getOpacity(x, bin_index, power, dropout, prev_bin_dropout)

            if alpha == 0:
                prev_bin_dropout = True
            else:
                prev_bin_dropout = False

            transfer_function[bin_index] = {
                "edge_min": edge_min,
                "edge_max": edge_max,
                "rgb": rgb,
                "alpha": alpha }

        vpt_tf_json = []
        for bin_index in range(bins):
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

        tf = {
            "feature_vector": feature_vector,
            "transfer_function": vpt_tf_json
        }

        return tf
        

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

    def _getValue(self, x, power):
        fx = (((x / 255) - 1) ** power) * 255
        return max(fx, 100)

    def _getOpacity(self, x, bin_index, power, dropout, prev_bin_dropout):
        fx = ((x / 255) ** power) * 255
        if random.uniform(0, 1) < dropout and not prev_bin_dropout:
            return 0
        elif bin_index == 0 or x <= 0.05: # IGNORE BACKGROUND NOISE
            return 0
        return min(fx, self.max_opacity * 255) 

    def generateTransferFunctionsPreview(self, data):
        dimensions_string = self.path.split("_")[-3]
        dimensions = tuple(map(int, dimensions_string.split("x")))
        volume = np.fromfile(self.path, dtype=np.uint8)
        volume = np.reshape(volume, dimensions[::-1])
        volume = np.moveaxis(volume, [0, 2], [2, 0])
        slice = volume[:, :, dimensions[2] // 2]
        for i in range(9):
            preview = np.ndarray((dimensions[0], dimensions[1], 3), dtype=np.uint8)
            tf = data[i]["transfer_function"]
            for ix in range(dimensions[0]):
                for iy in range(dimensions[1]):
                    pixel = slice[ix, iy]
                    r = int(tf[pixel]["color"]["r"] * 255)
                    g = int(tf[pixel]["color"]["g"] * 255)
                    b = int(tf[pixel]["color"]["b"] * 255)
                    a = int(tf[pixel]["color"]["a"] * 255)
                    if a > 0:
                        preview[ix, iy, :] = [b, g, r] 
                    else:
                        preview[ix, iy, :] = [0, 0, 0] 
            preview = cv2.resize(preview, (90, 90))
            cv2.imwrite("temp/tf{}_preview.png".format(i), preview)