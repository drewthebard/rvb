import time, threading
from keras.models import model_from_json

class ModelLoader(threading.Thread):

    def __init__(self, modelStructurePath, modelWeightsPath):
        super(ModelLoader, self).__init__()
        self.model = None
        self.modelStructurePath = modelStructurePath
        self.modelWeightsPath = modelWeightsPath

    def getModel(self):
        return self.model

    def loadModel(self):
        print("Model loading started...")
        s = time.clock()
        with open(self.modelStructurePath, "r") as jsonFile:
            loadedModelStructure = jsonFile.read()
        self.model = model_from_json(loadedModelStructure)
        self.model.load_weights(self.modelWeightsPath)
        e = time.clock()
        print("Model is Loaded: {0}; in {1:.2f} seconds".format(self.model, (e - s)))

    def run(self):
        super(ModelLoader, self).run()
        self.loadModel()
