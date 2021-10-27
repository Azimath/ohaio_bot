import tweepy
import pytz
import random

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

def tweet(first_words, word_dict):
    import tokens
    auth = tweepy.OAuthHandler(tokens.CONSUMER_KEY, tokens.CONSUMER_SECRET)
    auth.set_access_token(tokens.ACCESS_TOKEN, tokens.ACCESS_SECRET)

    api = tweepy.API(auth)

    chain = list(random.choice(first_words))

    tweetText = ""
    while len(tweetText) < 280 and not "<|endoftext|>" in tweetText:
        chain.append(random.choice(word_dict[(chain[-2], chain[-1])]))
        tweetText = ' '.join(chain)

    tweetText = tweetText.replace("<|endoftext|>", '')
    tweetText = tweetText[0:279]

    print("Tweeting {}\n".format(tweetText))

    api.update_status(tweetText)

if __name__ == "__main__":
    print("OHAAAAAIIIIOOOOO!")
    #https://towardsdatascience.com/simulating-text-with-markov-chains-in-python-1a27e6d13fc6
    text = open(corpus_filename, encoding='utf8').read()

    corpus = text.split()

    def make_pairs(corpus):
        for i in range(len(corpus)-1):
            yield (corpus[i], corpus[i+1])
            
    def make_trios(corpus):
        for i in range(len(corpus)-2):
            yield (corpus[i], corpus[i+1], corpus[i+2])
            
    #pairs = make_pairs(corpus)
    trios = make_trios(corpus)

    word_dict = {}

    for word_1, word_2, word_3 in trios:
        if (word_1, word_2) in word_dict.keys():
            word_dict[(word_1, word_2)].append(word_3)
        else:
            word_dict[(word_1, word_2)] = [word_3]

    first_words = [w for w in list(word_dict) if w[0].startswith("O") or w[0].lower().startswith("good") or w[0].startswith("G")]

    ct = CronTrigger(hour=8, minute=0, second=0, jitter=60*30)
    scheduler.add_job(tweet, trigger=ct, args=(first_words, word_dict))

    print("Starting scheduler!")

    scheduler.start()
    