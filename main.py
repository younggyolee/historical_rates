import collections
from typing import List, Dict, Tuple
from fastapi import FastAPI, HTTPException
from currency_exchange_api import get_historical_rates

app = FastAPI()

MIN_DATE = '0000-01-01'
MAX_DATE = '9999-99-99'

class Key:
    def __init__(self, base_currency, quote_currency, date):
        self.base_currency = base_currency
        self.quote_currency = quote_currency
        self.date = date

class Interval:
    def __init__(self, start_date: str=MAX_DATE, end_date: str=MIN_DATE):
        self.start_date = start_date
        self.end_date = end_date

    def __repr__(self):
        return f'start_date: {self.start_date}, end_date: {self.end_date}'

def convert_to_key_list(raw_key_list: List[str]) -> List[Key]:
    return [convert_to_key(raw_key) for raw_key in raw_key_list]

def convert_to_key(raw_key: str) -> Key:
    # raw_key = 'USDKRW20221202'
    base_currency = raw_key[: 3].upper()
    quote_currency = raw_key[3 : 6].upper()
    date = f'{raw_key[6 : 10]}-{raw_key[10 : 12]}-{raw_key[12 : 14]}'
    return Key(base_currency, quote_currency, date)

def convert_to_tuple(key: Key) -> Tuple[str, str, str]:
    return (key.base_currency, key.quote_currency, key.date)

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
    key_list = convert_to_key_list(raw_key_list)

    currency_pairs = collections.defaultdict(Interval)
    key_tuple_to_rate: Dict[tuple, str] = {} # (base_cur, quote_cur, date) => exchange_rate
                                             # e.g. {('USD', 'KRW', '2022-12-02'): '1299.369441'}
    for key in key_list:
        interval = currency_pairs[(key.base_currency, key.quote_currency)]
        interval.start_date = min(interval.start_date, key.date)
        interval.end_date = max(interval.end_date, key.date)

        key_tuple_to_rate[convert_to_tuple(key)] = ''

    for pair, interval in currency_pairs.items():
        base_cur, quote_cur = pair
        start_date, end_date = interval.start_date, interval.end_date
        fetched = get_historical_rates(base_cur, quote_cur, start_date, end_date)
        for date, rate in fetched:
            key = (base_cur, quote_cur, date)
            if key in key_tuple_to_rate:
                key_tuple_to_rate[key] = rate

    return [key_tuple_to_rate[convert_to_tuple(key)] for key in key_list]
