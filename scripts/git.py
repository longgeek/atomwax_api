#! /usr/bin/env python3

import json
from perceval.backends.core.git import Git

# url for the git repo to analyze
# directory for letting Perceval clone the git repo
repo_dir = '/tmp/pika'

# create a Git object, pointing to repo_url, using repo_dir for cloning
repo = Git(uri=repo_dir, gitpath='/tmp/aa')
# fetch all commits as an iterator, and iterate it printing each hash
contributor = {}
for commit in repo.fetch():
    if contributor.get(commit['data']['Author']):
        contributor[commit['data']['Author']] += 1
    else:
        contributor[commit['data']['Author']] = 1

list = sorted(contributor.items(), key=lambda d: d[1], reverse=True)
print(json.dumps(list))
