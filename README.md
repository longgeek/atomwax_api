# AtomWax API Backend Project

## Getting Started

If you'd like to run from the master branch, you can clone the git repo:

    git clone ssh://git@lab.openatom.tech:8102/lirong/atomwax_api.git

## How to use

1. INSTALL PACKAGES:

    apt-get install supervisor redis-server redis-tools

2. INSTALL ATOMWAX_API:

    mkdir /opt/git
    cd /opt/git
    git clone ssh://git@lab.openatom.tech:8102/lirong/atomwax_api.git
    cd atomwax_api/
    pip install -r requirements.txt

3. CREATE LOG DIR:

    mkdir /var/log/atomwax_api
    cp /opt/git/atomwax_api/config/logrotate_atomwax_api.conf.sample /etc/logrotate.d/logrotate_atomwax_api.conf
    chown :adm /var/log/atomwax_api
    logrotate -f /etc/logrotate.d/logrotate_atomwax_api.conf
    service rsyslog restart

4. CONFIG ATOMWAX_API:

    mkdir /etc/atomwax_api
    cp /opt/git/atomwax_api/config/atomwax_api.conf.sample /etc/atomwax_api/atomwax_api.conf
    cp /opt/git/atomwax_api/config/supervisor_atomwax_api.conf.sample /etc/supervisor/conf.d/atomwax_api.conf

5. START SUPERVISOR SERVICE:

    service supervisor restart
    supervisorctl reread
    supervisorctl update
    supervisorctl start atomwax_api

6. LOG DETAIL:

    tail -f /var/log/atomwax_api/output.log
    tail -f /var/log/atomwax_api/errors.log
