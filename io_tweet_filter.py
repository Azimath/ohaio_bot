import mmap
from tqdm import tqdm
import json
from datetime import datetime
import pytz

io_timezone = pytz.timezone("America/Toronto")

def get_num_lines(file_path):
    fp = open(file_path, "r+")
    buf = mmap.mmap(fp.fileno(), 0)
    lines = 0
    while buf.readline():
        lines += 1
    return lines

in_file_path = "maybe.txt"
out_file_path = "filtered_io_tweets.txt"
with open(in_file_path, "r") as infile, open(out_file_path, "w") as out_file:
    out_file.write("[")
    #for line in tqdm(infile, total=get_num_lines(in_file_path)):
    tweetsData = json.loads(infile.read())
    for tweetData in tweetsData:
        if not tweetData["content"].startswith("@") and not "hours" in tweetData["content"] and not "collab" in tweetData["content"]:
            tweetdatetime = datetime.strptime(tweetData["date"], '%Y-%m-%dT%H:%M:%S%z')
            tweetEST = tweetdatetime.astimezone(tz=io_timezone)
            if tweetEST.hour < 11 and tweetEST.hour > 5:
                out_file.write(json.dumps(tweetData)+",\n")
    out_file.write("]")