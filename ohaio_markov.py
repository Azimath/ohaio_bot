import random
import emoji

#https://towardsdatascience.com/simulating-text-with-markov-chains-in-python-1a27e6d13fc6

def is_emojiblock(text):
    if len(text) <= 1:
        return False
        
    for character in text:
        if character not in emoji.UNICODE_EMOJI_ENGLISH:
            return False
    return True

def make_pairs(corpus):
    for i in range(len(corpus)-1):
        yield (corpus[i], corpus[i+1])

def make_trios(corpus):
    for i in range(len(corpus)-2):
        yield (corpus[i], corpus[i+1], corpus[i+2])

def mod_key(key):
    if is_emojiblock(key):
        return "<|emojiblock|>"
    else:
        return key.lower()

def load_corpus(filepath):
    text = open(filepath, encoding='utf8').read()

    corpus = text.split()

    emojiCorpus = []
    for i, t in enumerate(corpus):
        if is_emojiblock(t):
            corpus[i] = "<|emojiblock|>"
            emojiCorpus.append(t)

    emojiCorpus = '\n'.join(emojiCorpus)
    
    pairs = make_pairs(corpus)
    trios = make_trios(corpus)
    emojiPairs = make_pairs(emojiCorpus)

    word_dict_one = {}
    word_dict_two = {}
    emoji_dict_one = {}

    for word_1, word_2 in pairs:
        word_1 = mod_key(word_1)
        if word_1 in word_dict_one.keys():
            word_dict_one[word_1].append(word_2)
        else:
            word_dict_one[word_1] = [word_2]

    for word_1, word_2, word_3 in trios:
        word_1 = mod_key(word_1)
        word_2 = mod_key(word_2)
        if (word_1, word_2) in word_dict_two.keys():
            word_dict_two[(word_1, word_2)].append(word_3)
        else:
            word_dict_two[(word_1, word_2)] = [word_3]

    for emoji_1, emoji_2 in emojiPairs:
        if emoji_1 in emoji_dict_one.keys():
            emoji_dict_one[emoji_1].append(emoji_2)
        else:
            emoji_dict_one[emoji_1] = [emoji_2]

    first_words = [w for w in list(word_dict_two) if w[0].lower().startswith("o") or w[0].lower().startswith("g")]
    random_word = [w for w in list(word_dict_one)]

    return (first_words, random_word, word_dict_one, word_dict_two, emoji_dict_one)

def generate_emojiblock(emoji_dict):
    emojiBlock = list(random.choice(emoji_dict['\n']))
    while len(emojiBlock) < 6:
        next = random.choice(emoji_dict[emojiBlock[-1]])
        if next != '\n':
            emojiBlock.append(next)
        else:
            break
    return ''.join(emojiBlock)

def generate_tweet(chain_data):
    first_words, random_word, word_dict_one, word_dict_two, emoji_dict_one = chain_data
    chain = list(random.choice(first_words))

    tweetText = ""
    while len(tweetText) < 280 and not "<|endoftext|>" in tweetText:
        lastOne = mod_key(chain[-1])
        lastTwo = mod_key(chain[-2])
        if len(lastOne) <= 3 and (lastTwo, lastOne) in word_dict_two.keys():
            chain.append(random.choice(word_dict_two[(lastTwo, lastOne)]))
        else:
            chain.append(random.choice(word_dict_one[lastOne]))
        
        if chain[-1] == "<|endoftext|>" and len(chain) < 4:
            if len(lastOne) <= 3 and (lastTwo, lastOne) in word_dict_two.keys():
                if len(list(filter(lambda x: not "<|endoftext|>" in x, word_dict_two[(lastTwo, lastOne)]))) == 0:
                    chain[-1] = random.choice(random_word)
                else:
                    chain.pop()
            else:
                if len(list(filter(lambda x: not "<|endoftext|>" in x, word_dict_one[lastOne]))) == 0:
                    chain[-1] = random.choice(random_word)
                else:
                    chain.pop()

        if chain[-1] == "<|emojiblock|>":
            chain[-1] = generate_emojiblock(emoji_dict_one)
        if chain[-2] == "<|emojiblock|>":
            chain[-2] = generate_emojiblock(emoji_dict_one)
        
        tweetText = ' '.join(chain)

    tweetText = tweetText.replace("<|endoftext|>", '')
    tweetText = tweetText[0:279]

    return tweetText


if __name__ == "__main__":
    chain_data = load_corpus('morning_dataset.txt')

    for i in range(100):
        print(generate_tweet(chain_data))
