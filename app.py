from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import Form
from wtforms import StringField , SubmitField
from wtforms.validators import DataRequired , length
app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///tasky.db"
app.config["SECRET_KEY"] = "Secret Key"
db = SQLAlchemy(app)


class Tasky(db.Model):
    sno = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.String(500), nullable=False)

    def __repr__(self):
        return f"{self.sno} - {self.title}"


class TaskForm(Form):
    title = StringField('Enter Task Title :', validators=[DataRequired() , length(max=200)])
    description = StringField('Enter Task Description :', validators=[DataRequired() , length(max=500)])
    submit = SubmitField('Submit')

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == 'POST':
        form = TaskForm()
        if form.validate_on_submit():
          title = request.form['title']
          description = request.form['description']
          task = Tasky(title=title,
                        description=description)
          db.session.add(task)
          db.session.commit()
    tasks = Tasky.query.all()
    return render_template("index.html", tasks=tasks , form=TaskForm())

@app.route("/update/<int:sno>", methods=["GET", "POST"])
def update(sno):
    if request.method == 'POST':
        form = TaskForm()
        if form.validate_on_submit():
          title = request.form['title']
          description = request.form['description']
          task = Tasky.query.filter_by(sno=sno).first()
          task.title = title
          task.description = description
          db.session.add(task)
          db.session.commit()
        return redirect('/')
    task = Tasky.query.filter_by(sno=sno).first()
    return render_template("update.html", task=task , form=TaskForm())


@app.route("/delete/<int:sno>")
def delete(sno):
    tasks = Tasky.query.filter_by(sno=sno).first()
    db.session.delete(tasks)
    db.session.commit()
    return redirect('/')


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")
