# global imports
import os, codecs, re, string, random
from __future__ import division
from sklearn.feature_extraction.text import CountVectorizer
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
# iPython command for my system
%matplotlib qt

# raw corpora files available at the following link:
# https://d396qusza40orc.cloudfront.net/dsscapstone/dataset/Coursera-SwiftKey.zip

# read in all 3 files
f = codecs.open('Coursera-SwiftKey/final/en_US/en_US.twitter.txt', encoding='utf-8')
rawtweetlist = f.readlines()
f.close()

f = codecs.open('Coursera-SwiftKey/final/en_US/en_US.blogs.txt', encoding='utf-8')
rawblogslist = f.readlines()
f.close()

f = codecs.open('Coursera-SwiftKey/final/en_US/en_US.news.txt', encoding='utf-8')
rawnewslist = f.readlines()
f.close()

# combine as a single string for cleaning
rawlists = [rawtweetlist, rawblogslist, rawnewslist]
rawtext = '. '.join(['. '.join(rawlist) for rawlist in rawlists])

# clean the string (this version gets rid of numbers entirely with no replacement sentinel)
def clean_string(input_text):
    cleaned = input_text.lower()
    cleaned = re.sub('["#$%&\()*+,/:;<=>@[\\]^_`{|}~]', '', cleaned)
    cleaned = re.sub(' [^ai1234567890][ |\.]', ' ', cleaned)
    cleaned = re.sub('[1234567890]+\.[1234567890]+', '', cleaned)
    cleaned = re.sub('[1234567890]+', '', cleaned)
    cleaned = re.sub('\r\n', '. ', cleaned)
    cleaned = re.sub('\s+', ' ', cleaned)
    cleaned = re.sub('[!?]', '.', cleaned)
    cleaned = re.sub(' \.', '.', cleaned)
    cleaned = re.sub('\.+', '.', cleaned)

    return cleaned

# clean the raw corpora text
cleantext = clean_string(rawtext)
cleanlist = cleantext.split('. ')
del rawtext
del rawlists

# function to find all n-grams in a string
def find_all_ngrams(input_string, max_n = 3):
    vectorizer = CountVectorizer(ngram_range = (1, max_n), token_pattern = '[a-z]+[\'[a-z]*|[a-z]*]')
    analyzer = vectorizer.build_analyzer()
    return(analyzer(input_string))

# function to build ngrams one sentence at a time to preserve semantic integrity
def complicated_ngram_build(input_list, max_n = 3):
    ngram_dict = dict()
    for sentence in input_list:
        current_ngrams = find_all_ngrams(sentence, max_n)
        for ngram in current_ngrams:
            if ngram == []:
                pass
            elif ngram in ngram_dict:
                ngram_dict[ngram] += 1
            else:
                ngram_dict[ngram] = 1

    return ngram_dict

# build frequency dictionary; takes about 10 minutes
ngram_dict_semantic_ordering = complicated_ngram_build(cleanlist, 4)

# determine cutoff point for dropping low-frequency terms, trading off space complexity for accuracy
cutoff_test = pd.DataFrame(columns=['freq', 'percentage'])
for i in range(0,1000, 5):
    pct = len(dict_df[dict_df.frequency < i]) / len(dict_df)
    cutoff_test = cutoff_test.append({'freq': i, 'percentage': pct}, ignore_index=True)

plt.plot(test.freq, test.percentage, 'bo')  # 10 appears to be a good cutoff point

# build dataframe from our dictionary
dict_df = pd.DataFrame(ngram_dict_semantic_ordering.items(), columns=['ngrams', 'frequency'])
dict_df['n'] = [len(value.split()) for value in dict_df.ngrams.values]
# prune low frequency terms (using cutoff point determined above)
dict_df = dict_df[dict_df.frequency > 10]
# then get rid of all but the top few 1-grams to use as filler predictions
keeper_1grams = dict_df[dict_df.n == 1].sort('frequency', ascending=False)[:10]
dict_df = dict_df[dict_df.n > 1].append(keeper_1grams)
# now get leading key, trailing prediction
dict_df['leading'] = [" ".join(value.split()[:-1]) if len(value.split()) > 1 else value for value in dict_df.ngrams.values]
dict_df['trailing'] = [value.split()[-1] if len(value.split()) >1 else 'NA' for value in dict_df.ngrams.values]

# manually remove all the trailing singletons that aren't "a" or "i" that didn't get killed by regexes
mask  = [item in ['a', 'i'] if len(item) == 1 else True for item in dict_df.trailing]
dict_df = dict_df[mask]

# write out for use in R
dict_df.to_csv('lookup_outfile_CLEAN.csv')
