CREATE TABLE users (id SERIAL PRIMARY KEY, email VARCHAR(100), username VARCHAR(100), password VARCHAR(500), created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP);
CREATE TABLE blogs (id SERIAL PRIMARY KEY, user_id INTEGER, text text, created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP);
CREATE TABLE stream_phrases(id SERIAL PRIMARY KEY, phrase VARCHAR(500), user_id INTEGER, created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP);

CREATE TABLE tracking(id SERIAL PRIMARY KEY, phrase_id INTEGER, created_date TIMESTAMP);

--query to get number of times a phrase is tweeted in a minute
WITH sum_of_minutes AS (SELECT COUNT(created_date) as number_of_times, MAX(created_date) as date, phrase_id FROM tracking
    GROUP BY phrase_id, created_date)
	select number_of_times, date, phrase, phrase_id FROM sum_of_minutes JOIN stream_phrases ON stream_phrases.id = sum_of_minutes.phrase_id;

-- query to get average for each phrase
WITH sum_of_minutes AS (SELECT COUNT(created_date) as number_of_times, MAX(created_date) as date, phrase_id FROM tracking
    GROUP BY phrase_id, created_date)

SELECT SUM(number_of_times) AS number_of_tweets, COUNT(phrase_id) as number_of_entries, MAX(phrase) as phrase FROM sum_of_minutes 
JOIN stream_phrases ON stream_phrases.id = sum_of_minutes.phrase_id
GROUP BY phrase;

