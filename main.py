import argparse, os, io, imutils, threading, cv2, colorsys
import tornado.ioloop

from hardware import Hardware
from web import SocketHandler, StatusHandler, DepthParamHandler
from settings import Parameters
from camera import Camera
from neural import Neural 

camera = None
neural = None
parameters = Parameters()
hardware = Hardware()

if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument('-s', '--stream', action='store_true', help="enable web stream")
    parser.add_argument('-c', '--camera', action='store_true', help="enable camera  ")
    parser.add_argument('-l', '--logfile', action='store', help="save stats to file")
    args = parser.parse_args()


    _socketHandler = (r"/websocket", SocketHandler, {'camera': camera})
    _statusHandler = (r"/status",StatusHandler, {'io': hardware})
    _settingsHandler = (r"/params",DepthParamHandler, {'parameters': parameters})
    _staticHandler =  (r"/(.*)", tornado.web.StaticFileHandler, 
                            {'path':  os.path.dirname(os.path.realpath(__file__)) + '/web/', 
                            'default_filename': 'index.html'})


    if args.camera:
        neural = Neural()
        loop = Camera(parameters, neural)
        loop.start()
        print("* Camera loop started")

    if args.stream:
        print("* Stream and interface at: http://localhost:8000")
        app = tornado.web.Application([_socketHandler, _statusHandler, _settingsHandler, _staticHandler])
    else:
        print("* Interface at: http://localhost:8000")
        app = tornado.web.Application([ _statusHandler, _settingsHandler, _staticHandler])

    
    app.listen(8000)
    tornado.ioloop.IOLoop.current().start()

