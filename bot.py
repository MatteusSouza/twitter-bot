import asyncio
import logging
import auth
import timeformat
from tweetmodel import tweetModel
from time import sleep

global tweets_list
global retweets_list
global exclusion_list

tweets_list = []
retweets_list = []
exclusion_list = []

async def tweetsListObserver(func, observer_time_interval):
    logging.info("tweetsListObserver Started")
    while True:
        logging.info('tweetsListObserver Was Running')
        lenth = len(tweets_list)
        if lenth > 0:
            logging.info(''+'New tweets!') 
            logging.info(f"Number of tweets: {lenth}")
            await func()
        await asyncio.sleep(observer_time_interval)

def searchRecentTweets(client,term_to_search,results_num,start_time, connection_failure_retry_interval):
    """needs V2 OAuth 2.0
    referencia: https://developer.twitter.com/en/docs/twitter-api/data-dictionary/object-model/tweet
    start_time='YYYY-MM-DDTHH:mm:ssZ'"""

    logging.info("SearchRecentTweets Was Called")
    while True:
        try:
            response = client.search_recent_tweets(
                query=term_to_search,
                max_results=results_num,
                start_time = start_time,
                tweet_fields=[
                    "text",
                    "author_id", 
                    "conversation_id",
                    "created_at",
                    "in_reply_to_user_id",
                    "lang",
                    "possibly_sensitive",
                    "referenced_tweets",
                    "reply_settings",
                    "source"
                    ]
                )
            break
        except Exception as e:
            logging.error(f"Response error: {e}")
            logging.info("Connection fail. Please wait, trying again in 1 minute.")
            sleep(connection_failure_retry_interval)
    return response

async def addToList(client, term_to_search, results_num, start_time, search_time_interval, connection_failure_retry_interval):
    """Iterar response, adicionar cada tweet na lista"""
    logging.info("addToList Started")
    while True:
        logging.info("addToList Was Running") 
        
        response = searchRecentTweets(client, term_to_search, results_num, start_time, connection_failure_retry_interval)
        if(response.data != None):
            logging.info(f"response Tweets {len(response.data)}")
            
            if retweets_list == []:
                for item in response.data:
                    try:
                        tweet = tweetModel(item)
                        if tweet['authorId'] not in exclusion_list:
                            tweets_list.append(tweet)
                    except Exception as e:
                        logging.error(e)
                        
            else:
                for item in response.data:
                    tweet = tweetModel(item)
                    
                    is_in_retweet = False
                    for rt in retweets_list:
                        if tweet['id'] == rt['id']:
                            is_in_retweet = True
                            break
                    if is_in_retweet == False:
                        try:
                            if tweet['authorId'] not in exclusion_list:
                                tweets_list.append(tweet)
                        except Exception as e:
                            logging.error(e)
        
        logging.info(f"tweetsList {len(tweets_list)}")
        logging.info(f'retweets_list: {len(retweets_list)}')
        await asyncio.sleep(search_time_interval)

async def retweetTweetsList(api, retweet_time_interval):
    logging.info("retweetTweetsList Was Called")
    tweets_to_retweet = tweets_list.copy()
    tweets_list.clear()

    for index, tweet in enumerate(tweets_to_retweet):
        if retweets_list == []:
            try:
                api.retweet(tweet['id'])
                retweets_list.append(tweets_to_retweet[0])
                await asyncio.sleep(retweet_time_interval)
            except Exception as e:
                logging.error(f'Retweet fail: {e}')
                try:
                    logging.info(f"Trying to save {tweet['id']} as retweeted")
                    retweets_list.append(tweet)
                except Exception as e:
                    logging.error(f"Failed to save as retweeted {e}")
        else:
            is_in_retweet = False
            for retweet in retweets_list:
                if tweet['id'] == retweet['id']:
                    is_in_retweet = True
                    break
            if is_in_retweet == False:
                try:
                    api.retweet(tweet['id'])
                    retweets_list.append(tweet)
                    logging.info(f"{index} ... {retweet_time_interval} seconds interval ... Last Retweet: {tweet['id']}")
                    await asyncio.sleep(retweet_time_interval)
                except Exception as e:
                    logging.error(f'Retweet fail: {e}')
                    try:
                        logging.info(f"Trying to save {tweet['id']} as retweeted")
                        retweets_list.append(tweet)
                    except Exception as e:
                        logging.error(f"Failed to save as retweeted {e}")       
    
    logging.info(f"tweetsList {len(tweets_list)}")
    logging.info(f'tweets_to_retweet: {len(tweets_to_retweet)}')
    logging.info(f'retweets_list: {len(retweets_list)}')           

async def clearRetweetsList(hour):
    logging.info("clearRetweetsList Called")
    while True:
        await asyncio.sleep(60*60)
        logging.info("clear was running")
        hh = timeformat.now().hour
        mm = timeformat.now().minute
        if hh == hour:
            retweets_list.clear()
            logging.info("retweet List was cleared")

async def coroutine_tasks(api, retweet_time_interval, observer_time_interval, client, term_to_search, results_num, start_time, search_time_interval, connection_failure_retry_interval, clearRetweetsListHour):
    tasks = []
    tasks.append(asyncio.create_task( tweetsListObserver(lambda: retweetTweetsList(api, retweet_time_interval), observer_time_interval) ))
    tasks.append(asyncio.create_task(addToList(client, term_to_search, results_num, start_time, search_time_interval, connection_failure_retry_interval)))
    tasks.append(asyncio.create_task( clearRetweetsList(clearRetweetsListHour) ))
    
    await asyncio.gather(*tasks)

def logConfig():
    logging.basicConfig(
        level=logging.INFO, #INFO, WARNING
        format="%(asctime)s [%(levelname)s] %(message)s",
        handlers=[
            logging.FileHandler("execution.log"),
            logging.StreamHandler()
            ]
    )

def getExclusionList(file):
    try:
        file = open(file) 
        lines = file.read().splitlines()
        file.close()
    except Exception as e:
        print(e)
        file.close() 
    
    for l in lines:
        exclusion_list.append(int(l))

def main():
    logConfig()
    getExclusionList('exclusionlist.txt') # https://tools.codeofaninja.com/find-twitter-id

    api = auth.api_v1_oauth1()
    client = auth.api_v2_oauth2()

    term_to_search = "#bolhadev"
    results_num = 100
    clearRetweetsListHour = 19
    start_time = timeformat.setTime(lastMinute=15)
    connection_failure_retry_interval = 60
    observer_time_interval = 10
    search_time_interval = 60
    retweet_time_interval = 18

    asyncio.run(
        coroutine_tasks(api, retweet_time_interval, observer_time_interval, client, term_to_search, results_num, start_time, search_time_interval, connection_failure_retry_interval, clearRetweetsListHour))

if __name__ == '__main__':
    main()