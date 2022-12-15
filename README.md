# Tasks
1. Create a Python API server which provides currency exchange rates data.
    1. [ x ] initialize your application
    2. [ x ] create Oanda API client function and test it.
    3. [ x ] decide the url pattern for exchange rates data API
    4. [ x ] implement the API endpoint
    5. [ x ] test if the API endpoint works fine.
2. Write a brief documentation about the service.
    1. [ x ] How is it implemented
    2. [ x ] What problems can happen in the current implementation
    3. [ x ] How can it be improved in the future
    4. [ x ] Any other things that we should know about

------

# 1. How is it implemented?

I tried to minimize the number of Oanda API queries.

1. Firstly, iterate through all the `queries` in the request URL.

    1. For each `(base_currency, quote_currency)` pair, find the `minimum_date` and `maximum_date` and keep them in `currency_pair_to_interval` dictionary.

    2. Also add `(base_currency, quote_currency, date)` tuple into `key_to_rate` dictionary as a `key`. This will be used to save only the required rates among consecutive rates (between `start_date` and `end_date`) into in-memory variable `key_to_rate`.

2. Using `currency_pair_to_interval` dictionary, send only one query to Oanda API per each pair (using `start_date` and `end_date` that covers all the requested dates).

3. And among all the fetched historical rates, save the ones that were requested from the user into in-memory key-value dictionary `key_to_rate`.

4. Then iterate through the requested `keys` again, and map each `rate` onto each `key` using `key_to_rate`. Then return mapped the `rates` in the same order as `keys`.

# 2. What problems can happen in the current implementation?

- Currently, Oanda API returns only for the last 180 days, without a specific interval limit (difference between `start_date` and `end_date`). But it is possible that such API would have a limit on the interval.
    - In such cases, let's say, maximum interval of 1 year between `start_date` and `end_date`, then I will need to divide the request into smaller pieces to fit into the limit.

- If the fetched data from Oanda API is too big, then we can have out of memory error. (but since 1 year worth of historical rates data only occupies 12kb. 100 year data will only be 1.2MB, so not likely a problem in the current problem)

- If the requested data are very far from each other, it may be inefficient to use `minimum_date` and `maximum_date`
    - For example, if `query1=USD,KRW,1980-01-01`, `query2=USD,KRW,2022-01-01`, then we are fetching 42 years' (42 years * 365 days = 15330 days) worth of data, while we only need 2 days' data.

# 3. How can it be improved in the future?

- By pre-saving all ISO currency codes in a hash set, I can validate currency code before sending request to Oanda API
    - It will contribute further to reduce the Oanda API calls for invalid requests
    - But it will come with a slight performance loss

- DB saving(caching): If Oanda API cost is significantly higher than saving the data into DB and querying it (or if there is a limit on the number of Oanda API call), it will make sense to cache all / or popular key & rate pairs into DB, so that we don't make repeated Oanda API calls.
    - I didn't implemented this because if this was viable, then this microservice would rather download the whole historical data into a DB and query from there. But this assignment didn't choose that path and rather asked me to query Oanda API.
    - Oanda API call itself looks to me as a DB query in the real world.

# 4. Any other things that we should know about?

- Which one is more expensive: API call or saving data & querying from DB?
- What is the maximum interval between `start_date` and `end_date` for Oanda API?

# Sample request

- Each `query` should be in the format of `query={base_currency},{quote_currency},{date.Format(YYYY-MM-DD)}`.
- Multiple `queries` can be included in the URL.

For example, when `queries` in the format of `({base_currency}, {quote_currency}, {date})` are like below,

```
query1 = ('USD', 'KRW', '2022-12-02')
query2 = ('USD', 'KRW', '2022-12-03')
query3 = ('USD', 'JPY', '2022-11-01')
```

the request URL is 
`http://localhost:8000/historical-rates/?query=USD,KRW,2022-12-02&query=USD,KRW,2022-12-03&query=USD,JPY,2022-11-01`


# Performance comparison: brute force vs batch request
- When requesting 60 days' worth of data for `(base=USD and quote=KRW)` and `(base=USD, quote=JPY)` pairs. (total 120 rows)

  - **brute force** (120 Oanada API calls) : **38.8s** (avg of 5 tries)
  - **batch processing** (2 Oanda API calls) : **0.6s** (avg of 5 tries)

- request URL = `http://localhost:8000/historical-rates/?query=USD,KRW,2022-10-01&query=USD,KRW,2022-10-02&query=USD,KRW,2022-10-03&query=USD,KRW,2022-10-04&query=USD,KRW,2022-10-05&query=USD,KRW,2022-10-06&query=USD,KRW,2022-10-07&query=USD,KRW,2022-10-08&query=USD,KRW,2022-10-09&query=USD,KRW,2022-10-10&query=USD,KRW,2022-10-11&query=USD,KRW,2022-10-12&query=USD,KRW,2022-10-13&query=USD,KRW,2022-10-14&query=USD,KRW,2022-10-15&query=USD,KRW,2022-10-16&query=USD,KRW,2022-10-17&query=USD,KRW,2022-10-18&query=USD,KRW,2022-10-19&query=USD,KRW,2022-10-20&query=USD,KRW,2022-10-21&query=USD,KRW,2022-10-22&query=USD,KRW,2022-10-23&query=USD,KRW,2022-10-24&query=USD,KRW,2022-10-25&query=USD,KRW,2022-10-26&query=USD,KRW,2022-10-27&query=USD,KRW,2022-10-28&query=USD,KRW,2022-10-29&query=USD,KRW,2022-10-30&query=USD,KRW,2022-10-31&query=USD,KRW,2022-11-01&query=USD,KRW,2022-11-02&query=USD,KRW,2022-11-03&query=USD,KRW,2022-11-04&query=USD,KRW,2022-11-05&query=USD,KRW,2022-11-06&query=USD,KRW,2022-11-07&query=USD,KRW,2022-11-08&query=USD,KRW,2022-11-09&query=USD,KRW,2022-11-10&query=USD,KRW,2022-11-11&query=USD,KRW,2022-11-12&query=USD,KRW,2022-11-13&query=USD,KRW,2022-11-14&query=USD,KRW,2022-11-15&query=USD,KRW,2022-11-16&query=USD,KRW,2022-11-17&query=USD,KRW,2022-11-18&query=USD,KRW,2022-11-19&query=USD,KRW,2022-11-20&query=USD,KRW,2022-11-21&query=USD,KRW,2022-11-22&query=USD,KRW,2022-11-23&query=USD,KRW,2022-11-24&query=USD,KRW,2022-11-25&query=USD,KRW,2022-11-26&query=USD,KRW,2022-11-27&query=USD,KRW,2022-11-28&query=USD,KRW,2022-11-29&query=USD,JPY,2022-10-01&query=USD,JPY,2022-10-02&query=USD,JPY,2022-10-03&query=USD,JPY,2022-10-04&query=USD,JPY,2022-10-05&query=USD,JPY,2022-10-06&query=USD,JPY,2022-10-07&query=USD,JPY,2022-10-08&query=USD,JPY,2022-10-09&query=USD,JPY,2022-10-10&query=USD,JPY,2022-10-11&query=USD,JPY,2022-10-12&query=USD,JPY,2022-10-13&query=USD,JPY,2022-10-14&query=USD,JPY,2022-10-15&query=USD,JPY,2022-10-16&query=USD,JPY,2022-10-17&query=USD,JPY,2022-10-18&query=USD,JPY,2022-10-19&query=USD,JPY,2022-10-20&query=USD,JPY,2022-10-21&query=USD,JPY,2022-10-22&query=USD,JPY,2022-10-23&query=USD,JPY,2022-10-24&query=USD,JPY,2022-10-25&query=USD,JPY,2022-10-26&query=USD,JPY,2022-10-27&query=USD,JPY,2022-10-28&query=USD,JPY,2022-10-29&query=USD,JPY,2022-10-30&query=USD,JPY,2022-10-31&query=USD,JPY,2022-11-01&query=USD,JPY,2022-11-02&query=USD,JPY,2022-11-03&query=USD,JPY,2022-11-04&query=USD,JPY,2022-11-05&query=USD,JPY,2022-11-06&query=USD,JPY,2022-11-07&query=USD,JPY,2022-11-08&query=USD,JPY,2022-11-09&query=USD,JPY,2022-11-10&query=USD,JPY,2022-11-11&query=USD,JPY,2022-11-12&query=USD,JPY,2022-11-13&query=USD,JPY,2022-11-14&query=USD,JPY,2022-11-15&query=USD,JPY,2022-11-16&query=USD,JPY,2022-11-17&query=USD,JPY,2022-11-18&query=USD,JPY,2022-11-19&query=USD,JPY,2022-11-20&query=USD,JPY,2022-11-21&query=USD,JPY,2022-11-22&query=USD,JPY,2022-11-23&query=USD,JPY,2022-11-24&query=USD,JPY,2022-11-25&query=USD,JPY,2022-11-26&query=USD,JPY,2022-11-27&query=USD,JPY,2022-11-28&query=USD,JPY,2022-11-29`
