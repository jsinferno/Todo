from flask import Flask, render_template, url_for, request, redirect, session, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import timedelta
import json


app = Flask(__name__)
app.secret_key = "djhdh"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///users.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.permanent_session_lifetime = timedelta(minutes = 10)


db = SQLAlchemy(app)

class todo(db.Model):
    _id = db.Column("id", db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    tasks = db.Column(db.String(100))

    def __init__(self, name, tasks):
        self.name = name
        self.tasks = tasks
        

@app.route("/view")
def view():
    return render_template("view.html", values = todo.query.all())


@app.route("/index", methods = ["GET","POST"])
def index():
    if "user" in session:
        user = session["user"]
        foundusr = todo.query.filter_by(name = user).first()
        
        if request.method == "POST":
            
            task = request.form.get("newtask")
            if not task:
                flash("Empty Task")
                return redirect("/index")

            if foundusr.tasks != "":
                
                tasks = json.loads(foundusr.tasks)
                tasks.insert(0,task)

            else: 
                tasks = [task]

            foundusr.tasks = json.dumps(tasks)
            db.session.commit()
            return render_template("index.html", tasks = zip(tasks,range(len(tasks))))

        if foundusr.tasks != "": return render_template("index.html", tasks = zip(json.loads(foundusr.tasks),range(len(json.loads(foundusr.tasks)))))
        return render_template("index.html")
       
        
    return redirect(url_for("login"))

@app.route("/", methods = ["GET","POST"])
def login():
    if request.method == "GET": 
        if "user" in session: return redirect(url_for("index"))
        return render_template("login.html")

    user = request.form.get("Username")
    session.permanent = True
    session["user"] = user

    foundusr = todo.query.filter_by(name = user).first()
    
    if not foundusr:
       
        usr = todo(user, "")
        
        db.session.add(usr)
        db.session.commit()


    flash(f"You have logged in succesfully {user}", "info")
    return redirect(url_for("index"))

@app.route("/logout")
def logout():
    if "user" in session: 
        user = session["user"]
        session.pop("user",None)

        flash(f"You have logged out succesfully {user}", "info")
    return redirect(url_for("login"))

@app.route("/delete", methods = ["POST"])
def delete():
    foundusr = todo.query.filter_by(name = session["user"]).first()
    tasks = json.loads(foundusr.tasks)
    index = int(request.form.get("index"))

    del tasks[index]
    foundusr.tasks = json.dumps(tasks)
    db.session.commit()
    return redirect("/index")










if __name__ == "__main__":
    db.create_all()
    app.run(debug = True)