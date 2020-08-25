
from scipy import ndimage, misc
import numpy as np

class Depth:
    def process(depth_frame, parameters): 
        depth_image = np.asanyarray(depth_frame.get_data())

        # use gausian filter
        im = ndimage.gaussian_filter(depth_image, parameters.gaussian_mag)

        #filter by objects larger than the numeric mean 
        mask = im > parameters.mask

        #labels features based on the mask filter
        label_im, numL = ndimage.label(mask)
    
        sizes = ndimage.sum(mask, label_im, range(numL+ 1))
        mask_size = sizes < parameters.mask
        #remove_pixel = mask_size[label_im]
        #label_im[remove_pixel] = 0
    
        labels = np.unique(label_im)
        data = np.searchsorted(labels, label_im)

        data = (255.0 / data.max() * (data - data.min())).astype(np.uint8)
        return depth_image, data
