# cli/sign.py
"""Signing CLI for Plugin Store (admin use)
Usage: python cli/sign.py /path/to/manifest.json"""

import sys, json
from pathlib import Path
from server.app import signing_utils

def main(argv):
    if len(argv) != 2:
        print('usage: sign.py path/to/manifest.json')
        return 2
    p = Path(argv[1])
    if not p.exists():
        print('manifest not found')
        return 2
    mf = json.loads(p.read_text(encoding='utf-8'))
    sig = signing_utils.sign_manifest(mf)
    mf['signature'] = sig
    p.write_text(json.dumps(mf, ensure_ascii=False, indent=2), encoding='utf-8')
    print('signed manifest, signature:', sig)
    return 0

if __name__ == '__main__':
    raise SystemExit(main(sys.argv))
