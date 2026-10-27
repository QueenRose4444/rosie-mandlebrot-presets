"""One-off: seed the list with the app's built-in places and three colour
schemes, as issues (their pages) and release files, using a running app for
the codes.

usage: GH_TOKEN=... REPO=owner/name python tools/seed.py APP_URL
"""
import json
import os
import sys
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import add_entry  # noqa: E402
import github  # noqa: E402

REPO = os.environ['REPO']
app = sys.argv[1].rstrip('/')


def app_call(path, body=None):
    req = urllib.request.Request(f'{app}{path}', data=None if body is None else json.dumps(body).encode(),
                                 headers={'content-type': 'application/json'}, method='GET' if body is None else 'POST')
    with urllib.request.urlopen(req) as r:
        return json.load(r)


def body(code, why, tags):
    return f'### Share code\n\n```text\n{code}\n```\n\n### What makes it good\n\n{why}\n\n### Tags\n\n{tags}\n'


places = [p for p in app_call('/api/presets') if p.get('kind') not in ('found',) and not p.get('shared')]
pals = {p['name']: p for p in app_call('/api/palettes')}
stops = lambda name: pals[name]['stops']
colours = [
    ('Neon cycle', {'stops': stops('neon'), 'play': {'cycle': 0.25}},
     'Neon that slides along as the video plays, there and back, so there is never a seam.', 'colours, cycling'),
    ('Aurora drift', {'stops': stops('aurora'), 'play': {'random': {'mode': 'drift', 'style': 'together', 'seed': 17, 'drift': 0.15}}},
     'Aurora whose colours wander slowly, each stop on its own beat.', 'colours, random, drift'),
    ('Sunset to deep space', {'stops': stops('sunset'), 'play': {'keys': [
        {'at': 0, 'stops': [{'pos': p, 'rgb': [int(c[i:i + 2], 16) for i in (1, 3, 5)]} for p, c in stops('sunset')]},
        {'at': 0.5, 'stops': [{'pos': p, 'rgb': [int(c[i:i + 2], 16) for i in (1, 3, 5)]} for p, c in stops('wine')]},
        {'at': 1, 'stops': [{'pos': p, 'rgb': [int(c[i:i + 2], 16) for i in (1, 3, 5)]} for p, c in stops('deepspace')]}], 'fade': 2}},
     'Sunset at the top, wine halfway down and deep space at the end, fading over two seconds.', 'colours, along the zoom'),
]

made = []
for p in places:
    code = app_call('/api/share/place', {'name': p['name'], 'julia': False})['code']
    made.append((f"Share: {p['name']}", body(code, p.get('description') or '', f"built-in, {p.get('kind') or 'view'}")))
for name, c, why, tags in colours:
    code = app_call('/api/share/colours', {'name': name, 'stops': c['stops'], 'inside': None, 'play': c['play']})['code']
    made.append((f'Share: {name}', body(code, why, tags)))

existing = {i['title']: i for i in github.pages(f'/repos/{REPO}/issues?state=all')}
for title, text in made:
    issue = existing.get(title) or github.call('POST', f'/repos/{REPO}/issues', {'title': title, 'body': text, 'labels': ['submission']})
    entry = add_entry.add(issue['number'], issue)
    github.call('POST', f"/repos/{REPO}/issues/{issue['number']}/labels", {'labels': ['listed']})
    print(issue['number'], entry['kind'], entry['name'], flush=True)
