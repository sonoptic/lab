import tornado.ioloop, tornado.web, tornado.websocket, psutil, os, json, datetime

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
        mem = str(mem)

        cpu = psutil.cpu_percent(interval=None)
        cpu_freq = psutil.cpu_freq()[0]
        temp = psutil.sensors_temperatures()['cpu-thermal'][0].current
        temp = "{:.2f}".format(temp)

        has_meter = self.io.has_meter()
        has_haptic = self.io.has_haptic()
        has_motion = self.io.has_motion()
        has_left_dac = self.io.has_left_dac()
        has_right_dac = self.io.has_right_dac()

        try: 
            voltage, current, power = self.io.read_power()
            life =  round((voltage - 3.1) * 100 / (4.2 - 3.1))
            voltage = "{:.2f}".format(voltage)
            current = "{:.2f}".format(current / 1000)
            
            now = datetime.datetime.now().isoformat()

            dumpobj = {
                'now': now,
                'voltage': voltage, 
                'current': current, 
                'percentage': life,  
            }

            obj = {
                'now': now, 
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
            }

            #with open("/home/ubuntu/sonoptic/lab/life_stream.json", "a") as myfile:
               # myfile.write(json.dumps(dumpobj, indent=4, sort_keys=True))

            self.write(obj)


            
        except Exception as e:
            obj = {
                'now': now, 
                'has_meter': has_meter,
                'has_haptic': has_haptic,
                'has_motion': has_motion, 
                'has_left_dac': has_left_dac,
                'has_right_dac': has_right_dac,
                'voltage': 'N/A ', 
                'current': 'N/A ', 
                'percentage': 'N/A', 
                'memory': mem, 
                'cpu_usage': cpu,
                'cpu_freq': cpu_freq,
                'temp': temp
            }
            
            with open("/home/ubuntu/life.txt", "a") as myfile:
                myfile.write(json.dumps(obj))


            self.write(obj)
            


class DepthParamHandler(tornado.web.RequestHandler):
    
    def initialize(self, parameters):
        self.parameters = parameters
    
    def get(self):
        response = { 
            'decimation_on': self.parameters.decimation,
            'decimation_mag': self.parameters.decimation_mag, 
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

        elif slider == 'prezoom':
            self.parameters.PREZOOM = float(value)

        elif slider == "scale":
            self.parameters.SCALE= float(value)
    
        elif slider == "sigma":
            self.parameters.SIGMA = float(value)

        elif slider == "size":
            self.parameters.SIZE = float(value)

        elif slider == "filter":
            self.parameters.FILTER = float(value)

        elif slider == "connectivity":
            self.parameters.CONNECTIVITY = float(value)

        
        print(self.get_body_argument("slider"), self.get_body_argument("value"))



            
