#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Longgeek <longgeek@fuvism.com>


"""Atomwax_api Porject

Flask based.
"""

import json
from flask import Flask
from flask import jsonify
from flask_restful import Api
from flask_redis import FlaskRedis
from werkzeug.middleware.proxy_fix import ProxyFix
from atomwax_api.project_list import project_list

# Flask Service App
app = Flask(__name__)
app.config.from_object("atomwax_api.settings.DefaultConfig")
app.config.from_object("atomwax_api.settings.LogConfig")
app.config.from_object("atomwax_api.settings.RedisConfig")

# Redis Service
# 初始化项目数据结构到 Redis
redis_store = FlaskRedis(app, decode_responses=True)
if len(redis_store.lrange("project_list", 0, -1)) == 0:
    for project in project_list:
        redis_store.rpush("project_list", json.dumps(project))

# API Service config
from atomwax_api.api.v1 import controller as v1
api_route = Api(app)
api_route.add_resource(v1.APIView, "/api/v1")


@app.errorhandler(404)
def http_404(error):
    return jsonify(http_code=404,
                   message="Page/API url path not found!"), 404


@app.errorhandler(500)
def http_500(error):
    return jsonify(http_code=500,
                   message="Runtime error(HTTP 500)!"), 500


app.wsgi_app = ProxyFix(app.wsgi_app)
