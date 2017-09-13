# coding=utf-8
import uuid

import werkzeug
from flask_restful import Resource, reqparse


class OriginImage(Resource):
    def get(self):
        parser = reqparse.RequestParser()
        parser.add_argument('uuid', type=str, location='args', required=True)
        args = parser.parse_args()
        uuid_img_name = args["uuid"]

    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('img', type=werkzeug.datastructures.FileStorage, location='files')
        args = parser.parse_args()
        img_file = args['img']
        uuid_img_name = uuid.uuid4().hex
