"""Reading and checking Rosie_Mandlebrot share codes (rmp1. places, rmc1.
colour schemes), as strictly as the app does before anything is listed."""
import base64
import json
import re

DECIMAL = re.compile(r'^[+-]?(\d+\.?\d*|\.\d+)([eE][+-]?\d{1,6})?$')
HEX = re.compile(r'^#?[0-9a-fA-F]{6}$')
MAX_CODE = 200_000
MAX_DIGITS = 2_000


class BadCode(ValueError):
    pass


def _name_ok(n):
    return isinstance(n, str) and n.strip() != '' and len(n) <= 60 and not any(ord(c) < 32 or ord(c) == 127 for c in n)


def decode(code):
    """(kind, data) for a code, or BadCode with the reason."""
    code = ''.join(code.split())
    if len(code) > MAX_CODE:
        raise BadCode('the code is too long')
    if '.' not in code:
        raise BadCode('not a share code (it should start rmp1. or rmc1.)')
    prefix, body = code.split('.', 1)
    if prefix not in ('rmp1', 'rmc1'):
        raise BadCode(f'unknown kind of code: {prefix}')
    if not re.fullmatch(r'[A-Za-z0-9_\-+/]*=*', body):
        raise BadCode('the code has characters a code cannot have')
    try:
        data = json.loads(base64.urlsafe_b64decode(body + '=' * (-len(body) % 4)))
    except Exception as e:  # noqa: BLE001 - any failure is a damaged code
        raise BadCode(f'the code is damaged: {e}') from None
    if not isinstance(data, dict):
        raise BadCode('the code is damaged')
    if prefix == 'rmp1':
        check_place(data)
        return 'place', data
    check_colours(data)
    return 'colours', data


def check_place(p):
    if not _name_ok(p.get('name')):
        raise BadCode('a place needs a name of 1 to 60 printable characters')
    for k in ('re', 'im'):
        v = p.get(k)
        if not isinstance(v, str) or len(v) > MAX_DIGITS or not DECIMAL.match(v):
            raise BadCode('a place\'s coordinates must be plain decimal numbers')
    end = p.get('end')
    if not isinstance(end, (int, float)) or not (1e-300 <= end <= 10):
        raise BadCode('a place\'s depth must be between 10 and 1e-300')
    if p.get('period') is not None and not (isinstance(p['period'], int) and 0 <= p['period'] <= 10_000_000):
        raise BadCode('bad period')
    if p.get('base') is not None and not re.fullmatch(r'[a-z0-9_]{1,40}', str(p['base'])):
        raise BadCode('bad base preset')
    if p.get('interest') is not None and not (isinstance(p['interest'], (int, float)) and 0 <= p['interest'] <= 100):
        raise BadCode('bad interest')


def check_colours(c):
    if not _name_ok(c.get('name')):
        raise BadCode('a colour scheme needs a name of 1 to 60 printable characters')
    stops = c.get('stops')
    if not isinstance(stops, list) or not 2 <= len(stops) <= 64:
        raise BadCode('a colour scheme has 2 to 64 stops')
    for s in stops:
        if not (isinstance(s, list) and len(s) == 2 and isinstance(s[0], (int, float)) and 0 <= s[0] <= 1 and isinstance(s[1], str) and HEX.match(s[1])):
            raise BadCode('every stop is [position 0..1, "#rrggbb"]')
    if c.get('inside') is not None and not (isinstance(c['inside'], str) and HEX.match(c['inside'])):
        raise BadCode('bad inside colour')
    play = c.get('play')
    if play is not None:
        if not isinstance(play, dict) or len(play.get('keys') or []) > 32:
            raise BadCode('bad colour play')
        for k in play.get('keys') or []:
            if len(k.get('stops') or []) > 64:
                raise BadCode('too many stops in a key')


def summary(kind, data):
    """What the list shows about an entry, from its code."""
    if kind == 'place':
        return {'depth': data['end'], 'julia': bool(data.get('julia')), 'interest': data.get('interest'), 'base': data.get('base')}
    play = data.get('play') or {}
    return {'stops': len(data['stops']), 'play': bool(play)}
