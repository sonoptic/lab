import cv2, threading, io
import pyrealsense2 as rs
import numpy as np
from PIL import Image, ImageDraw
from depth import Depth

class Camera(threading.Thread): 

    def __init__(self, parameters, neural):
        self.parameters = parameters
        self.neural = neural

        self.stream_frame = None
        config = rs.config()
        self.pipeline = rs.pipeline()
        config.enable_stream(rs.stream.depth, parameters.depth_width, parameters.depth_height, rs.format.z16,  parameters.depth_fps) 
        config.enable_stream(rs.stream.color, parameters.color_width, parameters.color_height, rs.format.rgb8, parameters.color_fps)

        profile = self.pipeline.start(config)
        self.depth_sensor = profile.get_device().first_depth_sensor().get_depth_scale()
        self.align_stream = rs.align(rs.stream.color)
        
        self.decimation = rs.decimation_filter()
        self.hole_filling = rs.hole_filling_filter()
        self.spatial = rs.spatial_filter()

        self.neural = neural
        self.depth = depth
        print("camera loop has stared")

        threading.Thread.__init__(self)

    def prep_depth(self, depth_raw):
        depth_raw = cv2.applyColorMap(cv2.convertScaleAbs(raw, alpha=parameters.colorizer_alpha), cv2.COLORMAP_JET)
        depth_raw = cv2.resize(depth_raw, (parameters.depth_width, parameters.depth_height), cv2.INTER_CUBIC)
        return depth_raw
        
    def prep_filtered(self, depth_out):
        depth_out = cv2.applyColorMap(cv2.convertScaleAbs(depth_out, alpha=parameters.depth_colorizer), cv2.COLORMAP_JET)
        depth_out = cv2.resize(depth_out, (parameters.depth_width, parameters.depth_height), cv2.INTER_CUBIC)
        return depth_out

    def prep_color(self, ml_out):
        return cv2.resize(ml_out, (parameters.color_width, parameters.color_height), cv2.INTER_CUBIC)

    def run(self):
        while True:
            frames = self.pipeline.wait_for_frames() 
            depth_frame = frames.get_depth_frame()
            color_frame = frames.get_color_frame()

            self.decimation.set_option(rs.option.filter_magnitude, self.parameters.decimation_mag)
            depth_frame = self.decimation.process(depth_frame)
            
            raw, filtered = Depth.process(self, depth_frame)
            ml_out = self.neural.process(color_frame)

            if self.parameters.stream == 'depth':
                self.stream_frame = prep_depth(raw)

            elif self.parameters.stream == 'color':
                self.stream_frame = prep_color(ml_out)

            elif self.parameters.stream == 'filtered':
                self.stream_frame = prep_filtered(filtered)

            elif self.parameters.stream == 'depth_color':
                self.stream_frame = np.hstack((prep_color(ml_out), prep_depth(raw)))

            elif self.parameters.stream == 'depth_filtered':
                self.stream_frame = np.hstack((prep_depth(raw),  prep_filtered(filtered)))

            elif self.parameters.stream == 'color_filtered': 
                self.stream_frame = np.hstack((prep_color(ml_out), prep_filtered(filtered)))

            elif self.parameters.stream == 'all':
                self.stream_frame = np.hstack((prep_color(ml_out), prep_depth(raw), prep_filtered(filtered)))

    def get_bytes(self):
        pimg = self.stream_frame
        with io.BytesIO() as bytesIO:
            pimg.save(bytesIO, "JPEG", quality=50, optimize=False)
            return bytesIO.getvalue()