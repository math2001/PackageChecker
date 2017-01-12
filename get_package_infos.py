# -*- encoding: utf-8 -*-

import urllib.request
import json
import base64
import os.path

def get_package_infos_heavily(name, sha):
    """Needs the name and sha of the last commit"""
    url = 'https://api.github.com/repos/wbond/package_control_channel/contents/repository/{}.json?ref={}'.format(name[0].lower(), sha)

    response = json.loads(urllib.request.urlopen(url).read().decode('utf-8'))['content']
    packages_infos = json.loads(base64.b64decode(response).decode('utf-8'))['packages']

    for package_infos in packages_infos:
        if package_infos.get('name', os.path.basename(package_infos['details'])) == name:
            return package_infos

def get_package_infos(pr_url):
    """Only needs the Pull requests url. Might be a bit risky (needs test)"""
    pr_url += '.diff'
    response = urllib.request.urlopen(pr_url).read().decode('utf-8')
    started = False
    lines = []
    for line in response.splitlines()[5:]:
        if line.strip() == '{':
            started = True
            lines.append(line.strip())
        if not started or not line.startswith('+'):
            continue
        lines.append(line[1:].strip())
    lines = lines[:-1]
    if lines[-1][-1] == ',':
        lines[-1] = lines[-1][:-1]
    return json.loads(''.join(lines))
