
from scipy import ndimage, misc
from skimage import io, feature, img_as_float, img_as_ubyte, img_as_uint, morphology, measure, util, color, transform
from skimage.segmentation import felzenszwalb, slic, quickshift, watershed, mark_boundaries, flood, flood_fill
import numpy as np
import cv2, colorsys, random

def draw_rectangle(image, box, color, thickness=1):
    b = np.array(box).astype(int)
    cv2.rectangle(image, (b[0], b[1]), (b[2], b[3]), color, thickness)

def _felzenszwalb(image, as_int, _scale, _sigma, _size, _filter, _connectivity, _multichannel):
    segments =  felzenszwalb(image,  scale=_scale, sigma=_sigma, min_size=_size, multichannel=True)
    segments = morphology.remove_small_objects(segments, min_size=_filter, connectivity=_connectivity) # filter little shits out
    labels, num = measure.label(segments, return_num=True) # turn segments into labels 
    
    # convert labels to rgb so we can draw bounding boxes
    data = color.label2rgb(labels, segments) 
    data = (255.0 / data.max() * (data - data.min())).astype(np.uint8) # convert to uint so it can be displayed with opencv
    
    objs = ndimage.find_objects(labels)

    index = 0

    for obj in objs:
        
        index+=1
        at_index = as_int[obj]
        x_min = obj[0].start
        x_max = obj[0].stop
        y_min = obj[1].start
        y_max = obj[1].stop
        h = x_max - x_min
        w = y_max - y_min
        avg = int(np.average(at_index))


        draw_rectangle(data, [x_min, x_max, y_min, y_max], (255, 255, 255))



    return labels, data

#def _slic(image, )

class Segmentation:
    def depth(depth_frame, param): 
        image = np.asanyarray(depth_frame.get_data())
        image = ndimage.zoom(image, param.DEPTH_PREZOOM)
        as_int = image
        image = img_as_float(image) 
        labels, data = _felzenszwalb(image, as_int, param.DEPTH_SCALE, param.DEPTH_SIGMA, param.DEPTH_SIZE, param.DEPTH_FILTER, param.DEPTH_CONNECTIVITY, True)
        return data


    def color(color_image, param):
        as_int = color_image
        
        image = img_as_float(color_image) 
        image = ndimage.zoom(image, param.DEPTH_PREZOOM)
        image = color.rgb2gray(image)
        image = transform.rescale(image, 0.2, anti_aliasing=True)
        labels, data = _felzenszwalb(image, as_int, param.COLOR_SCALE, param.COLOR_SIGMA, param.COLOR_SIZE, param.COLOR_FILTER, param.COLOR_CONNECTIVITY, False)
        return data

