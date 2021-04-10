# imports
from twitter_crawler import twitter_scraper
import pandas as pd
import os

# initialise variables
base_url = u'https://twitter.com/search?q='
cba = u'%40commbank'
westpac = u'%40westpac'
anz = u'%40anz'
nab = u'%40NAB'

urls = [base_url + cba, base_url + westpac, base_url + anz, base_url + nab]

scroll_down_num = 10

# the element we are obtaining from the webpage
post_element_xpath = '//div/div/article/div/div'

start_date = '2020-01-01'
end_date = '2021-01-01'

days_between = 2  # search every 2 days between the date range

# load tweets
if os.path.isfile('twitter_response.csv'):
    df = pd.read_csv('twitter_response.csv').reset_index(drop=True)
else:
    # run scraper to get tweets
    twitter_scraper(urls, scroll_down_num, post_element_xpath, start_date, end_date,
                    days_between, "twitter_response.csv")
    df = pd.read_csv('twitter_response.csv').reset_index(drop=True)

# drop unwanted columns first
df = df.drop(columns=['Unnamed: 0'])


# function to extract text from tweets
def extract_text(text):
    try:
        text_list = str.splitlines(text)  # split text by new line
        username = text_list[0]  # get username
        twitter_handle = ''.join(x for x in text_list[1:3] if '@' in x)  # get the twitter handle
        # date is always after the dot, so find the dot position in text list first
        dot_position = text_list[1:4].index('.')
        date = text_list[dot_position + 2]  # get date

        # check if a tweet is a reply to someone else
        if text_list[4] == "Replying to ":
            reply_to = True
            reply_to_handle = text_list[5]
            text = text_list[6]
        else:
            reply_to = False
            reply_to_handle = ''
            # find the longest string in the selection of the list
            text = max(text_list[4:6], key=len)

        return pd.Series([username, twitter_handle, date, reply_to, reply_to_handle, text])
    except:
        return pd.Series(['', '', '', '', '', ''])

#df[['username', 'handle', 'date', 'reply_to', 'reply_to_handle', 'text']] = df['all_text'].apply(extract_text)
