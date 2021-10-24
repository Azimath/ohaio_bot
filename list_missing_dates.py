from datetime import date, timedelta, datetime
import json
import pytz
from itertools import tee

io_timezone = pytz.timezone("America/Toronto")

def pairwise(iterable): # Modified from https://stackoverflow.com/a/2315049
    "s -> (s0,s1), (s1,s2), (s2, s3), ..."
    a = iter(iterable)
    b = iter(iterable)

    next(b)
    return zip(a, b)

def missing_dates(dates): # https://stackoverflow.com/a/2315049
    for prev, curr in pairwise(sorted(dates)):
        i = prev
        while i + timedelta(1) < curr:
            i += timedelta(1)
            yield i

file_path = "yes.txt"
with open(file_path) as file:
    tweets = json.loads(file.read())
    dates = []
    for tweet in tweets:
        tweetdatetime = datetime.strptime(tweet["date"], '%Y-%m-%dT%H:%M:%S%z')
        tweetEST = tweetdatetime.astimezone(tz=io_timezone)

        dates.append(tweetEST.date())

    m = 0
    for missing in missing_dates(dates):
        print(missing)
        m += 1
    print("Missing {} tweets!".format(m))

