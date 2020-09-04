from edgetpu.basic.basic_engine import BasicEngine
from edgetpu.detection.engine import DetectionEngine
from edgetpu.utils import dataset_utils, image_processing
from tflite_runtime.interpreter import load_delegate
import tflite_runtime.interpreter as tflite
import colorsys, random, cv2
from PIL import Image
import numpy as np

class Neural:

    def __init__(self, parameters):
        self.engine = DetectionEngine(parameters.model_path + '/' + parameters.model_file)
        self.labels = Neural.read_label_file(parameters.model_path + '/' + parameters.label_file) 
        last_key = sorted(self.labels.keys())[len(self.labels.keys()) - 1]
        self.colors = Neural.random_colors(last_key)
        self.parameters = parameters
    
    def process(self, frame):
        #frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        input_buf = Image.fromarray(frame)
        im = frame

        ans = self.engine.detect_with_image(
                input_buf,
                threshold=self.parameters.detection_threshold,
                keep_aspect_ratio=False,
                relative_coord=False,
                top_k=10)

        self.elapsed_ms = self.engine.get_inference_time()

        if ans:
            for obj in ans:
                label_name = "Unknown"
                if self.labels:
                    label_name = self.labels[obj.label_id]
                
                caption = "{0}({1:.2f})".format(label_name, obj.score)
                    # Draw a rectangle and caption.
                box = obj.bounding_box.flatten().tolist()
                Neural.draw_rectangle(im, box, self.colors[obj.label_id])
                Neural.draw_caption(im, box, caption)
        
        return im

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

