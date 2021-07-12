from flask import Flask, render_template, request, redirect, session
from flask_session import Session
from flask_sqlalchemy import SQLAlchemy
app = Flask(__name__)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///todolist.db"
db = SQLAlchemy(app)


class Database(db.Model):
    sno = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.String(500), nullable=False)

    def __repr__(self):
        return f"{self.sno} - {self.title}"


@app.route("/", methods=["GET", "POST"])
def index():
    if not session.get("name", "email"):
        return render_template("login.html")
    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        task = Database(title=title,
                        description=description)
        db.session.add(task)
        db.session.commit()
    tasks = Database.query.all()
    return render_template("index.html", tasks=tasks)


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        session["name"] = request.form.get("name")
        session["email"] = request.form.get("email")
        return redirect("/")
    return render_template("login.html")


@app.route("/logout")
def logout():
    session["name"] = None
    session["email"] = None
    return redirect("/")


@app.route("/update/<int:sno>", methods=["GET", "POST"])
def update(sno):
    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        task = Database.query.filter_by(sno=sno).first()
        task.title = title
        task.description = description
        db.session.add(task)
        db.session.commit()
        return redirect('/')
    task = Database.query.filter_by(sno=sno).first()
    return render_template("update.html", task=task)


@app.route("/delete/<int:sno>")
def delete(sno):
    tasks = Database.query.filter_by(sno=sno).first()
    db.session.delete(tasks)
    db.session.commit()
    return redirect('/')


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")
