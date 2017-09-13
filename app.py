# coding=utf-8
from flask import Flask
from flask_restful import Api

from resources.origin_img import OriginImage
from resources.user_prefer_img import UserPreferImg

app = Flask(__name__)
api = Api(app)

api.add_resource(OriginImage, '/origin_img', endpoint='origin_img')
api.add_resource(UserPreferImg, '/user_prefer_img', endpoint='user_prefer_img')

if __name__ == "__main__":
    app.run(debug=app.config['DEBUG'], host=app.config['HOST'])
