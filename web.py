import tornado.ioloop, tornado.web, tornado.websocket, psutil, utils, os
from ina219 import INA219
from ina219 import DeviceRangeError

class SocketHandler(tornado.websocket.WebSocketHandler):
    clients = set()

    def initialize(self, loop):
        self.loop = loop
        #tornado.websocket.WebSocketHandler.__init__(self)

    def check_origin(self, origin):
        # Allow access from every origin
        return True

    def open(self):
        SocketHandler.clients.add(self)
        print("WebSocket opened from: " + self.request.remote_ip)


    def on_message(self, message):
        jpeg_bytes = utils.get_bytes(self.loop.get_last_frame())
        self.write_message(jpeg_bytes, binary=True)

    def on_close(self):
        SocketHandler.clients.remove(self)
        print("WebSocket closed from: " + self.request.remote_ip)

class StatusHandler(tornado.web.RequestHandler):


    def get(self):
        meter = INA219(0.1, 3)
        meter.configure(meter.RANGE_16V)

        voltage = abs(meter.voltage())
        current = round(abs(meter.current()),2)

        life =  round((voltage - 3.1) * 100 / (4.2 - 3.1))

        own_process = psutil.Process(os.getpid())
        mem = round(own_process.memory_full_info().uss / 1024 / 1024)

        cpu = psutil.cpu_percent(interval=None)
        cpu_freq = psutil.cpu_freq()[0]
        temp = psutil.sensors_temperatures()['cpu-thermal'][0].current

        response = { 
            'voltage': voltage, 
            'current': current, 
            'percentage': life, 
            'memory': mem, 
            'cpu_usage': cpu,
            'cpu_freq': cpu_freq,
            'temp': temp
        }

        self.write(response)

class DepthParamHandler(tornado.web.RequestHandler):
    
    def initialize(self, parameters):
        self.parameters = parameters
    
    def get(self):
        response = { 
            'decimation_on': self.parameters.decimation,
            'decimation_mag': self.parameters.decimation_mag, 
            'spatial_on': self.parameters.spatial, 
            'spatial_mag': self.parameters.spatial_mag, 
            'spatial_alpha': self.parameters.spatial_alpha,
            'spatial_delta': self.parameters.spatial_delta,
            'hole_on': self.parameters.holes,
            'hole_mag': self.parameters.holes_mag,
            'gaussian_on': self.parameters.gaussian, 
            'gaussian_mag': self.parameters.gaussian_mag, 
            'zoom_on': self.parameters.zoom, 
            'zoom': self.parameters.zoom_mag,
            'mask': self.parameters.mask
        }

        self.write(response)

    def post(self):
        self.set_header("Content-Type", "text/plain")
        slider = self.get_body_argument("slider")
        value = self.get_body_argument("value")

        if slider == 'decimation_mag_slider':
            self.parameters.decimation_mag = value

        elif slider == 'spatial_mag_slider':
            self.parameters.spatial_mag  = value

        elif slider == "spatial_alpha_slider":
            self.parameters.spatial_alpha = value
    
        elif slider == "spatial_delta_slider":
            self.parameters.spatial_delta = value

        elif slider == "hole_mag_slider":
            self.parameters.holes_mag = value

        elif slider == "gauss_mag_slider":
            self.parameters.gaussian_mag = value

        elif slider == "zoom_slider":
            self.parameters.zoom_mag = value

        elif slider == "mask_slider":
            self.parameters.mask = value



        
        print(self.get_body_argument("slider"), self.get_body_argument("value"))



            