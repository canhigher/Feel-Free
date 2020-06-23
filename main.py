import tweepy
import praw
from urllib.request import urlopen
from bs4 import BeautifulSoup
from nltk.corpus import stopwords
from textblob import Word, TextBlob
import wordcloud
from wordcloud import WordCloud
from praw.models import MoreComments
import matplotlib.pyplot as plt


class StreamListener(tweepy.StreamListener):

    def on_status(self, status):
        if len(postsTwitter) >= 10:
            return False
        if not status.text.startswith('RT'):
            print(status.text)
            postsTwitter.insert(0, status.text)
            return postsTwitter

    def on_error(self, status_code):
        if status_code == 420:
            return False


def stream_twitter(api, news):
    streamListener = StreamListener()
    stream = tweepy.Stream(auth=api.auth, listener=streamListener, tweet_mode='extended')
    tags = news
    stream.filter(track=tags, languages=["en"])


def stream_reddit(reddit, array):
    all = reddit.subreddit("all")

    neg, pos = 0, 0
    for element in array:
        for subs in all.search(element):
            for comment in subs.comments:
                if len(postsReddit) >= 100:
                    continue
                if comment is None:
                    break
                if isinstance(comment, MoreComments):
                    continue
                postsReddit.insert(0, comment.body)
                polarity = TextBlob(comment.body).polarity
                print(comment.body)
                print(polarity)


def get_news():
    news = []
    url = "https://www.washingtonpost.com/"
    html = urlopen(url)
    soup = BeautifulSoup(html, "lxml")
    ulClass = soup.find_all("ul", class_="inline-list thin-style ad-none")
    for element in ulClass:
        wrappers = element.find_all("li")
        for i in range(1, len(wrappers)):
            text = wrappers[i].get_text()
            temp = list(text)
            if temp[0] and temp[-1] == "'":
                text = text[1:-1]
            news.append(text)
        return news


def normalization(array):
    sw = stopwords.words("english")
    tempArray = []

    for i in range(0, len(array)):
        comment = array[i]  # obtaining the words inside of the sentence
        sentence = ""  # used for storing words after processes
        for word in comment.split():  # each word
            if word in sw:  # if word is stopword, skip this word for process in below
                continue
            word = Word(word).lemmatize()  # lemmatize and stemming
            word = word.lower()  # capitalize
            word = "".join(char for char in word if
                           char.isalpha() or char == " " or char == "'")  # to joining. There is 3 different control occur because eliminating the possiblity of missing stopwords due to " ' " and space.
            sentence += word + " "

        tempArray.append(sentence)
        sentiment_score = TextBlob(sentence).sentiment
        print(sentiment_score)
    return tempArray


def wcloud(array):
    text = " ".join(i for i in array)
    wordcloud = WordCloud(max_words=100, background_color="white").generate(text)

    plt.figure()
    plt.imshow(wordcloud, interpolation="bilinear")
    plt.axis("off")
    plt.show()


if __name__ == '__main__':
    # credentialsTwitter
    CONSUMER_KEY = 'SFx0C6gQqWctsoo4tvtONK0N5'
    CONSUMER_SECRET = 'm0XkVDqbGSECSaue49h3yeEHgIZO0GCYXg0JWkPmRy6Ytha8qw'
    OAUTH_TOKEN = '1101027194946625536-kO4Lkdjy1SAgjT3xhrg7O5pkHCLEXT'
    OAUTH_TOKEN_SECRET = 'eYdYQSCxcxeptUxPEZkRpjRIr5CflCVsr3tvRUJiWDiJk'

    # credentialsReddit
    client_id = '1sDZmLsyUpDSsA'
    client_secret = '0fY88PAKSmZkX7dUgsaGSBgPA-k'
    username = 'canhigher'
    password = 'Burnside333.'
    user_agent = 'prawtutorial'

    auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
    auth.set_access_token(OAUTH_TOKEN, OAUTH_TOKEN_SECRET)
    api = tweepy.API(auth)

    reddit = praw.Reddit(client_id=client_id,
                         client_secret=client_secret,
                         username=username,
                         password=password,
                         user_agent=user_agent)

    news = get_news()
    print("News of the day:")
    for i in range(0, len(news)):
        print(news[i])

    postsReddit = []
    postsTwitter = []

    allPosts = postsTwitter+postsReddit

    stream_reddit(reddit, news)
    stream_twitter(api, news)

    parsedTwitter = normalization(postsTwitter)
    parsedReddit = normalization(postsReddit)
    allPosts = postsReddit + postsTwitter

    allParsed = parsedReddit+parsedTwitter
    #wcloud(allParsed)