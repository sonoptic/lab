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

    def initialize(self,io, wristband):
        self.wristband = wristband
        self.io = io 

    def post(self):
        self.set_header("Content-Type", "text/plain")
        slider = self.get_body_argument("slider")
        value = self.get_body_argument("value")
        print(slider, value)

        if slider == 'timeOn':
            self.wristband.setUpTime(int(value))

        elif slider == 'timeOff':
            self.wristband.setDownTime(int(value))

        elif slider == "intensity":
            self.wristband.setPower(int(value))

    def get(self):
        mem = psutil.virtual_memory()
        mem = round(mem[3] / 1024 / 1024)
        mem = str(mem)

        cpu = psutil.cpu_percent(interval=None)
        cpu_freq = psutil.cpu_freq()[0]
        temp = psutil.sensors_temperatures()['cpu-thermal'][0].current
        temp = "{:.2f}".format(temp)
        now = datetime.datetime.now().isoformat()

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
                'temp': temp, 
                'heading': self.wristband.getHeading(),
                'intensity': self.wristband.getIntensity(),
                'timeUp': self.wristband.getTimeUp(),
                'timeDown': self.wristband.getTimeDown(),
            }


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
                'temp': temp, 
                'heading': 'N/A ', 
                'intensity': 'N/A ', 
                'timeUp': 'N/A ', 
                'timeDown': 'N/A ', 
            }
            


            self.write(obj)
            