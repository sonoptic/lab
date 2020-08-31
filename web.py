import tornado.ioloop, tornado.web, tornado.websocket, psutil, os

class SocketHandler(tornado.websocket.WebSocketHandler):
    clients = set()

    def initialize(self, camera):
        self.loop = camera
        #tornado.websocket.WebSocketHandler.__init__(self)

    def check_origin(self, origin):
        # Allow access from every origin
        return True

    def open(self):
        SocketHandler.clients.add(self)
        print("WebSocket opened from: " + self.request.remote_ip)

    def on_message(self, message):
        jpeg_bytes = self.loop.get_bytes()
        self.write_message(jpeg_bytes, binary=True)

    def on_close(self):
        SocketHandler.clients.remove(self)
        print("WebSocket closed from: " + self.request.remote_ip)

class StatusHandler(tornado.web.RequestHandler):


    def initialize(self,io):
        self.io = io 

    def get(self):
        mem = psutil.virtual_memory()
        mem = round(mem[3] / 1024 / 1024)
        mem = str(mem) + " / 2048"

        cpu = psutil.cpu_percent(interval=None)
        cpu_freq = psutil.cpu_freq()[0]
        temp = psutil.sensors_temperatures()['cpu-thermal'][0].current

        has_meter = self.io.has_meter()
        has_haptic = self.io.has_haptic()
        has_motion = self.io.has_motion()
        has_left_dac = self.io.has_left_dac()
        has_right_dac = self.io.has_right_dac()

        try: 
            voltage, current, power = self.io.read_power()
            life =  round((voltage - 3.1) * 100 / (4.2 - 3.1))
            
            self.write({
                'has_meter': has_meter,
                'has_haptic': has_haptic,
                'has_motion': has_motion, 
                'has_left_dac': has_left_dac,
                'has_right_dac': has_right_dac,
                'voltage': voltage, 
                'current': current, 
                'percentage': life, 
                'memory': mem, 
                'cpu_usage': cpu,
                'cpu_freq': cpu_freq,
                'temp': temp
            })

            
        except Exception as e:
            self.write({
                'has_meter': has_meter,
                'has_haptic': has_haptic,
                'has_motion': has_motion, 
                'has_left_dac': has_left_dac,
                'has_right_dac': has_right_dac,
                'voltage': 'N/A ', 
                'current': 'N/A ', 
                'percentage': 'N/A s', 
                'memory': mem, 
                'cpu_usage': cpu,
                'cpu_freq': cpu_freq,
                'temp': temp
            })
            


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

            'colorizer_alpha_slider': self.parameters.colorizer_alpha,
            'mask': self.parameters.mask
        }

        self.write(response)

    def post(self):
        self.set_header("Content-Type", "text/plain")
        slider = self.get_body_argument("slider")
        value = self.get_body_argument("value")

        if slider == 'decimation_mag_slider':
            self.parameters.decimation_mag = round(int(value))

        elif slider == 'spatial_mag_slider':
            self.parameters.spatial_mag  = float(value)

        elif slider == "spatial_alpha_slider":
            self.parameters.spatial_alpha = float(value)
    
        elif slider == "spatial_delta_slider":
            self.parameters.spatial_delta = float(value)

        elif slider == "hole_mag_slider":
            self.parameters.holes_mag = float(value)

        elif slider == "gauss_mag_slider":
            self.parameters.gaussian_mag = float(value)

        elif slider == "zoom_slider":
            self.parameters.depth_colorizer = float(value)

        elif slider == "mask_slider":
            self.parameters.mask = int(value)
        
        elif slider == "colorizer_alpha_slider":
            self.parameters.colorizer_alpha = float(value)
        
        print(self.get_body_argument("slider"), self.get_body_argument("value"))



            