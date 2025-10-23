# server/app/signing_utils.py
import json
from pathlib import Path
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding, rsa
from cryptography.exceptions import InvalidSignature
import base64

KEY_DIR = Path(__file__).resolve().parents[1] / 'keys'
KEY_DIR.mkdir(parents=True, exist_ok=True)
PRIVATE_KEY_PATH = KEY_DIR / 'private_key.pem'
PUBLIC_KEY_PATH = KEY_DIR / 'public_key.pem'

def ensure_keys():
    if PRIVATE_KEY_PATH.exists() and PUBLIC_KEY_PATH.exists():
        return
    # generate RSA key pair
    private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption()
    )
    PRIVATE_KEY_PATH.write_bytes(pem)
    pub = private_key.public_key().public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )
    PUBLIC_KEY_PATH.write_bytes(pub)

def sign_manifest(manifest: dict) -> str:
    ensure_keys()
    # sign canonicalized manifest (sorted keys)
    data = json.dumps(manifest, separators=(',', ':'), sort_keys=True).encode('utf-8')
    from cryptography.hazmat.primitives import hashes
    from cryptography.hazmat.primitives.asymmetric import padding
    from cryptography.hazmat.primitives import serialization
    private_key = serialization.load_pem_private_key(PRIVATE_KEY_PATH.read_bytes(), password=None)
    sig = private_key.sign(data, padding.PKCS1v15(), hashes.SHA256())
    return base64.b64encode(sig).decode('ascii')

def verify_manifest(manifest: dict, signature: str) -> bool:
    ensure_keys()
    data = json.dumps(manifest, separators=(',', ':'), sort_keys=True).encode('utf-8')
    pub = serialization.load_pem_public_key(PUBLIC_KEY_PATH.read_bytes())
    try:
        pub.verify(base64.b64decode(signature), data, padding.PKCS1v15(), hashes.SHA256())
        return True
    except InvalidSignature:
        return False
