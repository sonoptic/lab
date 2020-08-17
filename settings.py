class SonopticSettings(object):
    def __init__(self):
        self.depth_width = 640
        self.depth_height = 360
        self.depth_fps = 15

        self.depth_filter_decimation = True
        self.depth_filter_decimation_mag = 4
        
        self.depth_filter_spatial = True
        self.depth_filter_spatial_mag = 5
        self.depth_filter_spatial_alpha = 1
        self.depth_filter_spatial_delta = 50

        self.depth_filter_holes = False
        self.depth_filter_holes_mag = 3

        self.depth_filter_gaussian = True
        self.depth_filter_gaussian_mag = 5
