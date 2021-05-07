import requests
import os
import sys
import requests
import json
from time import time
import hmac
import hashlib
from itertools import count
import urllib.parse
import cred


def getData(url,type,nonce):
    api_key = cred.API_KEY
    api_secret_key = cred.API_SECRET_KEY

    payload = {
        'nonce': nonce
    }

    payload = json.dumps(payload, separators=(',', ':'))
    signature = hmac.new(api_secret_key, payload.encode('utf-8'), digestmod=hashlib.sha512).hexdigest()

    headers = {
        'Content-type': 'application/json',
        'key': api_key,
        'sign': signature
    }

    r = requests.post(url, headers=headers, data=payload)
    response = r.json()

    return response


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    url_blnce = 'https://www.coinspot.com.au/api/ro/my/balances'
    url_ord =   'https://www.coinspot.com.au/api/ro/my/orders'

    NONCE_COUNTER = count(int(time() * 1000))
    n = next(NONCE_COUNTER)
    for b in getData(url_blnce,"balance",n).get("balances"):
        for k in b:
            print(f"{k},{b[k].get('balance')},{b[k].get('audbalance')},{ b[k].get('rate')}")
