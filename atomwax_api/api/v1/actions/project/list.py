#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Longgeek <longgeek@gmail.com>

import json


def list():
    """列出所有项目"""

    f = open('/opt/list.json')
    rsp = json.loads(f.read())
    f.close()

    return (0, "done", rsp)
