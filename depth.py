import pyrealsense2 as rs
from scipy import ndimage, misc
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import time, cv2
from PIL import Image


w_depth = 640
w_color = 640
h_depth = 480
h_color = 480
fps_color = 30
fps_depth = 30

WINDOW_NAME = 'depth'

def process_depth(im, _size_factor = 0.6, _filter = 0, _mask_size = 10):
    im = ndimage.gaussian_filter(im, _filter)
    #im = ndimage.zoom(im, _size_factor) # create a way smaller image by interpolation
   

    #filter by objects larger than the numeric mean 
    mask = im > im.mean()

    #labels features based on the mask filter
    label_im, numL = ndimage.label(mask)

    #
    sizes = ndimage.sum(mask, label_im, range(numL+ 1))
    mask_size = sizes < _mask_size
  
    labels = np.unique(label_im)
    label_im = np.searchsorted(labels, label_im)

    return label_im, labels
 
if __name__ == "__main__":
    pipeline = rs.pipeline()
    config = rs.config()
    config.enable_stream(rs.stream.depth, w_depth, h_depth, rs.format.z16, fps_depth) 
    profile = pipeline.start(config)

    cv2.namedWindow(
        WINDOW_NAME, cv2.WINDOW_GUI_NORMAL | cv2.WINDOW_AUTOSIZE | cv2.WINDOW_KEEPRATIO
    )
    cv2.moveWindow(WINDOW_NAME, 100, 200)
   

    while True:
        frames = pipeline.wait_for_frames() 
        depth_frame = frames.get_depth_frame()
        depth_image = np.asanyarray(depth_frame.get_data())

        data, label = process_depth(depth_image)

        rescaled = (255.0 / data.max() * (data - data.min())).astype(np.uint8)
        #im = Image.fromarray(rescaled)

        cv2.imshow(WINDOW_NAME, rescaled) 
        if cv2.waitKey(10) & 0xFF == ord("q"):
            break

        #plt.imshow(data)
        #plt.show()




  
      
