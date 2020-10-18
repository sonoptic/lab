import subprocess, serial, time, threading, os, signal
from subprocess import PIPE, Popen, STDOUT

def connect(): 
    p = subprocess.Popen("sudo rfcomm connect /dev/rfcomm0 00:19:07:34:F1:0F 1 &", shell=True, stdout=PIPE)
    time.sleep(5)
    os.kill(p.pid, signal.SIGTERM)

class Wristband(threading.Thread):
    def __init__(self):
        connected = False
        while connected is False:
            try:
                self.serial = serial.Serial('/dev/rfcomm0', 9600, timeout=1)
                connected = True
                print("connected !")
            except Exception as e:
                time.sleep(5)
                print("trying again...")
                connect()

        self.heading = {}
        self.accel = {}
        self.gyro = {}
        self.mag = {}

        threading.Thread.__init__(self)

    def setPower(self, power):
        print(power)
        string = "p{}\n".format(int(power))
        _bytes = bytes(string, encoding='utf8')
        self.serial.write(_bytes)
    
    def setUpTime(self, upTime):
        print(upTime)
        string = "u{}\n".format(int(upTime))
        _bytes = bytes(string, encoding='utf8')
        self.serial.write(_bytes)
    
    def setDownTime(self, downTime):
        print(downTime)
        string = "u{}\n".format(int(downTime))
        _bytes = bytes(string, encoding='utf8')
        self.serial.write(_bytes)

    def getHeading(self):
        return self.heading

    def getTimeUp(self):
        return self.time_up
    
    def getTimeDown(self):
        return self.time_down
    
    def getIntensity(self):
        return self.intensity

    def run(self):
        while True:
            line = str(self.serial.readline().decode()).split(',')
            if len(line) > 3:
                self.heading = {
                    'roll': float(line[0]),
                    'pitch': float(line[1]),
                    'yaw': float(line[2])}

                print(self.heading)

                self.time_up = float(line[3])
                self.time_down = float(line[4])
                self.intensity = float(line[5])


