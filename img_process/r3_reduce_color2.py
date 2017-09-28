# coding=utf-8

import argparse

import os
from sklearn.cluster import MiniBatchKMeans
import numpy as np
import cv2
import PIL.Image


def build_parser():
    parser = argparse.ArgumentParser(description='Reduce image color')
    parser.add_argument(
        '--in_dir',
        type=str,
        required=True,
        help='path to input dir'
    )
    parser.add_argument(
        '--out_dir',
        type=str,
        default='./outdir',
        help='path to output dir'
    )
    parser.add_argument(
        '--div',
        type=int,
        default=5,
        help='reduce the img to only have ${div} colors'
    )
    return parser


def check(args):
    import os.path as path
    assert path.isdir(args.in_dir), args.in_dir + ' does not exist!'
    assert args.div > 0, 'div should be greater than 0!'
    if not path.isdir(args.out_dir):
        os.makedirs(args.out_dir)


def get_file_list(path, extensions=['jpg', 'jpeg', 'png']):
    """
    returns a (flat) list of paths of all files of (certain types) recursively under a path
    """
    paths = [os.path.join(root, name)
             for root, dirs, files in os.walk(path)
             for name in files
             if name.lower().endswith(tuple(extensions))]
    return paths


def reduce_color(img_path, div=5):
    image = cv2.imread(img_path)
    (h, w) = image.shape[:2]

    # convert the image from the RGB color space to the L*a*b*
    # color space -- since we will be clustering using k-means
    # which is based on the euclidean distance, we'll use the
    # L*a*b* color space where the euclidean distance implies
    # perceptual meaning
    image_o = image
    image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    image = cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)
    image = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)

    # reshape the image into a feature vector so that k-means
    # can be applied
    image = image.reshape((image.shape[0] * image.shape[1], 3))

    # apply k-means using the specified number of clusters and
    # then create the quantized image based on the predictions
    clt = MiniBatchKMeans(n_clusters=div)
    labels = clt.fit_predict(image)
    quant = clt.cluster_centers_.astype("uint8")[labels]

    # reshape the feature vectors to images
    quant = quant.reshape((h, w, 3))
    image = image.reshape((h, w, 3))

    # convert from L*a*b* to RGB
    quant = cv2.cvtColor(quant, cv2.COLOR_LAB2BGR)
    # image = cv2.cvtColor(image, cv2.COLOR_LAB2BGR)

    # out_img = np.hstack([image_o, quant])
    return quant


def batch_reduce_color(opt):
    in_dir = opt.in_dir
    out_dir = opt.out_dir
    div = opt.div

    for file_p in get_file_list(in_dir):
        # load the image and grab its width and height
        out_img = reduce_color(file_p, div=div)
        _, file_name = os.path.split(file_p)
        out_path = os.path.join(out_dir, file_name)
        cv2.imwrite(out_path, out_img)


def single2pair_grayscale(path_single_img, target_dim=2048):
    out_shape = (target_dim, target_dim)
    gray_img = PIL.Image.fromarray(
        cv2.cvtColor(reduce_color(path_single_img), cv2.COLOR_BGR2RGB)
    ).resize(out_shape, PIL.Image.BICUBIC)
    origin_img = PIL.Image.open(path_single_img).convert('RGB').resize(out_shape, PIL.Image.BICUBIC)
    return PIL.Image.fromarray(
        np.concatenate(
            (np.array(origin_img), np.array(gray_img)),
            axis=1
        )
    )


if __name__ == '__main__':
    parser = build_parser()
    args = parser.parse_args()
    check(args)
    batch_reduce_color(args)
