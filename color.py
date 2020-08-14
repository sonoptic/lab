import os, time, collections, cv2, platform, argparse, random, colorsys, PIL
import pyrealsense2 as rs
import numpy as np
from edgetpu.basic.basic_engine import BasicEngine
from edgetpu.detection.engine import DetectionEngine
from edgetpu.utils import dataset_utils, image_processing
from tflite_runtime.interpreter import load_delegate

from PIL import Image, ImageDraw
import tflite_runtime.interpreter as tflite

w_depth = 640
w_color = 640
h_depth = 480
h_color = 480
fps_color = 30
fps_depth = 30


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


WINDOW_NAME = "DETECTION"
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", help="File path of Tflite model.", required=True)
    parser.add_argument("--label", help="File path of label file.", required=True)
    parser.add_argument("--top_k", help="keep top k candidates.", default=10)
    parser.add_argument("--threshold", help="threshold to filter results.", default=0.5, type=float)
    parser.add_argument("--width", help="Resolution width.", default=640, type=int)
    parser.add_argument("--height", help="Resolution height.", default=480, type=int)
    args = parser.parse_args()

    cv2.namedWindow(
        WINDOW_NAME, cv2.WINDOW_GUI_NORMAL | cv2.WINDOW_AUTOSIZE | cv2.WINDOW_KEEPRATIO
    )
    cv2.moveWindow(WINDOW_NAME, 100, 200)



    # Initialize engine.
    engine = DetectionEngine(args.model)
    labels = read_label_file(args.label) if args.label else None

    # Generate random colors.
    last_key = sorted(labels.keys())[len(labels.keys()) - 1]
    colors = random_colors(last_key)

    #initialise realsense
    pipeline = rs.pipeline()
    config = rs.config()
    config.enable_stream(rs.stream.depth, w_depth, h_depth, rs.format.z16, fps_depth) 
    config.enable_stream(rs.stream.color, w_color, h_color, rs.format.rgb8, fps_color)

    profile = pipeline.start(config)
    depth_sensor = profile.get_device().first_depth_sensor()


    while True:
        elapsed_list = []
        frames = pipeline.wait_for_frames() 

        depth_frame = frames.get_depth_frame()
        color_frame = frames.get_color_frame()

        if not depth_frame or not color_frame:
            continue

        depth_image = np.asanyarray(depth_frame.get_data())
        color_image = np.asanyarray(color_frame.get_data())
            #self.last_image =  imutils.resize(color_image, 640)


        start = time.perf_counter()

        image = color_image
        im = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
        input_buf = PIL.Image.fromarray(image)

        # Run inference.
        ans = engine.detect_with_image(
            input_buf,
            threshold=args.threshold,
                    keep_aspect_ratio=False,
                    relative_coord=False,
                    top_k=args.top_k,
            )
                
        elapsed_ms = engine.get_inference_time()

                # Display result.
        if ans:
            for obj in ans:
                label_name = "Unknown"
                if labels:
                    label_name = labels[obj.label_id]
                
                caption = "{0}({1:.2f})".format(label_name, obj.score)

                # Draw a rectangle and caption.
                box = obj.bounding_box.flatten().tolist()
                draw_rectangle(im, box, colors[obj.label_id])
                draw_caption(im, box, caption)

        # Calc fps.
        elapsed_list.append(elapsed_ms)
        avg_text = ""
        
        if len(elapsed_list) > 100:
            elapsed_list.pop(0)
            avg_elapsed_ms = np.mean(elapsed_list)
            avg_text = " AGV: {0:.2f}ms".format(avg_elapsed_ms)

        # Display fps
        fps_text = "{0:.2f}ms".format(elapsed_ms)
        draw_caption(im, (10, 30), fps_text + avg_text)

        # display
        cv2.imshow(WINDOW_NAME, im) 
        if cv2.waitKey(10) & 0xFF == ord("q"):
            break