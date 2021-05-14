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
import pandas as pd
from datetime import datetime


def getData(url,nonce):
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
    url_transactions =   'https://www.coinspot.com.au/api/ro/my/transactions'
    url_deposits = 'https://www.coinspot.com.au/api/ro/my/deposits'

    NONCE_COUNTER = count(int(time() * 1000))
    n = next(NONCE_COUNTER)
    data = getData(url_transactions,n)
    df_buy  = pd.json_normalize(data, 'buyorders')
    df_sell =pd.json_normalize(data, 'sellorders')
    n = next(NONCE_COUNTER)
    data = getData(url_deposits,n)
    df_deposit = pd.json_normalize(data, 'deposits')
    n = next(NONCE_COUNTER)
    blnc_json = []
    for b in getData(url_blnce,n).get("balances"):
        for k in b:
            blnc_json.append({'coin':k,
                              'balance':b[k].get('balance'),
                              'aud-balance':b[k].get('audbalance'),
                              'rate':b[k].get('rate')
                              })
    df_balance = pd.json_normalize(blnc_json)
    df_buy["curr_rate"] = 0.0000000
    for index,row in df_buy.iterrows():
        coin = row['market'][0:row['market'].find("/")]
        r = df_balance.loc[df_balance["coin"] == coin]["rate"]
        df_buy.at[index,'curr_rate'] = r

    df_buy["curr_value"]=df_buy["curr_rate"]*df_buy["amount"]
    df_buy["profit"] = df_buy["curr_value"] / df_buy["audtotal"]

    d1 = datetime.now().strftime("%Y-%m-%d %H-%M-%S")
    df_buy[["market","amount","audtotal","curr_rate","curr_value","profit"]].sort_values(by=['profit'],ascending=False).to_csv(f"[{d1}] status.csv")
    print("the end")



