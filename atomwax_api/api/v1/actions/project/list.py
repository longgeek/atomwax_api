#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Longgeek <longgeek@gmail.com>

import json
from atomwax_api import redis_store


def list():
    """ 列出所有项目 """

    rsp = []
    project_list = redis_store.lrange("project_list", 0, -1)
    rsp = [json.loads(r) for r in project_list]

    return (0, "", rsp)
