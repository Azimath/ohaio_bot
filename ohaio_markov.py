import random

#https://towardsdatascience.com/simulating-text-with-markov-chains-in-python-1a27e6d13fc6

def load_corpus(filepath):
    text = open(filepath, encoding='utf8').read()

    corpus = text.split()

    def make_pairs(corpus):
        for i in range(len(corpus)-1):
            yield (corpus[i], corpus[i+1])

    def make_trios(corpus):
        for i in range(len(corpus)-2):
            yield (corpus[i], corpus[i+1], corpus[i+2])
            
    pairs = make_pairs(corpus)
    trios = make_trios(corpus)

    word_dict_one = {}
    word_dict_two = {}

    for word_1, word_2 in pairs:
        word_1 = word_1.lower()
        if word_1 in word_dict_one.keys():
            word_dict_one[word_1].append(word_2)
        else:
            word_dict_one[word_1] = [word_2]

    for word_1, word_2, word_3 in trios:
        word_1 = word_1.lower()
        word_2 = word_2.lower()
        if (word_1, word_2) in word_dict_two.keys():
            word_dict_two[(word_1, word_2)].append(word_3)
        else:
            word_dict_two[(word_1, word_2)] = [word_3]

    first_words = [w for w in list(word_dict_two) if w[0].lower().startswith("o") or w[0].lower().startswith("g")]
    random_word = [w for w in list(word_dict_one)]

    return (first_words, random_word, word_dict_one, word_dict_two)

def generate_tweet(chain_data):
    first_words, random_word, word_dict_one, word_dict_two = chain_data
    chain = list(random.choice(first_words))

    tweetText = ""
    while len(tweetText) < 280 and not "<|endoftext|>" in tweetText:
        lastOne = chain[-1].lower()
        lastTwo = chain[-2].lower()
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

        tweetText = ' '.join(chain)

    tweetText = tweetText.replace("<|endoftext|>", '')
    tweetText = tweetText[0:279]

    return tweetText


if __name__ == "__main__":
    chain_data = load_corpus('morning_dataset.txt')

    for i in range(100):
        print(generate_tweet(chain_data))
