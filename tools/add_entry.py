"""List an approved submission: read the share code from issue N, check it,
attach it to a release (so every download is counted) and write
entries/N.json. Comments on the issue either way.

usage: GH_TOKEN=... REPO=owner/name python tools/add_entry.py N
"""
import datetime
import json
import os
import re
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import codes  # noqa: E402
import github  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
REPO = os.environ['REPO']
ASSETS_PER_RELEASE = 900  # GitHub allows 1,000 assets on a release


def code_in(body):
    m = re.search(r'rm[pc]1\.[A-Za-z0-9_\-+/=\s]{8,}', body or '')
    if not m:
        raise codes.BadCode('no share code (rmp1.… or rmc1.…) in the issue')
    # A code ends at the first blank line or heading.
    return m.group(0).split('\n\n')[0].split('###')[0]


def section(body, title):
    m = re.search(rf'###\s*{re.escape(title)}\s*\n+(.*?)(?=\n###|\Z)', body or '', re.S)
    text = (m.group(1).strip() if m else '')
    return '' if text == '_No response_' else text


def release_with_room():
    rels = [r for r in github.pages(f'/repos/{REPO}/releases') if r['tag_name'].startswith('entries')]
    for r in sorted(rels, key=lambda r: r['tag_name']):
        if len(r['assets']) < ASSETS_PER_RELEASE:
            return r
    tag = 'entries' if not rels else f'entries-{len(rels) + 1}'
    return github.call('POST', f'/repos/{REPO}/releases', {
        'tag_name': tag, 'name': f'Shared places and colours ({tag})',
        'body': 'Every listed place and colour scheme is a file here, so downloads are counted. The app downloads them; there is nothing to install.'})


def add(n, issue=None):
    issue = issue or github.call('GET', f'/repos/{REPO}/issues/{n}')
    body = issue.get('body') or ''
    kind, data = codes.decode(code_in(body))
    code = ''.join(code_in(body).split())
    asset = f'{n}.{"rmp" if kind == "place" else "rmc"}'
    rel = release_with_room()
    if not any(a['name'] == asset for a in rel['assets']):
        upload = rel['upload_url'].split('{')[0]
        github.call('POST', f'{upload}?name={asset}', raw=code.encode(), content_type='text/plain', base='')
    entry = {
        'id': n,
        'kind': kind,
        'name': data['name'],
        'description': section(body, 'What makes it good')[:500],
        'tags': [t.strip().lower() for t in section(body, 'Tags').split(',') if t.strip()][:8],
        'author': issue['user']['login'],
        'created': issue['created_at'],
        'listed': datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ'),
        'asset': asset,
        'release': rel['tag_name'],
        'code': code,
        **codes.summary(kind, data),
    }
    (ROOT / 'entries' / f'{n}.json').write_bytes((json.dumps(entry, indent=1, sort_keys=True) + '\n').encode('utf-8'))
    return entry


if __name__ == '__main__':
    n = int(sys.argv[1])
    try:
        e = add(n)
        github.call('POST', f'/repos/{REPO}/issues/{n}/comments', {'body': f'Listed as **{e["name"]}**. It appears in the app\'s Community list within a few hours. Give this issue a 👍 to star it.'})
        github.call('POST', f'/repos/{REPO}/issues/{n}/labels', {'labels': ['listed']})
    except codes.BadCode as err:
        github.call('POST', f'/repos/{REPO}/issues/{n}/comments', {'body': f'This could not be listed: {err}. Edit the issue with a fresh code from the app (Share), then label it again.'})
        sys.exit(1)
