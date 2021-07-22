#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Longgeek <longgeek@gmail.com>

import json
import requests

from atomwax_api import app
from datetime import datetime
from atomwax_api import redis_store


def detail(project):
    """ 获取项目详情 """

    # 获取项目详情
    length = redis_store.llen("project_list")
    for i in range(length):
        project_data = json.loads(redis_store.lindex("project_list", i))
        if project_data['name'] == project:
            rsp = project_data
    return (0, "done", rsp)


def detail_repo(project, repo):
    """ 获取项目的子项目详情 """

    # 获取子项目详情
    length = redis_store.llen(project + "-projects-list")
    for i in range(length):
        repo_data = redis_store.lindex(project + "-projects-list", i)
        repo_data = json.loads(repo_data)
        if repo_data['name'] == repo:
            rsp = repo_data
    return (0, "done", rsp)


def commits(project):
    """ 获取项目 commits 详情 """

    commits = redis_store.lrange(project + "-commits", 0, -1)
    rsp = [json.loads(c) for c in commits]
    return (0, "done", rsp)


def commits_chart(project):
    """ 获取项目 commits 详情 """

    chart = {}
    commits = redis_store.lrange(project + "-commits", 0, -1)
    commits = [json.loads(c) for c in commits]

    for commit in commits:
        if commit.get('CommitData'):
            date = commit['CommitDate']
            format = '%a %b %d %H:%M:%S %Y ' + date.split(' ')[-1]
            commit_time = datetime.strptime(date, format)
        else:
            date = commit['data']['CommitDate']
            format = '%a %b %d %H:%M:%S %Y ' + date.split(' ')[-1]
            commit_time = datetime.strptime(date, format)

        if not chart.get(commit_time.year):
            chart[commit_time.year] = {
                0: 0, 1: 0, 2: 0, 3: 0, 4: 0, 5: 0, 6: 0,
                7: 0, 8: 0, 9: 0, 10: 0, 11: 0,
            }
        else:
            chart[commit_time.year][commit_time.month - 1] += 1
    return (0, "done", chart)


def cloc(project):
    """ 获取项目 cloc 详情 """

    cloc = redis_store.get(project + "-cloc")
    rsp = json.loads(cloc) if cloc else {}
    return (0, "done", rsp)


def issue(project):
    """ 获取项目 issue 详情 """

    issue = redis_store.lrange(project + "-issue", 0, -1)
    rsp = [json.loads(i) for i in issue]
    return (0, "done", rsp)


def issue_chart(project):
    """ 获取项目 issue chart 详情 """

    chart = {}
    issues = redis_store.lrange(project + "-issue", 0, -1)
    issues = [json.loads(i) for i in issues]

    for issue in issues:
        format = "%Y-%m-%dT%H:%M:%SZ"
        if issue.get('data'):
            date = issue['data']['created_at']
        else:
            date = issue['created_at']
        try:
            issue_time = datetime.strptime(date, format)
        except ValueError:
            format = "%Y-%m-%dT%H:%M:%S%z"
            issue_time = datetime.strptime(date, format)

        if not chart.get(issue_time.year):
            chart[issue_time.year] = {
                0: 0, 1: 0, 2: 0, 3: 0, 4: 0, 5: 0, 6: 0,
                7: 0, 8: 0, 9: 0, 10: 0, 11: 0,
            }
        else:
            chart[issue_time.year][issue_time.month - 1] += 1
    return (0, "done", chart)


def contributors(project):
    """ 获取项目 contributors 详情 """

    contributors = redis_store.lrange(project + "-contributors", 0, -1)
    rsp = [json.loads(c) for c in contributors]
    return (0, "done", rsp)


def pull_requests(project):
    """ 获取项目 pull requests 详情 """

    pull_requests = redis_store.lrange(project + "-pull-requests", 0, -1)
    rsp = [json.loads(p) for p in pull_requests]
    return (0, "done", rsp)


def pull_requests_chart(project):
    """ 获取项目 pull requests chart 详情 """

    chart = {}
    pull_requests = redis_store.lrange(project + "-pull-requests", 0, -1)
    pull_requests = [json.loads(p) for p in pull_requests]

    for pull in pull_requests:
        format = "%Y-%m-%dT%H:%M:%SZ"
        date = pull['data']['created_at']
        pull_time = datetime.strptime(date, format)

        if not chart.get(pull_time.year):
            chart[pull_time.year] = {
                0: 0, 1: 0, 2: 0, 3: 0, 4: 0, 5: 0, 6: 0,
                7: 0, 8: 0, 9: 0, 10: 0, 11: 0,
            }
        else:
            chart[pull_time.year][pull_time.month - 1] += 1
    return (0, "done", chart)


def project_list(project):
    """ 获取项目下所有子项目列表 """

    projects = redis_store.lrange(project + "-projects-list", 0, -1)
    rsp = [json.loads(p) for p in projects]
    return (0, "done", rsp)
