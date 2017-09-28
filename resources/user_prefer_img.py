# coding=utf-8
import uuid

import werkzeug
from flask_restful import Resource, reqparse
from flask import abort
from flask import send_file
from pathlib import Path


class UserPreferImg(Resource):
    def get(self):
        parser = reqparse.RequestParser()
        parser.add_argument('uuid', type=str, location='args', required=True)
        args = parser.parse_args()
        uuid_img_name = args["uuid"]

        path_in_res = "./user_prefer_imgs/" + uuid_img_name + ".jpg"

        img_in_res = Path(path_in_res)

        if img_in_res.is_file():
            # Image is in res_imgs, return here
            return send_file(path_in_res, mimetype='image/jpg')
        else:
            # Image does not exist, error!
            abort(404)
