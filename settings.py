class Parameters(object):
    def __init__(self):
        self.model_path = '/home/ubuntu/sonoptic/lab/model'
        self.model_file = 'model.tflite'
        self.label_file = 'labels.txt'
        self.log_file = 'logfile.txt'

        self.detection_threshold = 0.5

        self.stream = 'color_filtered'
        self.depth_height = 360
        self.depth_width = 640
        self.depth_fps = 30

        self.color_height = 360
        self.color_width = 640
        self.color_fps = 30

        self.decimation = True
        self.decimation_mag = 4

        self.gaussian = True
        self.gaussian_mag = 5

        self.colorizer_alpha = 0.03
        self.depth_colorizer = 0.03

        self.mask = 1000

    #def to_file(self, file):

    #def from_file(self, file):
