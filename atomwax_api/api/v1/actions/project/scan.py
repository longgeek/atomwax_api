#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Longgeek <longgeek@gmail.com>

from atomwax_api.api.v1.config import GITHUB_TOKEN

from perceval.backends.core.git import Git
from perceval.backends.core.github import GitHub

from graal.backends.core.cocom import CoCom


def scan(owner, repository):
    """项目的健康分析扫描"""

    repo_url = 'https://github.com/%s/%s' % (owner, repository)
    repo_dir = '/tmp/%s.git' % repository

    # 返回数据
    rsp = {
        "commit": [],
        "graal": [],
        "pull_request": [],
        "issue": [],
        "contributor": [],
    }

    # 使用 perceval git 方式获取 commit 信息
    repo = Git(uri=repo_url, gitpath=repo_dir)
    contributor = []
    for commit in repo.fetch():
        rsp['commit'].append(commit['data'])
        contributor.append(commit['data']['Author'])

    # 生成贡献者列表
    contributor_count = []
    for i in set(contributor):
        contributor_count.append([i, contributor.count(i)])

    contributor_count.sort(key=lambda x: (x[1], x[0]), reverse=True)
    rsp['contributor'] = contributor_count

    # 使用 graal cocom 获取每次 commit 的代码分析
    repo = CoCom(uri=repo_url, git_path=repo_dir)
    rsp['graal'] = [commit for commit in repo.fetch()]

    # 使用 perceval github 方式获取 issiue | request 信息
    repo = GitHub(owner=owner, repository=repository,
                  api_token=GITHUB_TOKEN.split(','),
                  sleep_for_rate=True,
                  sleep_time=300)
    for item in repo.fetch():
        if 'pull_request' in item['data']:
            rsp['pull_request'].append(item)
        else:
            rsp['issue'].append(item)

    return (0, "done", rsp)
