# needed for the binance API and websockets
from typing import Optional

import dateparser
import pytz
from binance.client import Client
import csv
import os
import time
import requests
from datetime import date, datetime

from binance.exceptions import UnknownDateFormat

client = Client()

def get_coins():
    with open('coins.txt', 'r') as f:
        coins = f.readlines()
        coins = [coin.strip('\n') for coin in coins]
    return coins


def get_historical_data(coin, since, kline_interval):
    """
    Args example:
    coin = 'BTCUSDT'
    since = '1 Jan 2021'
    kline_interval = Client.KLINE_INTERVAL_1MINUTE
    """
    if os.path.isfile(f'{coin}_{since}.csv'):
        print('Datafile already exists, loading file...')

    else:
        print(f'Fetching historical data for {coin}, this may take a few minutes...')

        start_time = time.perf_counter()

        #data = client.get_historical_klines(coin, kline_interval, since)

        url = "https://api.binance.com/api/v3/klines"
        param = {
        "symbol" : coin,
        "interval" : kline_interval,
         "startTime": convert_ts_str(since)
        }
        data = requests.get(url=url,params=param)
        #print(data.json())
        data = [item[0:5] for item in data.json()]

        # field names
        fields = ['timstamp', 'open', 'high', 'low', 'close']

        # save the data
        with open(f'{coin}_{since}.csv', 'w', newline='') as f:

            # using csv.writer method from CSV package
            write = csv.writer(f)

            write.writerow(fields)
            write.writerows(data)

        end_time = time.perf_counter()

        # calculate how long it took to produce the file
        time_elapsed = round(end_time - start_time)

        print(f'Historical data for {coin} saved as {coin}_{since}.csv. Time elapsed: {time_elapsed} seconds')
    return f'{coin}_{since}.csv'


def convert_ts_str(ts_str):
    if ts_str is None:
        return ts_str
    if type(ts_str) == int:
        return ts_str
    return date_to_milliseconds(ts_str)

def date_to_milliseconds(date_str: str) -> int:
    """Convert UTC date to milliseconds

    If using offset strings add "UTC" to date string e.g. "now UTC", "11 hours ago UTC"

    See dateparse docs for formats http://dateparser.readthedocs.io/en/latest/

    :param date_str: date in readable format, i.e. "January 01, 2018", "11 hours ago UTC", "now UTC"
    """
    # get epoch value in UTC
    epoch: datetime = datetime.utcfromtimestamp(0).replace(tzinfo=pytz.utc)
    # parse our date string
    d: Optional[datetime] = dateparser.parse(date_str, settings={'TIMEZONE': "UTC"})
    if not d:
        raise UnknownDateFormat(date_str)

    # if the date is not timezone aware apply UTC timezone
    if d.tzinfo is None or d.tzinfo.utcoffset(d) is None:
        d = d.replace(tzinfo=pytz.utc)

    # return the difference in time
    return int((d - epoch).total_seconds() * 1000.0)