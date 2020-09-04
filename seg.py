
from scipy import ndimage, misc
from skimage import io, feature, img_as_float, img_as_ubyte, img_as_uint, morphology, measure, util, color
from skimage.segmentation import felzenszwalb, slic, quickshift, watershed, mark_boundaries, flood, flood_fill
import numpy as np

class Segmentation:
    def depth(depth_frame, parameters): 
        image = np.asanyarray(depth_frame.get_data())
        image = ndimage.zoom(image, parameters.PREZOOM)
        image = img_as_float(image) # convert image to float (skimage compatibilty)
        segments =  felzenszwalb(image,  scale=parameters.SCALE, sigma=parameters.SIGMA, min_size=parameters.SIZE, multichannel=True)
        segments = morphology.remove_small_objects(segments, min_size=parameters.FILTER, connectivity=parameters.CONNECTIVITY) # filter little shits out
        labels, num = measure.label(segments, return_num=True) # turn segments into labels 
        data = color.label2rgb(labels, segments) # create pretty colored labels 
        data = (255.0 / data.max() * (data - data.min())).astype(np.uint8) # convert to uint so it can be displayed with opencv

        return image, data

    
