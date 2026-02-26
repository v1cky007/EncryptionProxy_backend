import os
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.primitives import hashes

def rekey(old_key, context=b""):
    nonce = os.urandom(16)
    new_key = HKDF(
        algorithm=hashes.SHA256(),
        length=32,
        salt=nonce,
        info=b"ZeroTrust-Rekey"
    ).derive(old_key + context)

    print("[REKEY] Session key rotated")
    return new_key
