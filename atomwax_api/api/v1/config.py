#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Longgeek <longgeek@fuvism.com>

from atomwax_api import app


TOKEN = app.config["TOKEN"]
GITHUB_TOKEN = app.config["GITHUB_TOKEN"]

TOKEN_HEADERS = {
    "token": "Bearer %s" % TOKEN,
    "content-type": "application/json"
}

# API Actions
API_ACTIONS = {
    "Project": {
        "Scan": {
            "action": ("project", "scan", "scan"),
        },
    },
}


def load_api(api_key, api_action):
    """ 加载 API 的 Action """

    package, moduler, func = API_ACTIONS[api_key][api_action]["action"]
    load_action = getattr(
        __import__(
            "atomwax_api.api.v1.actions.%s.%s" % (package, moduler),
            fromlist=[func]
        ),
        func
    )

    return (0, "Success!", load_action)
