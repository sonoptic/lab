import os
import tornado.ioloop
import tornado.web
import tornado.websocket

def get_bytes(pimg):
    pimg = Image.fromarray(pimg)
    with io.BytesIO() as bytesIO:
        pimg.save(bytesIO, "JPEG", quality=50, optimize=False)
        return bytesIO.getvalue()

class TornadoApplication(tornado.web.Application):
    def __init__(self):
        script_path = os.path.dirname(os.path.realpath(__file__))
        static_path = script_path + '/static/'

        handlers = [(r"/websocket", ImageSocketHandler),  (r"/(.*)", tornado.web.StaticFileHandler, {'path': static_path, 'default_filename': 'index.html'})]
        super(TornadoApplication, self).__init__(handlers)

class ImageSocketHandler(tornado.websocket.WebSocketHandler):
    clients = set()

    def check_origin(self, origin):
        # Allow access from every origin
        return True

    def open(self):
        img_socket.clients.add(self)
        print("* WebSocket opened from: " + self.request.remote_ip)

    def on_message(self, message):
        last_image = _camera.get_last_image()
        if last_image is not None:
            jpeg_bytes = get_bytes(last_image)
            self.write_message(jpeg_bytes, binary=True)

    def on_close(self):
        img_socket.clients.remove(self)
        print("* WebSocket closed from: " + self.request.remote_ip)


  
