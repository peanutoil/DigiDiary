from flask import *
from flask_bootstrap import Bootstrap
from flask_pymongo import PyMongo
from flask_moment import Moment
from datetime import datetime

fl = Flask("diary")
Bootstrap(fl)
moment = Moment(fl)
fl.config["SECRET_KEY"] = "ARTIFICALkey"
fl.config['MONGO_URI'] = "mongodb://localhost:27017/digital-diary-db"
mongo = PyMongo(fl)

@fl.route("/",methods=["GET","POST"])
def register():
    if request.method == "GET":
        return render_template("register.html")
    elif request.method == "POST":
        exist = mongo.db.loginInfo.find_one({"email": request.form['email']})
        if exist is None:
            doc={}
            for item in request.form:
                doc[item] = request.form[item]
            mongo.db.loginInfo.insert_one(doc)
            print("new acc created")
            flash("Account created successfully!")
            return redirect("/login")
        else:
            flash("This email has already been used!")
            return redirect("/")

@fl.route("/login",methods=["GET","POST"])
def login():
    if request.method == "GET":
        return render_template("login.html")
    elif request.method == "POST":
        doc = {"email": request.form["email"], "password": request.form["password"]}
        exist = mongo.db.loginInfo.find_one(doc)
        if exist is None:
            flash('The information you entered does not match our records. Please try again.')
            return redirect("/login")
        else:
            session['info'] = {'firstName': exist['firstName'], 'lastName': exist['lastName'],
                                    'email': exist['email'], 'time': datetime.utcnow()}
            return redirect("/user")

@fl.route("/user", methods=["GET","POST"])
def user():
    if len(session["info"]) == 0:
        flash("Error: You must log in before accessing this page.")
        return redirect("/login")
    if request.method == "GET":
        posts = mongo.db.diaryEntries.find({'user': session['info']['email']}).sort('time', -1)
        return render_template("home.html", posts = posts)
    elif request.method == "POST":
        entry = {"post": request.form["entry"], "user": session["info"]["email"], "time": datetime.utcnow()}
        mongo.db.diaryEntries.insert_one(entry)
        flash("Your entry has been saved successfully.")
        return redirect("/user")

@fl.route("/logout")
def out():
    session["info"].clear()
    flash("You have been logged out.")
    return redirect("/login")

fl.run(debug=True)
