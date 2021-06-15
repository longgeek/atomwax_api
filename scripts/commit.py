#! /usr/bin/env python3.8

import os
import json
import redis
import shutil
import configparser
from graal.backends.core.cocom import CoCom


class RedisSingLeton(object):
    """ 单例类, 只初始化一次

    获取 Redis Host 连接对象
    """

    _instance = None
    _option = "redis"
    conn = None

    # 读取配置文件
    cfg = configparser.ConfigParser()
    err = "\nError: In configuration file /etc/atomwax_api/atomwax_api.conf "

    if not cfg.read("/etc/atomwax_api/atomwax_api.conf"):
        exit("\nError: Can not find config file in \
              /etc/atomwax_api/atomwax_api.conf\n")

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

    def commit(self, repo):
        """ 使用 graal 工具获取项目所有 commit """

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
            print(commit)

        # 转化贡献者数据格式，通过提交次数进行排名
        contributor = sorted(contributor.items(),
                             key=lambda d: d[1], reverse=True)
        # 写入排名到 redis
        for con in contributor:
            self.conn.rpush(repo['name'] + '-contributor-new', json.dumps(con))

        # 更 commit 数据
        self.conn.delete(repo['name'] + '-commit')
        self.conn.rename(repo['name'] + '-commit-new',
                         repo['name'] + '-commit')
        # 更新贡献者数据
        self.conn.delete(repo['name'] + '-contributor')
        self.conn.rename(repo['name'] + '-contributor-new',
                         repo['name'] + '-contributor')

    def issue(self, repo):
        pass


if __name__ == "__main__":
    run = Run()
    repo = json.loads(run.repos[0])
    run.commit(repo)
