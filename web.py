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