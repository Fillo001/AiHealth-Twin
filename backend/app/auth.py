import os, time, hmac, hashlib, base64
from typing import Tuple
from eth_account.messages import encode_defunct
from eth_account import Account

SECRET = os.environ.get("JWT_SECRET", "dev_secret_change_me")

# Extremely simplified token for demo purposes (NOT production-ready)
def issue_token(wallet: str) -> str:
    payload = f"{wallet}|{int(time.time())}"
    sig = hmac.new(SECRET.encode(), payload.encode(), hashlib.sha256).digest()
    token = base64.urlsafe_b64encode(payload.encode() + b"." + sig).decode()
    return token

def verify_token(token: str) -> str:
    raw = base64.urlsafe_b64decode(token.encode())
    payload, sig = raw.split(b".", 1)
    expected = hmac.new(SECRET.encode(), payload, hashlib.sha256).digest()
    if not hmac.compare_digest(sig, expected):
        raise ValueError("Bad signature")
    wallet = payload.decode().split("|")[0]
    return wallet

# --- EIP-191 signature verification helper ---
def verify_eip191_message(wallet: str, signature: str, message: str) -> bool:
    """
    Verifies that `signature` is an EIP-191 (personal_sign) signature of `message` by `wallet`.
    `wallet` should be the hex address (0x...).
    """
    try:
        eth_message = encode_defunct(text=message)
        recovered = Account.recover_message(eth_message, signature=signature)
        return recovered.lower() == wallet.lower()
    except Exception:
        return False
