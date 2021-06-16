#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Longgeek <longgeek@gmail.com>

import json
from atomwax_api import redis_store


def detail(project):
    """ 获取项目详情 """

    rsp = {}

    # 获取 commit
    cloc = redis_store.lrange(project + "-cloc", 0, -1)
    issue = redis_store.lrange(project + "-issue", 0, -1)
    commit = redis_store.lrange(project + "-commit", 0, -1)
    contributor = redis_store.lrange(project + "-contributor", 0, -1)
    pull_request = redis_store.lrange(project + "-pull-request", 0, -1)

    rsp = {
        'cloc': [json.loads(c) for c in cloc],
        'issue': [json.loads(i) for i in issue],
        'commit': [json.loads(c) for c in commit],
        'contributor': [json.loads(c) for c in contributor],
        'pull-request': [json.loads(p) for p in pull_request],
    }
    return (0, "done", rsp)
