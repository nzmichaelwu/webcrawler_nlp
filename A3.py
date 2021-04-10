# imports
from twitter_crawler import twitter_scraper
import pandas as pd
import os
import re

from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from textblob import TextBlob


# set options
pd.set_option('mode.chained_assignment', None)
pd.options.display.max_colwidth = 200

# initialise variables
base_url = u'https://twitter.com/search?q='
cba = u'%40commbank'
westpac = u'%40westpac'
anz = u'%40anz'
nab = u'%40NAB'

urls = [base_url + cba, base_url + westpac, base_url + anz, base_url + nab]
scroll_down_num = 10

stop_words = set(stopwords.words('english'))

# the element we are obtaining from the webpage
post_element_xpath = '//div/div/article/div/div'

start_date = '2020-01-01'
end_date = '2021-01-01'

days_between = 2  # search every 2 days between the date range

# load tweets
if os.path.isfile('twitter_response.csv'):
    df_tweets = pd.read_csv('twitter_response.csv').reset_index(drop=True)
else:
    # run scraper to get tweets
    twitter_scraper(urls, scroll_down_num, post_element_xpath, start_date, end_date,
                    days_between, "twitter_response.csv")
    df_tweets = pd.read_csv('twitter_response.csv').reset_index(drop=True)

# drop unwanted columns first
df_tweets = df_tweets.drop(columns=['Unnamed: 0'])


# function to extract text from tweets
def extract_text(text):
    try:
        text_list = str.splitlines(text)  # split text by new line
        username = text_list[0]  # get username
        twitter_handle = ''.join(x for x in text_list[1:3] if '@' in x)  # get the twitter handle
        # date is always after the dot, so find the dot position in text list first
        dot_position = text_list[1:4].index('·')
        date = text_list[dot_position + 2]  # get date

        # check if a tweet is a reply to someone else
        if text_list[4] == "Replying to ":
            reply_to = True
            reply_to_handle = ''.join(x for x in text_list[5:7] if '@' in x) + ' ' + \
                              ''.join(x for x in text_list[6:8] if '@' in x)
            text = max(text_list[5:], key=len)
        else:
            reply_to = False
            reply_to_handle = ''
            # find the longest string in the selection of the list
            text = max(text_list[4:], key=len)

        return pd.Series([username, twitter_handle, date, reply_to, reply_to_handle, text])
    except:
        return pd.Series(['', '', '', '', '', ''])


df_temp = pd.DataFrame()

df_temp[['username', 'handle', 'date', 'reply_to', 'reply_to_handle', 'text']] = df_tweets['all_text'].apply(
    extract_text)


# function to pre-process tweets
def preprocess_tweet_text(tweet):
    # initialise lemmatizer
    wordnet_lemmatizer = WordNetLemmatizer()

    tweet.lower()

    # Remove urls from tweet
    tweet = re.sub(r"http\S+|www\S+|https\S+", '', tweet, flags=re.MULTILINE)
    # Remove user handle reference and # from tweet
    tweet = re.sub(r'\@\w+|\#', '', tweet)
    # Remove punctuations
    tweet = re.sub(r"[^\w\d'\s]+", '', tweet)
    # Remove stopwords and lemmatisation
    tweet_words = word_tokenize(tweet)
    tweet_words = [wordnet_lemmatizer.lemmatize(word) for word in tweet_words if word not in stop_words]

    tweet_lemmed = ' '.join(tweet_words)
    return tweet_lemmed

df_temp['tweet_cleaned'] = df_temp['text'].apply(preprocess_tweet_text)

""""
sid = SentimentIntensityAnalyzer()

sentiment = df_temp.apply(lambda r: sid.polarity_scores(r['tweet_cleaned']), axis=1)
df_sent = pd.DataFrame(list(sentiment))
df_final = df_temp.join(df_sent)
"""

def getTextSubjectivity(text):
    return TextBlob(text).sentiment.subjectivity

def getTextPolarity(text):
    return TextBlob(text).sentiment.polarity

def getTextAnalysis(a):
    if a < 0:
        return "Negative"
    elif a == 0:
        return "Neutral"
    else:
        return "Positive"

df_temp['subjectivity'] = df_temp['tweet_cleaned'].apply(getTextSubjectivity)
df_temp['polarity'] = df_temp['tweet_cleaned'].apply(getTextPolarity)

df_temp['score'] = df_temp['polarity'].apply(getTextAnalysis)