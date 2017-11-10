import time, threading

class ModelLoader(threading.Thread):

    def __init__(self, modelStructurePath, modelWeightsPath):
        super(ModelLoader, self).__init__()
        self.graph = None
        self.model = None
        self.starter_lines = None
        self.modelStructurePath = modelStructurePath
        self.modelWeightsPath = modelWeightsPath

    def getModel(self):
        return self.model

    def getGraph(self):
        return self.graph

    def getStarterLines(self):
        return self.starter_lines

    def loadModel(self):
        from tensorflow import get_default_graph
        from keras.models import model_from_json

        # start timing
        print("Model loading started...")
        s = time.clock()

        # read starter lines
        self.starter_lines = open("starter.txt").readlines()

        # load models and graphs
        with open(self.modelStructurePath, "r") as jsonFile:
            loadedModelStructure = jsonFile.read()
        self.model = model_from_json(loadedModelStructure)
        self.model.load_weights(self.modelWeightsPath)
        self.graph = get_default_graph()

        # end timing
        e = time.clock()
        print("Model is Loaded: {0}; in {1:.2f} seconds".format(self.model, (e - s)))

    def run(self):
        super(ModelLoader, self).run()
        self.loadModel()
