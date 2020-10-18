import cv2, threading, io
import pyrealsense2 as rs
import numpy as np
import pytesseract

from PIL import Image, ImageDraw
from segmentation import Segmentation

class Camera(threading.Thread): 

    def __init__(self, parameters, neural):
        self.parameters = parameters
        self.neural = neural

        self.stream_frame = None
        config = rs.config()
        self.pipeline = rs.pipeline()
        config.enable_stream(rs.stream.depth, self.parameters.depth_width, self.parameters.depth_height, rs.format.z16,  self.parameters.depth_fps) 
        config.enable_stream(rs.stream.color, self.parameters.color_width, self.parameters.color_height, rs.format.rgb8, self.parameters.color_fps)

        profile = self.pipeline.start(config)
        self.depth_sensor = profile.get_device().first_depth_sensor().get_depth_scale()
        self.align_stream = rs.align(rs.stream.color)
        self.decimation = rs.decimation_filter()
        self.hole_filling = rs.hole_filling_filter()
        self.spatial = rs.spatial_filter()

        self.neural = neural
        print("camera loop has stared")

        threading.Thread.__init__(self)
        
    def prep_depth(self, depth_raw):
        depth_raw = cv2.applyColorMap(cv2.convertScaleAbs(raw, alpha=self.parameters.depth_colorizer), cv2.COLORMAP_JET)
        depth_raw = cv2.resize(depth_raw, (self.parameters.depth_width, self.parameters.depth_height), cv2.INTER_CUBIC)
        return depth_raw
        
    def prep_filtered(self, depth_out):
        depth_out = cv2.resize(depth_out, (self.parameters.depth_width, self.parameters.depth_height), cv2.INTER_CUBIC)
        return depth_out

    def prep_color(self, ml_out):
        return

    def run(self):
        while True:
            frames = self.pipeline.wait_for_frames() 
            
            color_frame = frames.get_color_frame()
            color_image = np.asanyarray(color_frame.get_data())
            depth_frame = frames.get_depth_frame()
            depth_image = np.asanyarray(depth_frame.get_data())
            #text = pytesseract.image_to_string(color_image)
            #print(text)
            #segmented_color = Segmentation.color(color_image, self.parameters) 
            ml_out = self.neural.process(color_image)

            

            self.decimation.set_option(rs.option.filter_magnitude, self.parameters.DECIMATION)
            depth_frame = self.decimation.process(depth_frame)
            #segmented_depth = Segmentation.depth(depth_frame, self.parameters)
            #segmented_color = Segmentation.color(color_image, self.parameters)

            depth_colormap = cv2.applyColorMap(cv2.convertScaleAbs(depth_image, alpha=0.03), cv2.COLORMAP_JET)
            depth = cv2.resize(depth_colormap, (self.parameters.depth_width, self.parameters.depth_height), cv2.INTER_CUBIC)
            #seg_depth = cv2.resize(segmented_depth, (self.parameters.depth_width, self.parameters.depth_height), cv2.INTER_CUBIC)
            ml = cv2.resize(ml_out, (self.parameters.color_width, self.parameters.color_height), cv2.INTER_CUBIC)

            self.stream_frame = np.hstack((ml, depth_colormap))
            #self.stream_frame = ml

    def get_bytes(self):
        pimg = Image.fromarray(self.stream_frame)
        
        with io.BytesIO() as bytesIO:
            pimg.save(bytesIO, "JPEG", quality=50, optimize=False)
            return bytesIO.getvalue()
