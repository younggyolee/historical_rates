import collections
from typing import List, Dict
from fastapi import FastAPI, HTTPException
from currency_exchange_api import get_historical_rates

app = FastAPI()

MIN_DATE = '1900-01-01'
MAX_DATE = '2999-12-31'

class Interval:
    def __init__(self, start_date: str=MAX_DATE, end_date: str=MIN_DATE):
        self.start_date = start_date
        self.end_date = end_date

def validate_raw_key(raw_key: str):
    if len(raw_key) != 14:
        return False
    return True

def validate_raw_key_list(raw_key_list: List[str]):
    if not raw_key_list:
        raise HTTPException(status_code=400, detail='Invalid input: Empty keys')
    for raw_key in raw_key_list:
        if not validate_raw_key(raw_key):
            raise HTTPException(status_code=400, detail=f'Invalid input: {raw_key}')

def convert_to_key(raw_key: str):
    # raw_key = 'USDKRW20221202'
    base_currency = raw_key[: 3].upper()
    quote_currency = raw_key[3 : 6].upper()
    date = f'{raw_key[6 : 10]}-{raw_key[10 : 12]}-{raw_key[12 : 14]}'
    return (base_currency, quote_currency, date)

@app.get("/historical-rates/")
def read_root(queries: str):
    raw_key_list = queries.split(',')
    validate_raw_key_list(raw_key_list)
    key_list = [convert_to_key(raw_key) for raw_key in raw_key_list]

    currency_pairs = collections.defaultdict(Interval)
    key_to_rate: Dict[tuple, str] = {} # (base_currency, quote_currency, date) => exchange_rate
                                       # e.g. {('USD', 'KRW', '2022-12-02'): '1299.369441'}
    for key in key_list:
        key_to_rate[key] = ''

        base_currency, quote_currency, date = key
        interval = currency_pairs[(base_currency, quote_currency)]
        interval.start_date = min(interval.start_date, date)
        interval.end_date = max(interval.end_date, date)

    for pair, interval in currency_pairs.items():
        base_cur, quote_cur = pair
        start_date, end_date = interval.start_date, interval.end_date
        fetched = get_historical_rates(base_cur, quote_cur, start_date, end_date)
        for date, rate in fetched:
            key = (base_cur, quote_cur, date)
            if key in key_to_rate:
                key_to_rate[key] = rate

    return [key_to_rate[key] for key in key_list]
