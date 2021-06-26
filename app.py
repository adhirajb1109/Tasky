from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy
app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+pymysql://root@localhost/flask-todolist"
db = SQLAlchemy(app)


class Database(db.Model):
    sno = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.String(500), nullable=False)

    def __repr__(self):
        return f"{self.sno} - {self.title}"


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        task = Database(title=title,
                        description=description)
        db.session.add(task)
        db.session.commit()
    tasks = Database.query.all()
    return render_template("index.html", tasks=tasks)


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
