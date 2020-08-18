import argparse, os, io, imutils, threading, cv2, utils, colorsys
import tornado.ioloop


import pyrealsense2 as rs
import numpy as np

from PIL import Image, ImageDraw
from scipy import ndimage, misc

from edgetpu.basic.basic_engine import BasicEngine
from edgetpu.detection.engine import DetectionEngine
from edgetpu.utils import dataset_utils, image_processing
from tflite_runtime.interpreter import load_delegate
import tflite_runtime.interpreter as tflite

from web import SocketHandler, StatusHandler, DepthParamHandler
from settings import DepthParams

DEPTH_HEIGHT = 240
DEPTH_WIDTH = 424
DEPTH_FPS = 15

COLOR_HEIGHT = 240
COLOR_WIDTH = 424
COLOR_FPS = 30

parameters = DepthParams()

engine = DetectionEngine('/home/ubuntu/sonoptic/runner/model/model.tflite')
labels = utils.read_label_file('/home/ubuntu/sonoptic/runner/model/labels.txt') 
last_key = sorted(labels.keys())[len(labels.keys()) - 1]
colors = utils.random_colors(last_key)


def do_depth(camera, depth_frame,): 
    
    camera.decimation.set_option(rs.option.filter_magnitude, parameters.decimation_mag)
    #camera.spatial.set_option(rs.option.holes_fill, holes_fill)
    camera.spatial.set_option(rs.option.filter_magnitude, parameters.spatial_mag)
    camera.spatial.set_option(rs.option.filter_smooth_alpha, parameters.spatial_alpha)
    camera.spatial.set_option(rs.option.filter_smooth_delta, parameters.spatial_delta)

    # do depth post processing using the realsense filters
    depth_frame = camera.decimation.process(depth_frame)
    depth_frame = camera.spatial.process(depth_frame)
    #depth_frame = camera.hole_filling.process(depth_frame)
    depth_image = np.asanyarray(depth_frame.get_data())

    depth_image = ndimage.zoom(depth_image, parameters.zoom) # create a way smaller image by interpolation
    im = ndimage.gaussian_filter(depth_image, parameters.gaussian_mag)

    #filter by objects larger than the numeric mean 
    mask = im > im.mean()

    #labels features based on the mask filter
    label_im, numL = ndimage.label(mask)
 
    sizes = ndimage.sum(mask, label_im, range(numL+ 1))
    mask_size = sizes < mask_size
  
    labels = np.unique(label_im)
    data = np.searchsorted(labels, label_im)

    data = (255.0 / data.max() * (data - data.min())).astype(np.uint8)
    return depth_image, data

def do_nn(color_frame, depth_frame, _threshold = 0.5):
    color_image = np.asanyarray(color_frame.get_data())
    depth_image = np.asanyarray(depth_frame.get_data())
    input_buf = Image.fromarray(color_image)
    im = color_image

    ans = engine.detect_with_image(
            input_buf,
            threshold=_threshold,
            keep_aspect_ratio=False,
            relative_coord=False,
            top_k=10)

    elapsed_ms = engine.get_inference_time()

    if ans:
        for obj in ans:
            label_name = "Unknown"
            if labels:
                label_name = labels[obj.label_id]
            
            caption = "{0}({1:.2f})".format(label_name, obj.score)
                # Draw a rectangle and caption.
            box = obj.bounding_box.flatten().tolist()
            utils.draw_rectangle(im, box, colors[obj.label_id])
            utils.draw_caption(im, box, caption)
    
    return im, elapsed_ms
    
class camera_loop(threading.Thread): 

    def __init__(self):
        self.last_image = None
        config = rs.config()
        self.pipeline = rs.pipeline()
        config.enable_stream(rs.stream.depth, DEPTH_WIDTH, DEPTH_HEIGHT, rs.format.z16, DEPTH_FPS) 
        config.enable_stream(rs.stream.color, COLOR_WIDTH, COLOR_HEIGHT, rs.format.rgb8, COLOR_FPS)
        profile = self.pipeline.start(config)
        self.depth_sensor = profile.get_device().first_depth_sensor().get_depth_scale()
        self.align_stream = rs.align(rs.stream.color)
        
        self.decimation = rs.decimation_filter()
        self.hole_filling = rs.hole_filling_filter()
        self.spatial = rs.spatial_filter()

        print("camera loop has stared")
        threading.Thread.__init__(self)
    

    def run(self):
        while True:
            
            frames = self.pipeline.wait_for_frames() 
            aligned_frames = self.align_stream.process(frames)
            depth_frame = aligned_frames.get_depth_frame()
            color_frame = aligned_frames.get_color_frame()

            if not depth_frame or not color_frame:
                continue

            raw, depth_out = do_depth(self, depth_frame)
            ml_out, ms = do_nn(color_frame, depth_frame)

            #utils.sys_usage(ms)

            depth_out = cv2.applyColorMap(cv2.convertScaleAbs(depth_out, alpha=0.12), cv2.COLORMAP_JET)
            depth_out = cv2.resize(depth_out,(424, 240),cv2.INTER_CUBIC)

            self.last_image = np.hstack((ml_out, depth_out))


    def get_last_frame(self):
        return self.last_image

if __name__ == "__main__":
    loop = None
    parser = argparse.ArgumentParser()
   
    parser.add_argument('-w', '--web', action='store_true', help="enable web interface")
    parser.add_argument('-c', '--camera', action='store_true', help="enable camera  ")
    parser.add_argument('-l', '--logfile', action='store', help="save stats to file")
    args = parser.parse_args()


    if args.camera:
        loop = camera_loop()
        loop.start()
        print("* Camera loop started")

    if args.web:
        print("* Web interface available at: http://localhost:8000")

        app = tornado.web.Application([
            (r"/websocket", SocketHandler, {'loop': loop}),
            (r"/status",StatusHandler),
            (r"/params",DepthParamHandler, {'parameters': parameters}),
            (r"/(.*)", tornado.web.StaticFileHandler, 
                                            {'path':  os.path.dirname(os.path.realpath(__file__)) + '/web/', 
                                            'default_filename': 'index.html'})])
        
        app.listen(8000)
        tornado.ioloop.IOLoop.current().start()

