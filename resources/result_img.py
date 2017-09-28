# coding=utf-8
import uuid

import werkzeug
from flask_restful import Resource, reqparse
from flask import abort
from flask import send_file
from pathlib import Path
import setting
import os
import img_process.r4_image_blend_0723
import uuid
from util import util
import cv2


class ResultImg(Resource):
    def get(self):
        parser = reqparse.RequestParser()
        parser.add_argument('origin_uuid', type=str, location='args', required=True)
        parser.add_argument('user_prefer_uuid', type=str, location='args', required=True)
        args = parser.parse_args()
        origin_img_uuid = args["origin_uuid"]
        user_prefer_img_uuid = args["user_prefer_uuid"]

        origin_img_path = os.path.join(setting.ORIGIN_IMGS_ROOT, str(origin_img_uuid) + '.jpg')
        user_prefer_img_path = os.path.join(setting.USER_PREFER_IMGS_ROOT, str(user_prefer_img_uuid) + '.jpg')

        if os.path.isfile(origin_img_path) and os.path.isfile(user_prefer_img_path):
            final_img = img_process.r4_image_blend_0723.blend_imgs(
                origin_img_path,
                user_prefer_img_path
            )

            final_img_uuid = str(uuid.uuid4().hex)
            if not os.path.exists(setting.BLEND_IMGS_ROOT):
                util.mkdirs(setting.BLEND_IMGS_ROOT)
            final_img_path = os.path.join(setting.BLEND_IMGS_ROOT, final_img_uuid + '.jpg')
            cv2.imwrite(final_img_path, final_img)
            final_img_res = Path(final_img_path)

            if final_img_res.is_file():
                return send_file(final_img_path, mimetype='image/jpg')
            else:
                # Image does not exist, error!
                abort(404)
