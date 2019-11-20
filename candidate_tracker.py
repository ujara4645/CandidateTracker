# Import the necessary package to process data in JSON format
try:
	import json
except ImportError:
	import simplejson as json

# Import the neccessary libraries
import tweepy
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np


# Variables that contains the user credentials to access Twitter API 
ACCESS_TOKEN = ''
ACCESS_SECRET = ''
CONSUMER_KEY = ''
CONSUMER_SECRET = ''


def generate_stats(screen_name, file_name, api, count):

    timeline = api.user_timeline(screen_name = screen_name, count = count, include_rts = False)

    # Collect json objects of each tweet
    collected_tweets = []
    for tweet in tweepy.Cursor(api.user_timeline, screen_name=screen_name, tweet_mode="extended").items(count):
        collected_tweets.append(tweet._json)

    # Access with 'text' for user_timeline and 'full_text' for Cursor
    # Create dataframe of just tweet texts
    df = pd.DataFrame(collected_tweets)
    df = df.astype({'full_text': str}) 
    df = df[['full_text']]
    df.to_csv(file_name)
    tweet_texts = df['full_text']

    # Count Trump, Biden, and Sanders mentions in each tweet
    trump_count = biden_count = sanders_count = 0

    for tweet in tweet_texts:
        if 'Trump' in tweet:
            trump_count += 1
        if 'Biden' in tweet:
            biden_count += 1
        if 'Sanders' in tweet:
            sanders_count += 1

    # Print mention count summary
    print("Of the past ",count," tweets by ",screen_name,", ",
        trump_count," mention Trump, ",biden_count," mention Biden, ",
        sanders_count," mention Sanders")

    return [trump_count, biden_count, sanders_count]



def main():
    # Setup tweepy to authenticate with Twitter credentials:
    auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
    auth.set_access_token(ACCESS_TOKEN, ACCESS_SECRET)

    # Create the api to connect to twitter with your credentials
    api = tweepy.API(auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True, compression=True)

    count = 3000

    # Create stat summary for each account
    CNN_stats = generate_stats('CNN', 'CNN_tweets.csv', api, count)
    CBS_stats = generate_stats('CBSNews', 'CBS_tweets.csv', api, count)
    WAPO_stats = generate_stats('WashingtonPost', 'CNN_tweets.csv', api, count)

    # Setup dataframe for plot
    trump_count = [CNN_stats[0], CBS_stats[0], WAPO_stats[0]]
    biden_count = [CNN_stats[1], CBS_stats[1], WAPO_stats[1]]
    sanders_count = [CNN_stats[2], CBS_stats[2], WAPO_stats[2]]

    accounts = ['CNN', 'CBS', 'WAPO']
    dict_stats = {'Account':accounts, 'Trump':trump_count, 'Biden':biden_count, 'Sanders':sanders_count}
    df = pd.DataFrame(dict_stats)

    # Create and label plot
    colors = ["#E0BBE4", "#957DAD","#FFDFD3"]
    df[['Trump', 'Biden', 'Sanders']].plot(kind = 'bar', stacked = True, color = colors, figsize = (10,7))
    plt.xticks(range(len(accounts)), accounts, size='small', rotation = 'horizontal')
    plt.title("Number of times a candidate was mentioned over " + str(count) + " tweets")
    plt.xlabel('News Account Source')
    plt.ylabel('Number of Tweets')
    plt.show()

if __name__ == "__main__":
    main()



