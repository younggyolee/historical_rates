import collections
from typing import List, Dict, Tuple
from fastapi import FastAPI, Query
from currency_exchange_api import get_historical_rates
from pydantic import Required

app = FastAPI()

MIN_DATE = '1900-01-01'
MAX_DATE = '2999-12-31'

class Interval:
    def __init__(self, start_date: str=MAX_DATE, end_date: str=MIN_DATE):
        self.start_date = start_date
        self.end_date = end_date

def get_key_to_rate(keys: List[tuple]):
    currency_pairs_to_interval = collections.defaultdict(Interval)
    key_to_rate: Dict[tuple, str] = {} # (base_currency, quote_currency, date) => exchange_rate
                                       # e.g. {('USD', 'KRW', '2022-12-02'): '1299.369441'}
    for key in keys:
        key_to_rate[key] = ''

        base_currency, quote_currency, date = key
        interval = currency_pairs_to_interval[(base_currency, quote_currency)]
        interval.start_date = min(interval.start_date, date)
        interval.end_date = max(interval.end_date, date)

    for pair, interval in currency_pairs_to_interval.items():
        base_cur, quote_cur = pair
        start_date, end_date = interval.start_date, interval.end_date
        fetched = get_historical_rates(base_cur, quote_cur, start_date, end_date)
        for date, rate in fetched:
            key = (base_cur, quote_cur, date)
            if key in key_to_rate:
                key_to_rate[key] = rate
    return key_to_rate

def convert_to_key(q: str) -> Tuple[str, str, str]:
    # 'USD,KRW,2022-12-02' -> ('USD', 'KRW', '2022-12-02')
    base_currency, quote_currency, date = q.split(',')
    return (base_currency, quote_currency, date)

@app.get("/historical-rates/", response_model=List[str])
def read_root(query: List[str] = Query(
    default=Required,
    regex='^[A-Z]{3}\,[A-Z]{3}\,[0-9]{4}-[0-9]{2}-[0-9]{2}$'
)):
    keys = [convert_to_key(q) for q in query]
    key_to_rate = get_key_to_rate(keys)
    return [key_to_rate[key] for key in keys]
