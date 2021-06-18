#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Longgeek <longgeek@gmail.com>

import json
from atomwax_api import redis_store


def detail(project):
    """ 获取项目详情 """

    # 获取项目其他数据
    cloc = redis_store.get(project + "-cloc")
    issue = redis_store.lrange(project + "-issue", 0, -1)
    commits = redis_store.lrange(project + "-commits", 0, -1)
    contributors = redis_store.lrange(project + "-contributors", 0, -1)
    pull_requests = redis_store.lrange(project + "-pull-requests", 0, -1)

    rsp = {
        'cloc': json.loads(cloc) if cloc else {},
        'issue': [json.loads(i) for i in issue],
        'commits': [json.loads(c) for c in commits],
        'contributors': [json.loads(c) for c in contributors],
        'pull-requests': [json.loads(p) for p in pull_requests],
    }

    # 获取项目详情
    length = redis_store.llen("project_list")
    for i in range(length):
        project_data = json.loads(redis_store.lindex("project_list", i))
        if project_data['name'] == project:
            rsp['detail'] = project_data

    return (0, "done", rsp)
