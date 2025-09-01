from .auth import issue_token, verify_token, verify_eip191_message

@app.post("/auth/signin", response_model=SignInResponse)
def signin(req: SignInRequest):
    """
    Expects a JSON body:
    {
      "wallet": "0xabc...",
      "signature": "0x...",   # signature of the nonce (or message)
      "nonce": "random-string-used-as-message"
    }
    The frontend should prompt the user to sign the nonce/message using personal_sign.
    """
    # verify signature
    ok = verify_eip191_message(req.wallet, req.signature, req.nonce)
    if not ok:
        raise HTTPException(status_code=401, detail="Invalid signature")
    token = issue_token(req.wallet)
    return SignInResponse(token=token)
