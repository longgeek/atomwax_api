#! /usr/bin/env python3.8

import os
import json
import redis
import shutil
import requests
import subprocess
import configparser

from project_list import project_list

from graal.backends.core.cocom import CoCom
from perceval.backends.core.gitee import Gitee
from perceval.backends.core.github import GitHub

from multiprocessing.dummy import Pool as ThreadPool


# 读取配置文件
cfg_file = "/etc/atomwax_api/atomwax_api.conf"
cfg = configparser.ConfigParser()
err = "\nError: In configuration file %s " % cfg_file

if not cfg.read(cfg_file):
    exit("\nError: Can not find config file in %s \n" % cfg_file)


class RedisSingLeton(object):
    """ 单例类, 只初始化一次

    获取 Redis Host 连接对象
    """

    _instance = None
    _option = "redis"
    conn = None

    try:
        REDIS_HOST = cfg.get(_option, "redis_host")
        REDIS_PORT = cfg.get(_option, "redis_port")
        REDIS_DBID = cfg.get(_option, "redis_dbid")
        REDIS_PASS = cfg.get(_option, "redis_pass")
    except Exception as e:
        exit(err + str(e) + "\n")

    def __new__(cls, *args, **kwargs):
        """初始化 Redis 连接"""
        if not cls._instance:
            cls._instance = super(RedisSingLeton, cls).__new__(cls, *args,
                                                               **kwargs)

            # Initialize Redis Host connection
            cls.conn = redis.StrictRedis(
                host=cls.REDIS_HOST,
                port=cls.REDIS_PORT,
                db=cls.REDIS_DBID,
                password=cls.REDIS_PASS,
                decode_responses=True
            )
        return cls.conn


class Run(object):
    """ 获取数据类

    获取项目的 commit、issue、pull requests
    """

    def __init__(self):
        self.conn = RedisSingLeton()
        self.repos = self.conn.lrange("project_list", 0, -1)
        self.gitee_token = cfg.get('default', 'gitee_token')
        self.github_token = cfg.get('default', 'github_token')

    def sync_project(self):
        # 初始化项目数据结构到 Redis
        key = "project_list"
        self.conn.delete(key + "-new")

        if self.conn.llen(key) == 0:
            for project in project_list:
                self.conn.rpush(key, json.dumps(project))
        else:
            repos = self.conn.lrange(key, 0, -1)
            for i in range(len(project_list)):
                if self.conn.llen(key) > i:
                    repo = json.loads(repos[i])
                    project_list[i]["watch"] = repo["watch"]
                    project_list[i]["star"] = repo["star"]
                    project_list[i]["fork"] = repo["fork"]
                    project_list[i]["issue"] = repo["issue"]
                    project_list[i]["commits"] = repo["commits"]
                    project_list[i]["pull_requests"] = repo["pull_requests"]
                    project_list[i]["contributors"] = repo["contributors"]
                    project_list[i]["line_of_code"] = repo["line_of_code"]
                self.conn.rpush(key + "-new", json.dumps(project_list[i]))
            self.conn.rename(key + "-new", key)

    def get_project(self, repo, children=False):
        """ 获取 project 在 redis 中的索引 """

        key = self.repos
        if children:
            key = self.conn.lrange(repo['parent'] + '-projects-list', 0, -1)
        for i in range(len(key)):
            if json.loads(key[i])['name'] == repo['name']:
                return i

    def commit(self, repo):
        """ 使用 graal 工具获取项目所有 commits 和 contributors """

        if not repo.get('repo'):
            return

        git_path = '/tmp/%s' % repo['name'].replace(' ', '-')
        if os.path.exists(git_path):
            shutil.rmtree(git_path)

        # Cocom object initialization
        cc = CoCom(uri=repo['repo'], git_path=git_path)

        # fetch 项目所有的 commits
        # 遍历所有 commits 并 push 到 redis 新 key 中
        # 同时统计贡献者排名
        contributors = {}
        contributors_last = {}
        self.conn.delete(repo['name'] + '-commits-new')
        for commit in cc.fetch():
            self.conn.rpush(repo['name'] + '-commits-new', json.dumps(commit))

            # 获取贡献者贡献次数
            author = commit['data']['Author']
            if contributors.get(author):
                contributors[author] += 1
            else:
                contributors[author] = 1
            contributors_last[author] = commit['updated_on']

        # 转化贡献者数据格式，通过提交次数进行排名
        contributors = sorted(contributors.items(),
                              key=lambda d: d[1], reverse=True)
        # 写入排名到 redis
        self.conn.delete(repo['name'] + '-contributors-new')
        for con in contributors:
            rank = con + (contributors_last[con[0]],)
            self.conn.rpush(repo['name'] + '-contributors-new', json.dumps(rank))

        # 更 commits 数据
        self.conn.delete(repo['name'] + '-commits')
        if self.conn.exists(repo['name'] + '-commits-new'):
            self.conn.rename(repo['name'] + '-commits-new',
                             repo['name'] + '-commits')
        # 更新贡献者数据
        self.conn.delete(repo['name'] + '-contributors')
        if self.conn.exists(repo['name'] + '-contributors-new'):
            self.conn.rename(repo['name'] + '-contributors-new',
                             repo['name'] + '-contributors')

        # 更新 project_list 数据
        # 需要判断是否有子项目
        key = 'project_list'
        index = self.get_project(repo)
        if repo.get('parent'):
            key = repo['parent'] + '-projects-list'
            index = self.get_project(repo, True)

        pro = self.conn.lindex(key, index)
        pro = json.loads(pro)
        pro['commits'] = self.conn.llen(repo['name'] + '-commits')
        pro['contributors'] = len(contributors)
        pro = json.dumps(pro)
        self.conn.lset(key, index, pro)
        shutil.rmtree(git_path)

    def issue_and_pr(self, repo):
        """ 获取项目的 issue 和 pull requests
        使用 perceval github 和 perceval gitee 模块
        """

        if not repo.get('repo'):
            return

        # create a Git object, pointing to repo_url, using repo_dir for cloning
        if 'github.com' in repo['repo']:
            data = GitHub(owner=repo['repo'].split('/')[-2],
                          repository=repo['repo'].split('/')[-1],
                          api_token=self.github_token.split(','),
                          sleep_for_rate=True)
        else:
            data = Gitee(owner=repo['repo'].split('/')[-2],
                         repository=repo['repo'].split('/')[-1],
                         api_token=self.gitee_token.split(','),
                         sleep_for_rate=True)
        # fetch all issues/pull requests as an iterator, and iterate it printing
        # their number, and whether they are issues or pull requests
        self.conn.delete(repo['name'] + '-issue-new')
        self.conn.delete(repo['name'] + '-pull-requests-new')
        for item in data.fetch():
            if 'pull_request' in item['data']:
                self.conn.rpush(repo['name'] + '-pull-requests-new',
                                json.dumps(item))
            else:
                self.conn.rpush(repo['name'] + '-issue-new', json.dumps(item))

        # 更 issue 数据
        self.conn.delete(repo['name'] + '-issue')
        if self.conn.exists(repo['name'] + '-issue-new'):
            self.conn.rename(repo['name'] + '-issue-new',
                             repo['name'] + '-issue')

        # 更 pull requests 数据
        self.conn.delete(repo['name'] + '-pull-requests')
        if self.conn.exists(repo['name'] + '-pull-requests-new'):
            self.conn.rename(repo['name'] + '-pull-requests-new',
                             repo['name'] + '-pull-requests')

        # 更新 project_list 数据
        # 需要判断是否有子项目
        key = 'project_list'
        index = self.get_project(repo)
        if repo.get('parent'):
            key = repo['parent'] + '-projects-list'
            index = self.get_project(repo, True)
        pro = self.conn.lindex(key, index)
        pro = json.loads(pro)
        pro['issue'] = self.conn.llen(repo['name'] + '-issue')
        pro['pull_requests'] = self.conn.llen(repo['name'] + '-pull-requests')
        print(pro['pull_requests'])
        pro = json.dumps(pro)
        self.conn.lset(key, index, pro)

    def cloc(self, repo):
        """ 统计项目代码行数 """

        if not repo.get('repo'):
            return

        git_path = '/tmp/%s' % repo['name'].replace(' ', '-')
        if os.path.exists(git_path):
            shutil.rmtree(git_path)

        os.system("git clone %s %s" % (repo['repo'], git_path))
        p = subprocess.Popen("cloc %s --json" % git_path,
                             shell=True, stdout=subprocess.PIPE)
        out, err = p.communicate()
        out = out.decode()

        # 更 cloc 数据
        self.conn.set(repo['name'] + '-cloc', out)

        # 更新 project_list 数据
        # 需要判断是否有子项目
        key = 'project_list'
        index = self.get_project(repo)
        if repo.get('parent'):
            key = repo['parent'] + '-projects-list'
            index = self.get_project(repo, True)
        pro = self.conn.lindex(key, index)
        pro = json.loads(pro)
        code_num = json.loads(self.conn.get(repo['name'] + '-cloc'))
        code_num = code_num['SUM']['code']
        pro['line_of_code'] = code_num
        pro = json.dumps(pro)
        self.conn.lset(key, index, pro)

    def gitee_stat(self, repo):
        """ 获取 gitee 项目统计信息

        同时遍历 owner 下所有仓数据
        """

        if not repo.get('org'):
            return

        owner = repo['org'].split('/')[-1]
        page = fork = star = watch = issue = follower = pull_requests = 0

        # 获取 owner 下所有仓库, 涉及到分页
        rsp = requests.get(
            "https://gitee.com/api/v5/orgs/%s/repos" % owner,
            params={'page': 1, 'per_page': 100,
                    'type': 'all', 'access_token': self.gitee_token}
        )
        total_page = int(rsp.headers['total_page'])
        repos = []

        for i in range(total_page):
            page += 1
            rsp = requests.get(
                "https://gitee.com/api/v5/orgs/%s/repos" % owner,
                params={'page': page, 'per_page': 100,
                        'type': 'all', 'access_token': self.gitee_token}
            )
            total_page = rsp.headers['total_page']
            content = json.loads(rsp.content)
            for j in content:
                repos.append(j['name'])

        # 获取 follower
        rsp = requests.get(
            "https://gitee.com/api/v5/orgs/%s/followers" % owner,
            params={'page': 1, 'per_page': 1,
                    'access_token': self.gitee_token}
        )
        follower += int(rsp.headers['total_count'])

        # 遍历所有项目
        self.conn.delete(repo['name'] + '-projects-list-new')
        for re in repos:
            # star fork watch
            rsp = requests.get(
                "https://gitee.com/api/v5/repos/%s/%s" % (owner, re.strip()),
                params={'access_token': self.gitee_token}
            )
            rsp = json.loads(rsp.content)
            fork += rsp['forks_count']
            star += rsp['stargazers_count']
            watch += rsp['watchers_count']
            project = {
                "name": re,
                "parent": repo['name'],
                "repo": repo['org'] + "/" + re,
                "fork": rsp['forks_count'],
                "star": rsp['stargazers_count'],
                "watch": rsp['watchers_count'],
            }

            # issue
            rsp = requests.get(
                "https://gitee.com/api/v5/repos/%s/%s/issues" % (owner,
                                                                 re.strip()),
                params={'state': 'all', 'sort': 'created',
                        'direction': 'desc', 'page': 1,
                        'per_page': 1, 'access_token': self.gitee_token}
            )
            issue += int(rsp.headers['total_count'])
            project["issue"] = int(rsp.headers['total_count'])

            # pull requests
            rsp = requests.get(
                "https://gitee.com/api/v5/repos/%s/%s/pulls" % (owner,
                                                                re.strip()),
                params={'state': 'all', 'page': 1, 'per_page': 1,
                        'access_token': self.gitee_token}
            )
            pull_requests += int(rsp.headers['total_count'])

            # 写入每个项目的统计信息到 Redis
            print(project)
            project["pull_requests"] = int(rsp.headers['total_count'])
            self.conn.rpush(repo['name'] + '-projects-list-new',
                            json.dumps(project))
        self.conn.rename(repo['name'] + '-projects-list-new',
                         repo['name'] + '-projects-list')

        # 写入到 Redis 中
        index = self.get_project(repo)
        pro = self.conn.lindex("project_list", index)
        pro = json.loads(pro)
        pro['fork'] = fork
        pro['star'] = star
        pro['watch'] = watch
        pro['issue'] = issue
        pro['follower'] = follower
        pro['pull_requests'] = pull_requests
        pro = json.dumps(pro)
        self.conn.lset("project_list", index, pro)

    def gitee_children_stat(self, repo):
        """ 多线程跑收集子项目数据 """

        repos = self.conn.lrange(repo["name"] + "-projects-list", 0, -1)
        pool = ThreadPool(10)
        pool.map(self._gitee_children_stat, repos)
        pool.close()
        pool.join()

    def _gitee_children_stat(self, project):
        project = json.loads(project)
        print(project)
        # self.commit(project)
        # self.issue_and_pr(project)
        # self.cloc(project)

    def gitee_children_stat_summer(self, repo):
        """ 汇总子项目数据到主项目中 """
        repos = self.conn.lrange(repo["name"] + "-projects-list", 0, -1)
        commits = contributors = line_of_code = 0
        for project in repos:
            project = json.loads(project)
            commits += project.get('commits', 0)
            contributors += project.get('contributors', 0)
            line_of_code += project.get('line_of_code', 0)

        # 更新 project_list 数据
        # 需要判断是否有子项目
        key = 'project_list'
        index = self.get_project(repo)
        pro = self.conn.lindex(key, index)
        pro = json.loads(pro)
        pro['commits'] = commits
        pro['contributors'] = contributors
        pro['line_of_code'] = line_of_code
        pro = json.dumps(pro)
        self.conn.lset(key, index, pro)


if __name__ == "__main__":
    run = Run()
    # run.sync_project()
    repo = json.loads(run.repos[2])
    # run.commit(repo)
    # run.issue_and_pr(repo)
    # run.cloc(repo)
    # run.gitee_stat(repo)
    # run.gitee_children_stat(repo)
    # run.gitee_children_stat_summer(repo)
