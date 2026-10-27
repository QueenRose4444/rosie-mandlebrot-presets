"""The little of the GitHub REST API the scripts use."""
import json
import os
import urllib.request

API = 'https://api.github.com'


def token():
    return os.environ['GH_TOKEN']


def call(method, path, body=None, raw=None, content_type=None, base=API):
    url = path if path.startswith('http') else f'{base}{path}'
    data = raw if raw is not None else (None if body is None else json.dumps(body).encode())
    req = urllib.request.Request(url, data=data, method=method)
    req.add_header('Authorization', f'Bearer {token()}')
    req.add_header('Accept', 'application/vnd.github+json')
    req.add_header('X-GitHub-Api-Version', '2022-11-28')
    if data is not None:
        req.add_header('Content-Type', content_type or 'application/json')
    with urllib.request.urlopen(req) as r:
        text = r.read()
        return json.loads(text) if text else None


def pages(path):
    """Every item of a paged list."""
    out, page = [], 1
    sep = '&' if '?' in path else '?'
    while True:
        items = call('GET', f'{path}{sep}per_page=100&page={page}')
        out.extend(items)
        if len(items) < 100:
            return out
        page += 1
