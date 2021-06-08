# AtomWax API Backend Project

## Getting Started

If you'd like to run from the master branch, you can clone the git repo:

    git clone

## References

* http://wiki.pyindex.com

## How to use

1. INSTALL SUPERVISOR:

    apt-get install supervisor

2. INSTALL PACKAGES:

    apt-get install python-dev python-rados python-tox libffi-dev libssl-dev libxml2-dev libxslt1-dev
    # Note:
    # apt-get install redis-server 不安装 redis，将直接使用 redis 容器(scripts/redis.sh)
    #

3. INSTALL ATOMWAX_API:

    mkdir /opt/git
    cd /opt/git
    git clone git@git.pyindex.com:reviewdev/atomwax_api.git
    cd atomwax_api/
    pip install -r requirements.txt

4. CREATE LOG DIR:

    mkdir /var/log/atomwax_api
    cp /opt/git/atomwax_api/install/etc/logrotate.d/atomwax_api /etc/logrotate.d/
    chown :adm /var/log/atomwax_api
    logrotate -f /etc/logrotate.d/atomwax_api
    service rsyslog restart

5. CONFIG ATOMWAX_API:

    mkdir /etc/atomwax_api
    cp /opt/git/atomwax_api/install/etc/atomwax_api/atomwax_api.conf.sample /etc/atomwax_api/atomwax_api.conf
    cp /opt/git/atomwax_api/install/etc/supervisor/conf.d/atomwax_api.conf.sample /etc/supervisor/conf.d/atomwax_api.conf

    vim /etc/atomwax_api/atomwax_api.conf
    # redis_pass YCTACMmimohBBiZRanibCnjJV8zdnwGs 设置 redis 访问密码

    vim /etc/redis/redis.conf
    55 行  bind 0.0.0.0 设置 redis 监听地址
    330 行 requirepass YCTACMmimohBBiZRanibCnjJV8zdnwGs 设置 redis 访问密码
    service redis-server restart


10. START SUPERVISOR SERVICE:

    service supervisor restart
    supervisorctl reread
    supervisorctl update
    supervisorctl start atomwax_api

11. LOG DETAIL:

    tail -f /var/log/atomwax_api/output.log
    tail -f /var/log/atomwax_api/errors.log
