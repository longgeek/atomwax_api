#!/usr/bin/env python3
""" OpenHarmony gitee 仓库数据统计"""

import json
import requests

owner = 'openharmony'
access_token = '17566c72212fd96715ca459e70131544'
access_token = 'b24ac11bd3417e1cae5d408c3370856d'

forks_count = 0
stargazers_count = 0
watchers_count = 0
issue_count = 0
pull_request_count = 0
follower_count = 0

f = open('oh-repos.txt')
repos = f.readlines()
f.close()

# # all repos
# rsp = requests.get(
#     "https://gitee.com/api/v5/orgs/%s/repos" % owner,
#     params={'page': 3, 'per_page': 100, 'access_token': access_token}
# )
# rsp = json.loads(rsp.content)
# for i in rsp:
#     print i['full_name'].split('/')[1]


# follower
rsp = requests.get(
    "https://gitee.com/api/v5/orgs/%s/followers" % owner,
    params={'page': 1, 'per_page': 1, 'access_token': access_token}
)
follower_count += int(rsp.headers['total_count'])

for repo in repos:
    # star fork watch
    rsp = requests.get(
        "https://gitee.com/api/v5/repos/%s/%s" % (owner, repo.strip()),
        params={'access_token': access_token}
    )
    rsp = json.loads(rsp.content)
    forks_count += rsp['forks_count']
    stargazers_count += rsp['stargazers_count']
    watchers_count += rsp['watchers_count']

    # issue
    rsp = requests.get(
        "https://gitee.com/api/v5/repos/%s/%s/issues" % (owner, repo.strip()),
        params={'state': 'all', 'sort': 'created', 'direction': 'desc', 'page': 1, 'per_page': 1, 'access_token': access_token}
    )
    issue_count += int(rsp.headers['total_count'])

    # pull request
    rsp = requests.get(
        "https://gitee.com/api/v5/repos/%s/%s/pulls" % (owner, repo.strip()),
        params={'state': 'all', 'page': 1, 'per_page': 1, 'access_token': access_token}
    )
    pull_request_count += int(rsp.headers['total_count'])


print 'done.'
print 'forks: ',          forks_count
print 'stars: ',          stargazers_count
print 'watch: ',          watchers_count
print 'issue: ',          issue_count
print 'pull_request: ',   pull_request_count
print 'followers: ',      follower_count
