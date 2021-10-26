import tweepy
import pytz
import numpy as np

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

def tweet(corpus, word_dict):
    import tokens
    auth = tweepy.OAuthHandler(tokens.CONSUMER_KEY, tokens.CONSUMER_SECRET)
    auth.set_access_token(tokens.ACCESS_TOKEN, tokens.ACCESS_SECRET)

    api = tweepy.API(auth)

    first_word = np.random.choice(corpus)

    while first_word.islower():
        first_word = np.random.choice(corpus)

    chain = [first_word]

    tweetText = ""
    while len(tweetText) < 280 and not "<|endoftext|>" in tweetText:
        chain.append(np.random.choice(word_dict[chain[-1]]))
        tweetText = ' '.join(chain)

    print("Tweeting {}\n".format(tweetText))

    tweetText = tweetText.replace("<|endoftext|>", '')

    api.update_status(tweetText)

if __name__ == "__main__":
    #https://towardsdatascience.com/simulating-text-with-markov-chains-in-python-1a27e6d13fc6
    text = open(corpus_filename, encoding='utf8').read()

    corpus = text.split()

    def make_pairs(corpus):
        for i in range(len(corpus)-1):
            yield (corpus[i], corpus[i+1])
            
    pairs = make_pairs(corpus)

    word_dict = {}

    for word_1, word_2 in pairs:
        if word_1 in word_dict.keys():
            word_dict[word_1].append(word_2)
        else:
            word_dict[word_1] = [word_2]

    ct = CronTrigger(hour=8, minute=0, second=0, jitter=60*60*1)
    scheduler.add_job(tweet, trigger=ct, args=(corpus, word_dict))

    scheduler.start()
    