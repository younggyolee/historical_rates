from typing import List
from fastapi import FastAPI, HTTPException
import currency_exchange_api

app = FastAPI()

class Key:
    def __init__(self, base_currency, quote_currency, date):
        self.base_currency = base_currency
        self.quote_currency = quote_currency
        self.date = date

def convert_to_key(raw_key: str) -> Key:
    # raw_key = 'USDKRW20221202'
    base_currency = raw_key[: 3].upper()
    quote_currency = raw_key[3 : 6].upper()
    date = f'{raw_key[6 : 10]}-{raw_key[10 : 12]}-{raw_key[12 : 14]}'
    return Key(base_currency, quote_currency, date)

def validate_raw_key(raw_key: str):
    if len(raw_key) != 14:
        return False
    return True

def validate_raw_key_list(raw_key_list: List[str]):
    for raw_key in raw_key_list:
        if not validate_raw_key(raw_key):
            raise HTTPException(status_code=400, detail=f'Invalid input : {raw_key}')

@app.get("/historical-rates/")
def read_root(keys: str):
    raw_key_list = keys.split(',')
    validate_raw_key_list(raw_key_list)
    key_list: List[Key] = [convert_to_key(raw_key) for raw_key in raw_key_list]

    res = []
    for key in key_list:
        rates = currency_exchange_api.get_historical_rate(
            key.base_currency,
            key.quote_currency,
            key.date, key.date
        )
        res.append(rates[0][1])
    return res
