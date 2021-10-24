import tweepy

import pytz

import random

from datetime import datetime, timedelta
import json

from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.jobstores.memory import MemoryJobStore
from apscheduler.triggers.cron import CronTrigger
from apscheduler.executors.pool import ThreadPoolExecutor

io_timezone = pytz.timezone("America/Toronto")
io_tweet_filename = "yes.txt"

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

jobstores = {
    'default': MemoryJobStore()
}
executors = {
    'default': ThreadPoolExecutor(1)
}
job_defaults = {
    'coalese': False
}

scheduler = BlockingScheduler(jobstores=jobstores, executors=executors, job_defaults=job_defaults, timezone=io_timezone)

def retweet(tweetid):
    import tokens
    auth = tweepy.OAuthHandler(tokens.CONSUMER_KEY, tokens.CONSUMER_SECRET)
    auth.set_access_token(tokens.ACCESS_TOKEN, tokens.ACCESS_SECRET)

    api = tweepy.API(auth)

    print("Retweeting {}".format(tweetid))

    api.unretweet(tweetid)
    #api.retweet(tweetid)

def retweet_random(tweetids):
    import tokens
    auth = tweepy.OAuthHandler(tokens.CONSUMER_KEY, tokens.CONSUMER_SECRET)
    auth.set_access_token(tokens.ACCESS_TOKEN, tokens.ACCESS_SECRET)

    api = tweepy.API(auth)

    tweetid = random.choice(tweetids)

    print("Retweeting {}".format(tweetid))
    
    api.unretweet(tweetid)
    #api.retweet(tweetid)

if __name__ == "__main__":
    tweetdatetimes = []
    with open(io_tweet_filename, "r") as io_tweet_file:
        io_tweets = json.loads(io_tweet_file.read())

        tweetdays = []
        io_tweet_ids = []
        for tweet in io_tweets:
            tweetdatetime = datetime.strptime(tweet["date"], '%Y-%m-%dT%H:%M:%S%z')
            tweetEST = tweetdatetime.astimezone(tz=io_timezone)
            
            ct = CronTrigger(month=tweetEST.month, day=tweetEST.day, hour=tweetEST.hour, minute=tweetEST.minute, second=tweetEST.second)
            scheduler.add_job(retweet, trigger=ct, args=(tweet["id"],))

            tweetdays.append(tweetEST)
            io_tweet_ids.append(tweet["id"])

    for missing in missing_dates(tweetdays):
        ct = CronTrigger(month=missing.month, day=missing.day, hour=random.randint(6, 12), minute=random.randint(0, 59), second=random.randint(0, 59))
        scheduler.add_job(retweet_random, trigger=ct, args=(io_tweet_ids,))

    scheduler.print_jobs()
    print("Scheduled {} tweets!".format(len(scheduler.get_jobs())))
    scheduler.start()