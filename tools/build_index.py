"""Build index.json: every listed entry with its stars (👍 on its issue) and
downloads (of its release file). The workflow signs it; the app checks the
signature before it shows anything.

usage: GH_TOKEN=... REPO=owner/name python tools/build_index.py
Prints "changed" or "unchanged".
"""
import datetime
import json
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import github  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
REPO = os.environ['REPO']


def main():
    entries = [json.loads(p.read_text(encoding='utf-8')) for p in sorted((ROOT / 'entries').glob('*.json'))]
    assets = {}
    for rel in github.pages(f'/repos/{REPO}/releases'):
        for a in rel['assets']:
            assets[a['name']] = a
    out = []
    for e in sorted(entries, key=lambda e: e['id']):
        issue = github.call('GET', f'/repos/{REPO}/issues/{e["id"]}')
        if issue.get('state') != 'open' or 'removed' in [l['name'] for l in issue.get('labels', [])]:
            continue
        a = assets.get(e['asset'])
        if not a:
            continue
        out.append({**e,
                    'stars': issue.get('reactions', {}).get('+1', 0),
                    'downloads': a['download_count'],
                    'page': issue['html_url'],
                    'download': a['browser_download_url']})
    path = ROOT / 'index.json'
    old = json.loads(path.read_text(encoding='utf-8')) if path.exists() else {}
    if old.get('entries') == out:
        print('unchanged')
        return
    index = {'version': 1, 'repo': REPO,
             'generated': datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ'),
             'entries': out}
    # Exactly these bytes are signed and published: LF on every system.
    path.write_bytes((json.dumps(index, indent=1, sort_keys=True, ensure_ascii=False) + '\n').encode('utf-8'))
    print('changed')


if __name__ == '__main__':
    main()
