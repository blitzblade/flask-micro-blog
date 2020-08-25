import psycopg2
from psycopg2.extras import RealDictCursor
import sys

def print_err(err):
    print(str(err) + " on line " + str(sys.exc_info()[2].tb_lineno))

class TwitterDb:
    def __init__(self):
        pwd = "baw48KdcN6yRQ37yVEWjuehtx"
        host = "localhost"
        self.conn = psycopg2.connect("dbname=twitter_streamer_db user=postgres password={} host={}".format(pwd,host))
        self.cur = self.conn.cursor(cursor_factory=RealDictCursor)

    def get_phrases(self):
        self.cur.execute("SELECT * FROM stream_phrases;")
        data = self.cur.fetchall()
        return data

    def create_occurrence(self, phrase_id):
        self.cur.execute("INSERT INTO tracking (phrase_id, created_date) VALUES (%s, DATE_TRUNC('minute',CURRENT_TIMESTAMP))",[phrase_id])
        self.conn.commit()

    def get_tracked_phrases(self):
        query = """
        WITH sum_of_minutes AS (SELECT COUNT(created_date) as number_of_times, MAX(created_date) as date, phrase_id FROM tracking
        GROUP BY phrase_id, created_date)
	    select number_of_times, date, phrase, phrase_id FROM sum_of_minutes JOIN stream_phrases ON stream_phrases.id = sum_of_minutes.phrase_id;
        """
        self.cur.execute(query)
        return self.cur.fetchall()
    
    def get_average_phrase_per_minute(self):
        query = """
        WITH sum_of_minutes AS (SELECT COUNT(created_date) as number_of_times, MAX(created_date) as date, phrase_id FROM tracking
        GROUP BY phrase_id, created_date)

        SELECT SUM(number_of_times) AS number_of_tweets, COUNT(phrase_id) as number_of_entries, MAX(phrase) as phrase FROM sum_of_minutes 
        JOIN stream_phrases ON stream_phrases.id = sum_of_minutes.phrase_id
        GROUP BY phrase;
        """
        self.cur.execute(query)
        return self.cur.fetchall()


