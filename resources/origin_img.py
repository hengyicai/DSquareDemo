# coding=utf-8
import uuid

import werkzeug
from flask_restful import Resource, reqparse
from util import util
import os
import setting

ORIGIN_IMGS_ROOT = setting.ORIGIN_IMGS_ROOT
USER_PREFER_IMGS_ROOT = setting.USER_PREFER_IMGS_ROOT

import img_process.r3_reduce_color2
import img_process.r2_auto_canny_aligned_2048_wxs_mirror_0723
from options.test_options import TestOptions
from models.models import create_model
import PIL.Image


class OriginImage(Resource):
    def __init__(self):
        self.edge_opt = TestOptions().parse()

        self.edge_opt.nThreads = 1  # test code only supports nThreads = 1
        self.edge_opt.batchSize = 1  # test code only supports batchSize = 1
        self.edge_opt.serial_batches = True  # no shuffle
        self.edge_opt.no_flip = True  # no flip
        self.edge_opt.name = "pix2pix_render_standeview_daytime_1900samples"
        self.edge_opt.model = "pix2pix"
        self.edge_opt.which_model_netG = "unet_1024"
        self.edge_opt.which_direction = "BtoA"
        self.edge_opt.dataset_mode = "aligned"
        self.edge_opt.fineSize = 1024
        self.edge_opt.loadSize = 1024

        self.gray_scale_opt = TestOptions().parse()

        self.gray_scale_opt.nThreads = 1  # test code only supports nThreads = 1
        self.gray_scale_opt.batchSize = 1  # test code only supports batchSize = 1
        self.gray_scale_opt.serial_batches = True  # no shuffle
        self.gray_scale_opt.no_flip = True  # no flip
        self.gray_scale_opt.name = "render_building_standview_1900s_gray7levels"
        self.gray_scale_opt.model = "pix2pix"
        self.gray_scale_opt.which_model_netG = "unet_1024"
        self.gray_scale_opt.which_direction = "BtoA"
        self.gray_scale_opt.dataset_mode = "aligned"
        self.gray_scale_opt.fineSize = 1024
        self.gray_scale_opt.loadSize = 1024
        self.gray_scale_opt.which_epoch = "200"

    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('img', type=werkzeug.datastructures.FileStorage, location='files')
        args = parser.parse_args()
        img_file = args['img']
        uuid_img_name = str(uuid.uuid4().hex)

        if img_file:
            if not os.path.exists(ORIGIN_IMGS_ROOT):
                util.mkdirs(ORIGIN_IMGS_ROOT)
            if not os.path.exists(USER_PREFER_IMGS_ROOT):
                util.mkdirs(USER_PREFER_IMGS_ROOT)

            origin_img_path = os.path.join(ORIGIN_IMGS_ROOT, uuid_img_name + '.jpg')
            img_file.save(origin_img_path)

            # Get the pair_img of gray_scale and edge
            pair_img_gray_scale = img_process.r3_reduce_color2.single2pair_grayscale(origin_img_path)
            pair_img_edge = img_process.r2_auto_canny_aligned_2048_wxs_mirror_0723.single2pair_canny(origin_img_path)[0]

            # Load model and do generation
            out_img_gray_scale = self.generate_img(self.gray_scale_opt, pair_img_gray_scale)
            uuid_gray_scale = str(uuid.uuid4().hex)
            out_img_gray_scale.save(os.path.join(USER_PREFER_IMGS_ROOT, uuid_gray_scale + '.jpg'))

            out_img_edge = self.generate_img(self.edge_opt, pair_img_edge)
            uuid_edge = str(uuid.uuid4().hex)
            out_img_edge.save(os.path.join(USER_PREFER_IMGS_ROOT, uuid_edge + '.jpg'))

            # Response
            return {
                "code": setting.CODE_OK,
                "msg": setting.MSG_SUCCESS,
                "data": {
                    "origin_img": uuid_img_name,
                    "gray_scale_img": uuid_gray_scale,
                    "edge_img": uuid_edge
                }
            }
        else:
            # Error
            return {
                "code": setting.CODE_ERROR,
                "msg": "img is null!",
                "data": setting.NULL_DATA
            }

    def generate_img(self, opt, input_pair_img):
        model = create_model(opt)
        model.set_single_img(input_pair_img, '')
        model.test()
        visuals = model.get_current_visuals()
        del model
        return PIL.Image.fromarray(visuals['fake_B'])
