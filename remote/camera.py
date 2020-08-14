import pyrealsense2 as rs
import segmentation
import threading


class camera(threading.Thread): 

    def __init__(self,  w_depth = 640, h_depth = 480, w_color = 640, h_color = 480, fps_depth = 30, fps_color = 60):
        self.last_image = None
        
        config = rs.config()
        self.pipeline = rs.pipeline()
        config.enable_stream(rs.stream.depth, w_depth, h_depth, rs.format.z16, fps_depth) 
        config.enable_stream(rs.stream.color, w_color, h_color, rs.format.rgb8, fps_color)
        profile = self.pipeline.start(config)

        depth_sensor = profile.get_device().first_depth_sensor()
        self.depth_scale = depth_sensor.get_depth_scale()
        print('rs init ')

        threading.Thread.__init__(self)

    def attach_interpreter(interpreter):
        self.interpreter = interpreter
        
        
    def run(self):
        while True:
    
            frames = self.pipeline.wait_for_frames() 

            depth_frame = frames.get_depth_frame()
            color_frame = frames.get_color_frame()

            if not depth_frame or not color_frame:
                continue

            depth_image = np.asanyarray(depth_frame.get_data())
            color_image = np.asanyarray(color_frame.get_data())
            #self.last_image =  imutils.resize(color_image, 640)

            predictions, time, mask = self.interpreter.onFrame(color_image) 


    def get_last_image(self):
        return self.last_image
