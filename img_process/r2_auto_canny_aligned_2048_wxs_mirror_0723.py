#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
@author: memo

loads bunch of images from a folder (and recursively from subfolders)
preprocesses (resize or crop, canny edge detection) and saves into a new folder
"""

from __future__ import division
from __future__ import print_function

import PIL.Image
import cv2
import numpy as np
import os


def auto_canny(image, sigma=0.33):
    # compute the median of the single channel pixel intensities
    v = np.median(image)
    # apply automatic Canny edge detection using the computed median
    lower = int(max(0, (1.0 - sigma) * v))
    upper = int(min(255, (1.0 + sigma) * v))
    edged = cv2.Canny(image, lower, upper)
    # return the edged image
    return edged


def get_file_list(path, extensions=('jpg', 'jpeg', 'png')):
    """
    :returns: a (flat) list of paths of all files of (certain types) recursively under a path
    """
    return [
        os.path.join(root, name)
        for root, dirs, files in os.walk(path)
        for name in files
        if name.lower().endswith(extensions)
    ]


def single2pair_canny(path_single_img, do_crop=False, open_mirror=False, target_dim=2048, min_size=0):
    """
    :param path_single_img: path to the origin image
    :param do_crop: if true, resize shortest edge to target dimensions and crops other edge.
                    otherwise, does non-uniform resize
    :param open_mirror: mirror output image
    :param target_dim: target dimensions
    :return:
    """
    out_shape = (target_dim, target_dim)
    origin_img = PIL.Image.open(path_single_img)

    # set the minimum size of image
    if origin_img.size[0] * origin_img.size[1] < min_size:
        print('{} size not allowed'.format(origin_img.size[0] * origin_img.size[1]))
        return None
    try:
        rgb_img = origin_img.convert('RGB')
    except:
        print('image covert error, continue')
        return None
    if do_crop:
        resize_shape = list(out_shape)
        if rgb_img.width < rgb_img.height:
            resize_shape[1] = int(round(float(rgb_img.height) / rgb_img.width * target_dim))
        else:
            resize_shape[0] = int(round(float(rgb_img.width) / rgb_img.height * target_dim))
        resized_img = rgb_img.resize(resize_shape, PIL.Image.BICUBIC)
        hw = int(resized_img.width / 2)
        hh = int(resized_img.height / 2)
        hd = int(target_dim / 2)
        area = (hw - hd, hh - hd, hw + hd, hh + hd)
        img = resized_img.crop(area)

    else:
        img = rgb_img.resize(out_shape, PIL.Image.BICUBIC)

    img_arr = np.array(img)

    img_canny = auto_canny(img_arr)
    img_canny = cv2.cvtColor(img_canny, cv2.COLOR_GRAY2RGB)
    img_bitwise_not = cv2.bitwise_not(img_canny)
    img_pair = np.concatenate((img_arr, img_bitwise_not), axis=1)
    ret_img = PIL.Image.fromarray(img_pair)

    if open_mirror:
        mirror_a1 = img_arr[:, ::-1]
        mirror_a3 = img_bitwise_not[:, ::-1]
        mirror_a4 = np.concatenate((mirror_a1, mirror_a3), axis=1)
        mirror_img = PIL.Image.fromarray(mirror_a4)

        return ret_img, mirror_img

    return ret_img, None


if __name__ == '__main__':
    in_path = './'
    paths = get_file_list(in_path)
    print('{} files found'.format(len(paths)))
    for i, path in enumerate(paths):
        out_img, mirror_img = single2pair_canny(path)
        # Do something with out_img and mirror_img
