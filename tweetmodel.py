def tweetModel(response_data):
    item = response_data
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
    return tweet