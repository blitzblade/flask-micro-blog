
import tweepy
import time
from db_script import TwitterDb, print_err

CONSUMER_KEY = ''
CONSUMER_SECRET = ''
ACCESS_TOKEN = ''
ACCESS_SECRET = ''

auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
auth.set_access_token(ACCESS_TOKEN, ACCESS_SECRET)

api = tweepy.API(auth,wait_on_rate_limit=True, wait_on_rate_limit_notify=True)
db = TwitterDb()
phrase_objects = db.get_phrases()

def extract_phrase(status, phrase_list):
    for i in phrase_list:
        selected_phrase = i.lower()
        if selected_phrase in status.lower():
            return selected_phrase
        


def in_list(status, _list):
    for i in _list:
        if i.lower() in status.lower():
            return True
    return False

class MyStreamListener(tweepy.StreamListener):
    def on_status(self, status):
        try:
            tweet_id=status.id
            tweet = status
            status = tweet.text
            print("status: ", status)

            if status.lower().startswith("rt @"):
                print("Retweets are ignored")
            else:
                print("dealing with phrase")
                
                phrases = [row["phrase"] for row in phrase_objects]
                #get phrase from twitter status
                selected_phrase = extract_phrase(status, phrases)
                selected_object = None
                #fetch phrase id from db
                for phrase_object in phrase_objects:
                    if phrase_object["phrase"].lower() == selected_phrase.lower():
                        selected_object = phrase_object
                        break
                db.create_occurrence(selected_object["id"])

                print("occurrence of phrase: ",selected_phrase, " created...")
                time.sleep(5)
        except Exception as e:
            print_err(e)
   
# Initialize Stream listener

if __name__=="__main__":
    streamer_obj = MyStreamListener()
    stream = tweepy.Stream(auth, streamer_obj)
    # Filter Twitter Streams to capture data by the keywords:
    phrases = [row["phrase"] for row in phrase_objects]
    stream.filter(track = phrases)