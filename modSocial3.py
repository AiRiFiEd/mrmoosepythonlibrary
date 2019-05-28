# -*- coding: utf-8 -*-
"""
Created on Mon May  6 01:20:37 2019

@author: yuanq
"""

import twitter
import json
import tweepy

import modGlobal3









WORLD_ID = {'WORLD':1,
            'EUROPE': 24865675,
            'UNITED_STATES':23424977,
            'SINGAPORE':1062617,
            'MALAYSIA':23424901}

def get_twitter(consumer_key = None,
                consumer_secret = None,
                access_token = None,
                access_secret = None):
    if consumer_key:
        str_consumer_key = consumer_key
    else:
        str_consumer_key = modGlobal3.CONSUMER_KEY
    
    if consumer_secret:
        str_consumer_secret = consumer_secret
    else:
        str_consumer_secret = modGlobal3.CONSUMER_SECRET
        
    if access_token:
        str_access_token = access_token
    else:
        str_access_token = modGlobal3.ACCESS_TOKEN
        
    if access_secret:
        str_access_secret = access_secret
    else:
        str_access_secret = modGlobal3.ACCESS_SECRET
        
#    auth = twitter.oauth.OAuth(token = str_access_token,
#                               token_secret = str_access_secret,
#                               consumer_key = str_consumer_key,
#                               consumer_secret = str_consumer_secret)    
#                
#    return twitter.Twitter(auth=auth)
        
    auth = tweepy.OAuthHandler(str_consumer_key, str_consumer_secret)
    auth.set_access_token(str_access_token, str_access_secret)
    return tweepy.API(auth)

def get_trends(twitter_api, lst_world_id, name_only=False):
    if name_only:
        return [set([trend['name'] 
                for trend in twitter_api.trends.place(_id=world_id)[0]['trends']])
                for world_id in lst_world_id]
    else:
        return [json.dumps(twitter_api.trends.place(_id=world_id), indent=1)
                for world_id in lst_world_id]
    

if __name__ == '__main__':
    twitter_api = get_twitter()
    
    for tweet in twitter_api.home_timeline():
        print(tweet.text)
#    trends = get_trends(twitter_api, [WORLD_ID['MALAYSIA'],WORLD_ID['SINGAPORE']],True)
#    print(set.intersection(*trends))
#    
#    q = '#dearmetenyearsago'
#    
#    # see http://dev.twitter.com/docs/api/1.1/get/search/tweets
#    # new https://developer.twitter.com/en/docs/tweets/search/api-reference/get-search-tweets
#    search_results = twitter_api.search.tweets(q=q)
#    statuses = search_results['statuses']
#    for __ in range(5):
#        print('Length of statuses', len(statuses))
#        try:
#            next_results = search_results['search_metadata']['next_result']
#        except KeyError as e: #No more results when next_results does not exist
#            break
#        
#        # create a dictionary from next_results, which has the following form:
#        # ?max_id = 313519052523986943&q=NCAA&include_entities=1
#        
#        kwargs = dict([kv.split('=') for kv in next_results[1:].split('&')])
#        
#        search_results = twitter_api.search.tweets(**kwargs)
#        statuses += search_results['statuses']
#        
#    # show one sample search result by slicing the list...
#    print(json.dumps(statuses[0], indent=1))
#    print(statuses[0]['text'])
