class Parameters(object):
    def __init__(self):
        self.model_path = '/home/ubuntu/sonoptic/lab/model'
        self.model_file = 'model.tflite'
        self.label_file = 'labels.txt'
        self.log_file = 'logfile.txt'

        self.detection_threshold = 0.3

        self.stream = 'color_filtered'
        self.depth_height = 360
        self.depth_width = 640
        self.depth_fps = 15

        self.color_height = 360
        self.color_width = 640
        self.color_fps = 15

        self.decimation = True
        self.decimation_mag = 4

        self.gaussian = True
        self.gaussian_mag = 5

        self.PREZOOM = 0.5
        self.SCALE = 30
        self.SIGMA = 0.5
        self.SIZE = 200
        self.FILTER = 500
        self.CONNECTIVITY = 0.5

        self.depth_colorizer = 0.03
   

    #def to_file(self, file):

    #def from_file(self, file):
