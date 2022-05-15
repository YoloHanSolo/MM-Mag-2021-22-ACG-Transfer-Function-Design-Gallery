from transferFunctionGenerator import TransferFunctionGenerator

TFG = TransferFunctionGenerator("aneurism_256x256x256_1x1x1_uint8.raw")
data = TFG.generateInitialTransferFunctions()
TFG.generateTransferFunctionsPreview(data)