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
key = "project_list"
redis_store = FlaskRedis(app, decode_responses=True)

if redis_store.llen(key) == 0:
    for project in project_list:
        redis_store.rpush(key, json.dumps(project))
else:
    repos = redis_store.lrange(key, 0, -1)
    for i in range(len(project_list)):
        if redis_store.llen(key) > i:
            repo = json.loads(repos[i])
            project_list[i]["watch"] = repo["watch"]
            project_list[i]["star"] = repo["star"]
            project_list[i]["fork"] = repo["fork"]
            project_list[i]["issue"] = repo["issue"]
            project_list[i]["commits"] = repo["commits"]
            project_list[i]["pull_requests"] = repo["pull_requests"]
            project_list[i]["contributors"] = repo["contributors"]
            project_list[i]["line_of_code"] = repo["line_of_code"]
        redis_store.rpush(key + "-new", json.dumps(project_list[i]))
    redis_store.rename(key + "-new", key)

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
