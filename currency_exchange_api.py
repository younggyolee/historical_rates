import requests
import json
import datetime
# from typing import List

def convert_unix_timestamp_to_date(unix_timestamp: int) -> datetime.date:
    return datetime.date.fromtimestamp(int(str(unix_timestamp)[:10]))

def get_historical_rate(
    base_currency: str,
    quote_currency: str,
    start_date: str,
    end_date: str
):
# ) -> List[List[datetime.date, str]]:
    '''
    input:
        base_currency = 'USD'
        quote_currency = 'KRW'
        start_date = '2022-12-04'
        end_date = '2022-12-05'

    return:
        List[[date: datetime.date, rate: str]]
        [[datetime.date(2022, 12, 04), '1294.872107'], [datetime.date(2022, 12, 05), '1299.220955']]
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
    data = json.loads(res.text)['widget'][0]['data']
    return list(map(lambda x: [convert_unix_timestamp_to_date(x[0]), x[1]], data))
