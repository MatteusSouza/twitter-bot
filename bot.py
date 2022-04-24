import asyncio
import logging
import auth
import timeformat

global tweets_list
global retweets_list

tweets_list = []
retweets_list = []

async def tweetsListObserver(func, observer_time_interval):
    logging.info("tweetsListObserver Started")
    while True:
        logging.info('tweetsListObserver Was Running')
        lenth = len(tweets_list)
        if lenth > 0:
            logging.info(''+'Novos tweets!') 
            logging.info(f"Number of tweets: {lenth}")
            await func()
        await asyncio.sleep(observer_time_interval)

def searchRecentTweets(client,term_to_search,results_num,start_time):
    """needs V2 OAuth 2.0
    referencia: https://developer.twitter.com/en/docs/twitter-api/data-dictionary/object-model/tweet
    start_time='YYYY-MM-DDTHH:mm:ssZ'"""

    logging.info("SearchRecentTweets Was Called")
    
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
    except Exception as e:
        logging.error("Response error: {e}")
    return response

async def addToList(client, term_to_search, results_num, start_time, search_time_interval):
    """Iterar response, adicionar cada tweet na lista"""
    logging.info("addToList Started")
    while True:
        logging.info("addToList Was Running") 
        response = searchRecentTweets(client, term_to_search, results_num, start_time)
        if(response.data != None):
            logging.info(f"response Tweets {len(response.data)}")
            for item in response.data:
                tweet = {
                    "id": item.id,
                    "text": item.text,
                    "authorId": item.author_id,
                    "conversationId": item.conversation_id,
                    "createdAt": item.created_at,
                    "inReplyToUserId": item.in_reply_to_user_id,
                    "lang": item.lang,
                    "possiblySensitive": item.possibly_sensitive,
                    "referencedTweets": item.referenced_tweets,
                    "source": item.source
                }
                try:
                    tweets_list.append(tweet)
                except Exception as e:
                    logging.error(f"Exception when append a tweet in the tweets_list: {e}")
        
        logging.info(f"tweetsList {len(tweets_list)}")
        logging.info(f'retweets_list: {len(retweets_list)}')
        await asyncio.sleep(search_time_interval)

async def retweetTweetsList(api, retweet_time_interval):
    logging.info("retweetTweetsList Was Called")
    tweets_to_retweet = tweets_list.copy()
    tweets_list.clear()
    
    if retweets_list == []:
        try:
            api.retweet(tweets_to_retweet[0]['id'])
            retweets_list.append(tweets_to_retweet[0])
            logging.info(f"tweet 0 {retweet_time_interval} seconds interval ... Last Retweet: {tweets_to_retweet[0]['id']}")
            await asyncio.sleep(retweet_time_interval)
        except Exception as e:
            logging.error(e)
    
    for index, tt in enumerate(tweets_to_retweet):
        is_in_retweet = False
        for rt in retweets_list:
            if tt['id'] == rt['id']:
                is_in_retweet = True
                break
        if is_in_retweet == False:
            try:
                api.retweet(tweets_to_retweet['id'])
                retweets_list.append(tt)
                logging.info(f"{index} ... {retweet_time_interval} seconds interval ... Last Retweet: {tt['id']}")
                await asyncio.sleep(retweet_time_interval)
            except Exception as e:
                logging.error(e)
    
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

async def coroutine_tasks(api, retweet_time_interval, client, term_to_search, results_num, start_time, search_time_interval, clearRetweetsListHour, observer_time_interval):
    tasks = []
    tasks.append(asyncio.create_task( tweetsListObserver(lambda: retweetTweetsList(api, retweet_time_interval), observer_time_interval) ))
    tasks.append(asyncio.create_task(addToList(client, term_to_search, results_num, start_time, search_time_interval)))
    tasks.append(asyncio.create_task( clearRetweetsList(clearRetweetsListHour) ))
    
    await asyncio.gather(*tasks)

def logConfig():
    logging.basicConfig(
        level=logging.WARNING,
        format="%(asctime)s [%(levelname)s] %(message)s",
        handlers=[
            logging.FileHandler("execution.log"),
            logging.StreamHandler()
            ]
    )

def main():
    logConfig()
    api = auth.api_v1_oauth1()
    client = auth.api_v2_oauth2()
    term_to_search = "@vagasDevRJ"
    results_num = 100
    clearRetweetsListHour = 3
    start_time = timeformat.setTime(lastMinute=15)
    observer_time_interval = 60
    search_time_interval = 60*5
    retweet_time_interval = 18

    asyncio.run(
        coroutine_tasks(api, retweet_time_interval, client, term_to_search, results_num, start_time, search_time_interval, clearRetweetsListHour, observer_time_interval))

if __name__ == '__main__':
    main()