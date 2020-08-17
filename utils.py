import psutil, os, random, colorsys, io, cv2
from PIL import Image
import numpy as np

def draw_rectangle(image, box, color, thickness=3):
    """ Draws a rectangle.

    Args:
        image: The image to draw on.
        box: A list of 4 elements (x1, y1, x2, y2).
        color: Rectangle color.
        thickness: Thickness of lines.
    """
    b = np.array(box).astype(int)
    cv2.rectangle(image, (b[0], b[1]), (b[2], b[3]), color, thickness)

def draw_caption(image, box, caption):
    """ Draws a caption above the box in an image.

    Args:
        image: The image to draw on.
        box: A list of 4 elements (x1, y1, x2, y2).
        caption: String containing the text to draw.
    """
    b = np.array(box).astype(int)
    cv2.putText(
        image, caption, (b[0], b[1]), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 0), 2
    )
    cv2.putText(
        image, caption, (b[0], b[1]), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 1
    )

def read_label_file(file_path):
    """ Function to read labels from text files.

    Args:
        file_path: File path to labels.
    """
    with open(file_path, "r") as f:
        lines = f.readlines()

    ret = {}
    for line in lines:
        pair = line.strip().split(maxsplit=1)
        ret[int(pair[0])] = pair[1].strip()
    return ret

def random_colors(N):
    """ Random color generator.
    """
    N = N + 1
    hsv = [(i / N, 1.0, 1.0) for i in range(N)]
    colors = list(
        map(lambda c: tuple(int(i * 255) for i in colorsys.hsv_to_rgb(*c)), hsv)
    )
    random.shuffle(colors)
    return colors

def sys_usage(ms):
    meter = INA219(0.1, 3)
    meter.configure(meter.RANGE_16V)

    voltage = abs(meter.voltage())
    current = abs(meter.current())
    life =  round((voltage - 3.1) * 100 / (4.2 - 3.1))

    own_pid = os.getpid()
    own_process = psutil.Process(own_pid)
    mem = round(own_process.memory_full_info().uss / 1024 / 1024)

    cpu = psutil.cpu_percent(interval=None)
    cpu_freq = psutil.cpu_freq()
    temp = psutil.sensors_temperatures()['cpu-thermal'][0].current

    print('load_avg: {}, cpu_perc: {}%, cpu_freq: {}, cpu_temp: {}, mem: {}, FPS: {}'.format(load_avg, cpu, cpu_freq[0], temp, mem, 1000/ms))

def get_bytes(pimg):
    pimg = Image.fromarray(pimg)
    with io.BytesIO() as bytesIO:
        pimg.save(bytesIO, "JPEG", quality=50, optimize=False)
        return bytesIO.getvalue()