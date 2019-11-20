# Import the necessary package to process data in JSON format
try:
	import json
except ImportError:
	import simplejson as json

# Import the tweepy and pandas libraries
import tweepy
import pandas as pd
import matplotlib.pyplot as plt


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

    count = 2000

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

    # Create stacked bar chart of relative metion percentages
    f, ax = plt.subplots(1, figsize=(10,5))
    bar_width = .5
    bar_l = [i for i in range(len(df['Trump']))] 
    tick_pos = [i+(bar_width/8) for i in bar_l] 
    totals = [i+j+k for i,j,k in zip(df['Trump'], df['Biden'], df['Sanders'])]
    
    pre_rel = [i / j * 100 for  i,j in zip(df['Trump'], totals)]
    mid_rel = [i / j * 100 for  i,j in zip(df['Biden'], totals)]
    post_rel = [i / j * 100 for  i,j in zip(df['Sanders'], totals)]
    
    ax.bar(bar_l, pre_rel, label='Trump', alpha=0.9,
        color='#E0BBE4',width=bar_width, edgecolor='white')

    ax.bar(bar_l, mid_rel, bottom=pre_rel, label='Biden', 
           alpha=0.9, color='#957DAD', width=bar_width,edgecolor='white')

    ax.bar(bar_l, post_rel, bottom=[i+j for i,j in zip(pre_rel, mid_rel)], 
            label='Sanders', alpha=0.9, color='#FFDFD3', width=bar_width,edgecolor='white')

    # Label axes and plots
    plt.xticks(tick_pos, df['Account'])
    ax.set_ylabel("Percent Account Tweets About Person Relative to Others")
    ax.set_xlabel("")
    plt.legend(loc='upper left', bbox_to_anchor=(1,1), ncol=1)

    plt.title("Tweet Distribution between Trump, Biden, and Sanders over " + str(count) + " tweets")
    plt.xlim([min(tick_pos)-bar_width, max(tick_pos)+bar_width])
    plt.ylim(-10, 110)
    plt.setp(plt.gca().get_xticklabels(), rotation=45, horizontalalignment='right')
    plt.show()


if __name__ == "__main__":
    main()



