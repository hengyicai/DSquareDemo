# -- coding: utf-8 --

import cv2
import numpy as np
import os
import sys
from blend_modes import blend_modes
import PIL.Image
from PIL import ImageEnhance


def eachFile(filepath, resutlpath):
    blend_N = 0
    pathDir = os.listdir(filepath)
    for allDir in pathDir:
        if allDir.find("_fake_B") != -1:
            child = os.path.join('%s/%s' % (filepath, allDir))
            foreground_img = child
            line_img = child.replace("_fake_B", "_real_A", 1)
            background_img = child.replace("_fake_B", "_real_B", 1)
            if os.path.exists(line_img) and os.path.exists(background_img):
                result_img = os.path.join('%s/%s' % (resutlpath, allDir))
                blend_pictures(background_img, foreground_img, line_img, result_img)
                blend_N = blend_N + 1
                print "save result(" + bytes(blend_N) + "):" + result_img


def changeto4Channel(img, size_height=1024, size_width=1024):
    alpha = np.full((size_height, size_width), 255.0)
    b, g, r = cv2.split(img)
    merged = cv2.merge([b, g, r, alpha])
    return merged


# background_img_float 截图  foreground_img_floa 效果图  line_img_float 线稿
def blend_pictures(background_img, foreground_img, line_img, result_img):
    background_img_float = cv2.imread(background_img, cv2.IMREAD_COLOR).astype(float)
    b, g, r = cv2.split(background_img_float)

    background_img_float = changeto4Channel(background_img_float)

    foreground_img_float = cv2.imread(foreground_img, cv2.IMREAD_COLOR).astype(float)
    foreground_img_float = changeto4Channel(foreground_img_float)

    # line_img_float = cv2.imread(line_img, cv2.IMREAD_COLOR).astype(float)
    # line_img_float = changeto4Channel(line_img_float)

    # Blend images_original_100%正常截图+200%柔光效果图+30%正片叠底线稿
    '''opacity = 1  # The opacity of the foreground that is blended onto the background is 70 %.
    blended_img_float = blend_modes.soft_light(background_img_float, foreground_img_float, opacity)
    blended_img_float = blend_modes.soft_light(blended_img_float, foreground_img_float, opacity)
    opacity = 0.3
    blended_img_float = blend_modes.multiply(blended_img_float, line_img_float, opacity)
    # Display blended image'''

    # Blend images 100%正常&效果图+100%强光模式&截图
    opacity = 1  # The opacity of the foreground that is blended onto the background is 70 %.
    blended_img_float = blend_modes.hard_light(foreground_img_float, background_img_float, opacity)

    # Blend images SU截图100%+效果图100%变暗+线稿50%正片叠底
    '''
    opacity = 1  # The opacity of the foreground that is blended onto the background is 70 %.
    blended_img_float = blend_modes.darken_only(background_img_float, foreground_img_float, opacity)
    opacity = 0.5
    blended_img_float = blend_modes.multiply(blended_img_float, line_img_float, opacity)'''

    '''
    # Blend images 效果图100%正常+效果图100%柔光+SU截图100%变暗
    opacity = 1  # The opacity of the foreground that is blended onto the background is 70 %.
    blended_img_float = blend_modes.darken_only(foreground_img_float, background_img_float, opacity)
    blended_img_float = blend_modes.soft_light(blended_img_float, foreground_img_float, opacity)'''

    '''
    # 图片增强
    enhance_factor = 1.3
    enhancer = ImageEnhance.Color(blended_img_float)
    blended_img_float = enhancer.enhance(enhance_factor)
    enhancer = ImageEnhance.Contrast(blended_img_float)
    blended_img_float = enhancer.enhance(enhance_factor)
    '''

    cv2.imwrite(result_img, blended_img_float)


def blend_imgs(origin_img_path,
               user_prefer_img_path,
               blend_function=blend_modes.hard_light,
               blend_opacity=1,
               do_enhance=False,
               enhance_factor=1.3):
    origin_img = cv2.imread(origin_img_path, cv2.IMREAD_COLOR).astype(float)
    # Resize origin_img and user_prefer_img to same size
    origin_height, origin_width, _ = origin_img.shape
    user_prefer_img = np.asarray(
        PIL.Image.open(
            user_prefer_img_path
        ).convert('RGB').resize((origin_width, origin_height), PIL.Image.BICUBIC),
        float
    )[:, :, ::-1].copy()

    origin_img_float = changeto4Channel(origin_img, origin_height, origin_width)
    user_prefer_img_float = changeto4Channel(user_prefer_img, origin_height, origin_width)

    blended_img_float = blend_function(origin_img_float, user_prefer_img_float, blend_opacity)

    if do_enhance:
        blended_img_float = ImageEnhance.Contrast(
            ImageEnhance.Color(blended_img_float).enhance(enhance_factor)
        ).enhance(enhance_factor)
    return blended_img_float


if __name__ == '__main__':
    if len(sys.argv) == 3:
        rootdir = sys.argv[1]
        resultdir = sys.argv[2]
    if len(sys.argv) == 2:
        rootdir = sys.argv[1]
        resultdir = os.path.join('%s/%s' % (rootdir, 'result'))
    if len(sys.argv) == 1:
        rootdir = os.path.dirname(os.path.realpath(__file__)) + '/images'
        resultdir = os.path.join('%s/%s' % (rootdir, 'result'))
    if not os.path.exists(rootdir):
        print "images dir: " + rootdir + " not found ,end"
    else:
        if not os.path.exists(resultdir):
            os.makedirs(resultdir)
        print "blend image in dir:" + rootdir
        eachFile(rootdir, resultdir)
