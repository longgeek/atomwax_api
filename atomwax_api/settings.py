#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Longgeek <longgeek@fuvism.com>

import configparser

cfg = configparser.ConfigParser()
err = "\nError: In configuration file /etc/atomwax_api/atomwax_api.conf "

if not cfg.read("/etc/atomwax_api/atomwax_api.conf"):
    exit("\nError: Can not find config file in \
          /etc/atomwax_api/atomwax_api.conf\n")


class DefaultConfig(object):
    """Default configuration."""

    _option = "default"

    try:
        TOKEN = cfg.get(_option, "token")
        GITHUB_TOKEN = cfg.get(_option, "github_token")
    except Exception as e:
        exit(err + str(e) + "\n")


class LogConfig(object):
    """ Log configuration. """

    _option = "log"

    try:
        DEBUG = True if cfg.get(_option, "debug") == "true" else False
        VERBOSE = True if cfg.get(_option, "verbose") == "true" else False

        LOG_DIR = cfg.get(_option, "log_dir")
        LOG_FILE = cfg.get(_option, "log_file")
    except Exception as e:
        exit(err + str(e) + "\n")


class RedisConfig(object):
    """Redis Config"""

    _option = "redis"

    try:
        REDIS_HOST = cfg.get(_option, "redis_host")
        REDIS_PORT = cfg.get(_option, "redis_port")
        REDIS_DBID = cfg.get(_option, "redis_dbid")
        REDIS_PASS = cfg.get(_option, "redis_pass")
        REDIS_URL = "redis://:%s@%s:%s/%s" % (REDIS_PASS, REDIS_HOST,
                                              REDIS_PORT, REDIS_DBID)
    except Exception as e:
        exit(err + str(e) + "\n")
