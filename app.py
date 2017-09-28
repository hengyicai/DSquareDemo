# coding=utf-8
from flask import Flask
from flask_restful import Api

from resources.origin_img import OriginImage
from resources.user_prefer_img import UserPreferImg
from resources.result_img import ResultImg
import config as cfg

app = Flask(__name__)
api = Api(app)

app.config.from_object(cfg)

api.add_resource(OriginImage, '/' + app.config['PREFIX'] + '/origin_img', endpoint='origin_img')
api.add_resource(UserPreferImg, '/' + app.config['PREFIX'] + '/user_prefer_img', endpoint='user_prefer_img')
api.add_resource(ResultImg, '/' + app.config['PREFIX'] + '/result_img', endpoint='result_img')

if __name__ == "__main__":
    app.run(debug=app.config['DEBUG'], host=app.config['HOST'], port=app.config['PORT'])
