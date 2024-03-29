import tweepy
import pytz
import random

import ohaio_markov

from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.jobstores.memory import MemoryJobStore
from apscheduler.triggers.cron import CronTrigger
from apscheduler.executors.pool import ThreadPoolExecutor

io_timezone = pytz.timezone("America/Toronto")
corpus_filename = "morning_dataset.txt"

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

def tweet(corpus_data):
    import tokens
    client = tweepy.Client(
        consumer_key=tokens.CONSUMER_KEY, consumer_secret=tokens.CONSUMER_SECRET,
        access_token=tokens.ACCESS_TOKEN, access_token_secret=tokens.ACCESS_SECRET
    )

    tweetText = ohaio_markov.generate_tweet(corpus_data)

    print("Tweeting {}\n".format(tweetText))

    client.create_tweet(text=tweetText)

def test_tweet():
    corpus_data = ohaio_markov.load_corpus(corpus_filename)
    tweet(corpus_data)

if __name__ == "__main__":
    print("OHAAAAAIIIIOOOOO!")
    
    corpus_data = ohaio_markov.load_corpus(corpus_filename)

    ct = CronTrigger(hour=8, minute=0, second=0, jitter=60*30)
    scheduler.add_job(tweet, trigger=ct, args=(corpus_data,))

    print("Starting scheduler!")

    scheduler.start()
    
