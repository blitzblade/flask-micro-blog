import psycopg2
from psycopg2.extras import RealDictCursor
import sys

def print_err(err):
    print(str(err) + " on line " + str(sys.exc_info()[2].tb_lineno))

class TwitterDb:
    def __init__(self):
        pwd = "postgres"
        # pwd = "baw48KdcN6yRQ37yVEWjuehtx"
        host = "localhost"
        self.conn = psycopg2.connect("dbname=twitter_streamer_db user=postgres password={} host={}".format(pwd,host))
        self.cur = self.conn.cursor(cursor_factory=RealDictCursor)

    def get_cur(self):
        try:
            self.cur.execute("SELECT 1 FROM stream_phrases;")
            return self.cur
<<<<<<< HEAD
        except psycopg2.InterfaceError as ex:
            self.conn = psycopg2.connect("dbname=twitter_streamer_db user=postgres password={} host={}".format(pwd,host))
=======
        except as ex:
            self.conn = psycopg2.connect("dbname=twitter_streamer_db user=postgres password={} host={}".format(self.pwd,self.host))
            print_err(ex)
>>>>>>> 8cc291140f11af4bc485247f73812964b5903d3c
            return self.conn.cursor(cursor_factory=RealDictCursor)

    def get_phrases(self):
        self.cur = self.get_cur()
        self.cur.execute("SELECT * FROM stream_phrases;")
        data = self.cur.fetchall()
        return data

    def create_occurrence(self, phrase_id):
        self.cur = self.get_cur()
        self.cur.execute("INSERT INTO tracking (phrase_id, created_date) VALUES (%s, DATE_TRUNC('minute',CURRENT_TIMESTAMP))",[phrase_id])
        self.conn.commit()

    def get_tracked_phrases(self):
        query = """
        WITH sum_of_minutes AS (SELECT COUNT(created_date) as number_of_times, MAX(created_date) as date, phrase_id FROM tracking
        GROUP BY phrase_id, created_date)
	    select number_of_times, date, phrase, phrase_id FROM sum_of_minutes JOIN stream_phrases ON stream_phrases.id = sum_of_minutes.phrase_id;
        """
        self.cur = self.get_cur()
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
        self.cur = self.get_cur()
        self.cur.execute(query)
        return self.cur.fetchall()

    def get_chart_data_for_minutes(self):
        query = """
        SELECT COUNT(tracking.created_date) as number_of_times, MAX(tracking.created_date) as date, phrase FROM tracking JOIN 
						stream_phrases ON 
						tracking.phrase_id = stream_phrases.id WHERE tracking.created_date 
						BETWEEN CURRENT_TIMESTAMP - INTERVAL '30 minutes' AND CURRENT_TIMESTAMP
                        GROUP BY phrase, tracking.created_date ORDER BY tracking.created_date asc
        """
        self.cur = self.get_cur()
        self.cur.execute(query)
        return self.cur.fetchall()


