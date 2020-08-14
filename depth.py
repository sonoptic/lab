import pyrealsense2 as rs
from scipy import ndimage, misc
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import time

w_depth = 640
w_color = 640
h_depth = 480
h_color = 480
fps_color = 30
fps_depth = 30


def process_depth(im, _size_factor = 0.2, _filter = 0.4, _mask_size = 500):
    im = ndimage.gaussian_filter(im, _filter)
    im = ndimage.zoom(im, _size_factor) # create a way smaller image by interpolation
    
    #filter by objects larger than the numeric mean 
    mask = im > im.mean()

    #labels features based on the mask filter
    label_im, numL = ndimage.label(mask)

    sizes = ndimage.sum(mask, label_im, range(numL+ 1))
    mask_size = sizes < _mask_size
    remove_pixel = mask_size[label_im]
    label_im[remove_pixel] = 0
    labels = np.unique(label_im)
    label_im = np.searchsorted(labels, label_im)

    plt.imshow(label_im)
    plt.axis('off')
    plt.show()

if __name__ == "__main__":
    pipeline = rs.pipeline()
    config = rs.config()
    config.enable_stream(rs.stream.depth, w_depth, h_depth, rs.format.z16, fps_depth) 
    profile = pipeline.start(config)
   

    while True:
        frames = pipeline.wait_for_frames() 
        depth_frame = frames.get_depth_frame()
        depth_image = np.asanyarray(depth_frame.get_data())

        process_depth(depth_frame)



  
      
