#! /usr/bin/env python3.8

import os
import json
import redis
import shutil
import subprocess
import configparser

from graal.backends.core.cocom import CoCom
from perceval.backends.core.gitee import Gitee
from perceval.backends.core.github import GitHub


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

    def commit(self, repo):
        """ 使用 graal 工具获取项目所有 commit 和 contributor """

        if not repo['repo']:
            return

        git_path = '/tmp/commit'
        if os.path.exists(git_path):
            shutil.rmtree(git_path)

        # Cocom object initialization
        cc = CoCom(uri=repo['repo'], git_path='/tmp/commit')

        # fetch 项目所有的 commit
        # 遍历所有 commit 并 push 到 redis 新 key 中
        # 同时统计贡献者排名
        contributor = {}
        for commit in cc.fetch():
            self.conn.rpush(repo['name'] + '-commit-new', json.dumps(commit))

            # 获取贡献者贡献次数
            author = commit['data']['Author']
            if contributor.get(author):
                contributor[author] += 1
            else:
                contributor[author] = 1

        # 转化贡献者数据格式，通过提交次数进行排名
        contributor = sorted(contributor.items(),
                             key=lambda d: d[1], reverse=True)
        # 写入排名到 redis
        for con in contributor:
            self.conn.rpush(repo['name'] + '-contributor-new', json.dumps(con))

        # 更 commit 数据
        self.conn.delete(repo['name'] + '-commit')
        if self.conn.exists(repo['name'] + '-commit-new'):
            self.conn.rename(repo['name'] + '-commit-new',
                             repo['name'] + '-commit')
        # 更新贡献者数据
        self.conn.delete(repo['name'] + '-contributor')
        if self.conn.exists(repo['name'] + '-contributor-new'):
            self.conn.rename(repo['name'] + '-contributor-new',
                             repo['name'] + '-contributor')

    def issue_and_pr(self, repo):
        """ 获取项目的 issue 和 pull request
        使用 perceval github 和 perceval gitee 模块
        """

        # create a Git object, pointing to repo_url, using repo_dir for cloning
        if 'github.com' in repo['repo']:
            data = GitHub(owner=repo['repo'].split('/')[-2],
                          repository=repo['repo'].split('/')[-1],
                          api_token=self.github_token.split(','),
                          sleep_for_rate=True)
        else:
            data = Gitee(owner=repo['repo'].split('/')[-2], 
                         repository=repo['repo'].split('/')[-1],
                         api_token=self.github_token.split(','),
                         sleep_for_rate=True)
        # fetch all issues/pull requests as an iterator, and iterate it printing
        # their number, and whether they are issues or pull requests 
        for item in data.fetch():
            print(item)
            print()
            if 'pull_request' in item['data']:
               self.conn.rpush(repo['name'] + '-pull-request-new', json.dumps(item))
            else:
               self.conn.rpush(repo['name'] + '-issue-new', json.dumps(item))

        # 更 issue 数据
        self.conn.delete(repo['name'] + '-issue')
        if self.conn.exists(repo['name'] + '-issue-new'):
            self.conn.rename(repo['name'] + '-issue-new',
                             repo['name'] + '-issue')

        # 更 pull request 数据
        self.conn.delete(repo['name'] + '-pull-request')
        if self.conn.exists(repo['name'] + '-pull-request-new'):
            self.conn.rename(repo['name'] + '-pull-request-new',
                             repo['name'] + '-pull-request')

    def cloc(self, repo):
        """ 统计项目代码行数 """

        git_path = '/tmp/%s' % repo['name']
        if os.path.exists(git_path):
           shutil.rmtree(git_path)

        os.system("git clone %s %s" % (repo['repo'], git_path))
        p = subprocess.Popen("cloc %s --json" % git_path, shell=True, stdout=subprocess.PIPE)
        out, err = p.communicate()
        out = out.decode()

        # 更 cloc 数据
        self.conn.set(repo['name'] + '-cloc', out)


if __name__ == "__main__":
    run = Run()
    repo = json.loads(run.repos[0])
    # run.commit(repo)
    # run.issue_and_pr(repo)
    run.cloc(repo)
