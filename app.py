from flask import Flask, render_template, request, redirect
from flask_login.utils import login_required
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField
from wtforms.validators import DataRequired, length
from flask_login import UserMixin, login_user, LoginManager, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///tasky.db"
app.config["SECRET_KEY"] = "Secret Key"
db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class Tasky(db.Model):
    sno = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.String(500), nullable=False)

    def __repr__(self):
        return f"{self.sno} - {self.title}"


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))
    name = db.Column(db.String(1000))


class TaskForm(FlaskForm):
    title = StringField('Enter Task Title :', validators=[
                        DataRequired(), length(max=200)])
    description = StringField('Enter Task Description :', validators=[
                              DataRequired(), length(max=500)])
    submit = SubmitField('Submit')


class UserForm(FlaskForm):
    name = StringField('Enter Your Name :', validators=[
                       DataRequired(), length(max=1000)])
    password = PasswordField('Enter Your Password :', validators=[
                             DataRequired(), length(max=100)])
    email = StringField('Enter Your Email :', validators=[
        DataRequired(), length(max=100)])
    submit = SubmitField('Submit')


@app.route('/register', methods=["GET", "POST"])
def register():
    if request.method == "POST":

        if User.query.filter_by(email=request.form.get('email')).first():
            return redirect("/login")

        hash_and_salted_password = generate_password_hash(
            request.form.get('password'),
            method='pbkdf2:sha256',
            salt_length=8
        )
        new_user = User(
            email=request.form.get('email'),
            name=request.form.get('name'),
            password=hash_and_salted_password,
        )
        db.session.add(new_user)
        db.session.commit()
        login_user(new_user)
        return redirect("/")

    return render_template("register.html", form=UserForm())


@app.route('/login', methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get('email')
        password = request.form.get('password')

        user = User.query.filter_by(email=email).first()
        if not user:
            return redirect('/login')
        elif not check_password_hash(user.password, password):
            return redirect('/login')
        else:
            login_user(user)
            return redirect('/')

    return render_template("login.html", form=UserForm())


@app.route('/logout')
def logout():
    logout_user()
    return redirect("/")


@ app.route("/", methods=["GET", "POST"])
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
    return render_template("index.html", tasks=tasks, form=TaskForm())


@ app.route("/update/<int:sno>", methods=["GET", "POST"])
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
    return render_template("update.html", task=task, form=TaskForm())


@ app.route("/delete/<int:sno>")
def delete(sno):
    tasks = Tasky.query.filter_by(sno=sno).first()
    db.session.delete(tasks)
    db.session.commit()
    return redirect('/')


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")
