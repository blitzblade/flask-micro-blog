import os
import requests
import time
from flask import Flask, session,render_template,request,redirect,url_for,flash,make_response,jsonify
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from db_script import TwitterDb, print_err
import create_db_connection
import json

app = Flask(__name__)

if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)


engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))
twitter_db = TwitterDb()


@app.route("/")
def home():
    return render_template('home.html')

@app.route("/login")
def log_in():
    return render_template('login.html')

@app.route("/handle_data", methods=['POST'])
def handle_data():

    data = request.form
    email1 = data["email"]
    pwd = data["pass"]
    username = data["username"]
    
    if db.execute("SELECT * from users WHERE username= :u AND password= :p",{"u":username,"p":pwd}).rowcount == 1 :
        return render_template('already_hehe.html')
    else:
        db.execute("INSERT INTO users (email,username,password) VALUES (:e,:u,:p)",{"e":email1,"u":username,"p":pwd})
        db.commit()
        return render_template('login.html')     


@app.route("/after_loggin",methods=["GET","POST"])
def after_login():
    data = request.form
    u = data["username"]

    pwd = data["pwd"]
    
    result = db.execute("SELECT * from users WHERE username=:u AND password=:p",{"u":u,"p":pwd}).fetchall()
    for row in result:
        print("ROW: ", row)
        if(pwd==row.password):
                ts = time.gmtime()
                timestamp = time.strftime("%x", ts)
                mybool = db.execute("SELECT * FROM blogs WHERE user_id=:u AND created_date=:timestamp",{"u":row[0],"timestamp":timestamp}).rowcount > 0
                print(mybool)
                if(mybool):
                    display = False
                    resp = make_response(render_template('feed.html',u=u,display=display))  
                    resp.set_cookie('username',u) 
                    resp.set_cookie('user_id',str(row[0])) 
                    return resp

                else:        
                    display = True    
                    resp = make_response(render_template('feed.html',u=u,display=display))  
                    resp.set_cookie('username',u)  
                    resp.set_cookie('user_id',str(row[0])) 
                    return resp  
            
        else:
            message2 = True
            message = False
            return render_template('empty.html',message=message,message2=message2)

@app.route("/after_submit",methods=["POST"])
def after_submit():
    data = request.form
    blog_text = data["blog-text"]
    x = request.cookies.get('user_id') 
    
    ts = time.gmtime()
    timestamp = time.strftime("%x", ts)
    
    db.execute("INSERT INTO blogs (user_id,text,created_date) VALUES (:u,:t,:c)",{"u":x,"t":blog_text,"c":timestamp})
    db.commit()

    message = True
    message2 = False
        
    return render_template('empty.html',message=message,message2=message2)

@app.route("/feed")
def feed():
    result=db.execute("SELECT * from blogs").fetchall()   
    for row in result:
        print("User: ",row.user_id, "Blog:",row.text, "Created_date:",row.created_date)
    return render_template('posts.html',result=result)   


@app.route("/phrases", methods=['GET','POST'])
def phrases():
    if request.method == "POST":
        data = request.form
        phrase = data["phrase"]
        u_id = request.cookies.get('user_id')
        ts = time.gmtime()
        timestamp = time.strftime("%x", ts)

        db.execute("INSERT INTO stream_phrases (user_id,phrase,created_date) VALUES (:u,:p,:c)",{"u":u_id,"p":phrase,"c":timestamp})
        db.commit()
    result=db.execute("SELECT * from stream_phrases").fetchall()   
    for row in result:
        print("User: ",row.user_id, "Phrase:",row.phrase, "Created_date:",row.created_date)
    return render_template('phrases.html',result=result)  

@app.route("/phrase_occurrence")
def phrase_occurrence():
    data = twitter_db.get_tracked_phrases()
    return jsonify(data)

@app.route("/average_phrase_per_minute")
def average_phrase():
    data = twitter_db.get_average_phrase_per_minute()
    print("DATA: ",data)
    new_data = [ {"average_per_min": float(d["number_of_tweets"])/float(d["number_of_entries"]), "phrase": d["phrase"]} for d in data]
    print(new_data)
    return json.dumps(new_data)



@app.route("/home")
def home_after_login():
    u = request.cookies.get('username')
    u_id = request.cookies.get('user_id')
    ts = time.gmtime()
    timestamp = time.strftime("%x", ts)
                
    mybool = db.execute("SELECT * FROM blogs WHERE user_id=:u AND created_date=:timestamp",{"u":u_id,"timestamp":timestamp}).rowcount > 0
    print(mybool)
    if(mybool):
        display = False
        return render_template('feed.html',display=display)

    else:        
        display = True    
        return render_template('feed.html',display=display) 


if __name__ == "__main__":
    app.run()