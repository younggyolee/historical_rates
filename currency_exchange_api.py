import requests
import json
import datetime
from typing import List
from fastapi import HTTPException

def convert_unix_timestamp_to_date(unix_timestamp: int) -> str:
    return datetime.date.fromtimestamp(int(str(unix_timestamp)[:10])).strftime('%Y-%m-%d')

def get_historical_rates(
    base_currency: str,
    quote_currency: str,
    start_date: str,
    end_date: str
) -> List[list]:
    '''
    input:
        base_currency = 'USD'
        quote_currency = 'KRW'
        start_date = '2022-12-04'
        end_date = '2022-12-05'

    return:
        List[[date: str, rate: str]]
        [['2022-12-04', '1294.872107'], ['2022-12-05', '1299.220955']]
    '''

    url = (
        "https://www.oanda.com/fx-for-business/historical-rates/api/data/update/" +
        "?widget=1" +
        "&source=OANDA" +
        "&display=absolute" +
        "&adjustment=0" +
        "&data_range=c" +
        "&period=daily" +
        "&price=bid" +
        "&view=graph" +
        "&base_currency=" + base_currency +
        "&quote_currency_0=" + quote_currency +
        "&start_date=" + start_date +
        "&end_date=" + end_date
    )
    res = requests.get(url)
    if res.status_code == 200:
        data = json.loads(res.text)['widget'][0]['data']
        return list(map(lambda x: [convert_unix_timestamp_to_date(x[0]), x[1]], data))
    elif res.status_code == 400:
        print(res.text)
        raise HTTPException(status_code=400, detail='Invalid input')
    else:
        print(res.text)
        raise HTTPException(status_code=500, detail='External API error')
