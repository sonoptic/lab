class Parameters(object):
    def __init__(self):
        self.model_path = '/home/ubuntu/sonoptic/lab/model'
        self.model_file = 'fresh.tflite'
        self.label_file = 'fresh.txt'
        self.log_file = 'logfile.txt'

        self.detection_threshold = 0.5

        self.stream = 'color_filtered'
        self.depth_height = 360
        self.depth_width = 640
        self.depth_fps = 15

        self.color_height = 360
        self.color_width = 640
        self.color_fps = 15

        self.DECIMATION = 1
 
        self.DEPTH_PREZOOM = 0.2
        self.DEPTH_SCALE = 18
        self.DEPTH_SIGMA = 0.5
        self.DEPTH_SIZE = 120
        self.DEPTH_FILTER = 800
        self.DEPTH_CONNECTIVITY = 0.5

        self.COLOR_SCALE = 30
        self.COLOR_SIGMA = 0.5
        self.COLOR_SIZE = 200
        self.COLOR_FILTER = 500
        self.COLOR_CONNECTIVITY = 0.5

   

    #def to_file(self, file):

    #def from_file(self, file):
