import os
db = "postgres://postgres:postgres@localhost/twitter_streamer_db"
os.environ["DATABASE_URL"] = db
