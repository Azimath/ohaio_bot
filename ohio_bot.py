import tweepy

import pytz

from datetime import datetime
import json

from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.jobstores.memory import MemoryJobStore
from apscheduler.triggers.cron import CronTrigger
from apscheduler.executors.pool import ThreadPoolExecutor

io_timezone = pytz.timezone("America/Toronto")
io_tweet_filename = "filtered_io_tweets.txt"

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

    api.unretweet(tweetid)
    #api.retweet(tweetid)

if __name__ == "__main__":
    tweetdatetimes = []
    with open(io_tweet_filename, "r") as io_tweet_file:
        io_tweets = json.loads(io_tweet_file.read())
        for tweet in io_tweets:
            tweetdatetime = datetime.strptime(tweet["date"], '%Y-%m-%dT%H:%M:%S%z')
            tweetEST = tweetdatetime.astimezone(tz=io_timezone)
            
            ct = CronTrigger(month=tweetEST.month, day=tweetEST.day, hour=tweetEST.hour, minute=tweetEST.minute, second=tweetEST.second)
            scheduler.add_job(retweet, trigger=ct, args=(tweet["id"],))

    scheduler.print_jobs()
    scheduler.start()