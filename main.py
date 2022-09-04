from flask import Flask, url_for, flash, redirect, render_template, request
from flask_wtf import FlaskForm
from wtforms import StringField, DateField,SubmitField, PasswordField
from wtforms.validators import DataRequired
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
import os
from flask_login import LoginManager, UserMixin, login_user, current_user, login_required, logout_user
from flask_bcrypt import Bcrypt
import psycopg2


app=Flask(__name__)
Bootstrap(app)

app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')
login_manager=LoginManager()
login_manager.init_app(app)
bcrypt=Bcrypt(app)

# connect to DB
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL1','sqlite:///task.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db=SQLAlchemy(app)


# create DB
class Task(db.Model):
    id=db.Column(db.Integer, primary_key=True)
    date = db.Column(db.String, nullable=False)
    task=db.Column(db.String(50), nullable=False)
    location=db.Column(db.String(500))

db.create_all()

class User(UserMixin, db.Model):
    id=db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(50), nullable=False,unique=True)
    password=db.Column(db.String(50), nullable=False)


db.create_all()


# form
class NewTaskForm(FlaskForm):
    date = StringField('Date',validators=[DataRequired()])
    task = StringField('Task',validators=[DataRequired()])
    location_or_link = StringField('Location',validators=[DataRequired()])
    submit=SubmitField('Submit')

class RegistrationForm(FlaskForm):
    email = StringField('Email',validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password=PasswordField('Confirm Password', validators=[DataRequired()])
    submit = SubmitField('Submit')

class LoginForm(FlaskForm):
    email = StringField('Email',validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Submit')

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@app.route('/')
def home():
    return render_template('index.html', current_user=current_user)


@app.route('/show_task')
def show_task():
    tasks = db.session.query(Task).all()
    return render_template('show_task.html',tasks=tasks, current_user=current_user)

@app.route('/add_task',methods=['GET','POST'])
def add_task():
    form = NewTaskForm()
    if form.validate_on_submit():
        date = form.date.data
        task = form.task.data
        location = form.location_or_link.data

        new_task=Task(
            date=date,
            task=task,
            location=location
        )
        db.session.add(new_task)
        db.session.commit()
        return redirect(url_for('home'))
    return render_template('add_task.html',form=form, current_user=current_user)


@app.route('/delete-task/<int:task_id>', methods=['GET','POST'])
@login_required
def delete_task(task_id):
    task=Task.query.get(task_id)
    db.session.delete(task)
    db.session.commit()
    flash('Task deleted')
    return redirect(url_for('show_task'))

@app.route('/register',methods=['GET','POST'])
def register():
    form=RegistrationForm()
    if form.validate_on_submit():
        email=form.email.data
        password=form.password.data
        confirm_password=form.password.data
        user=User.query.filter_by(email=email).first()
        if not user:
            if password==confirm_password:
                hashed_pw=bcrypt.generate_password_hash(password,10)
                new_user=User(
                    email=email,
                    password=hashed_pw
                )
                db.session.add(new_user)
                db.session.commit()
                flash('sign up successfully')
                login_user(new_user)
            else:
                flash('Two passwords do not match.')
        else:
            flash('The account exists.')
            return redirect(url_for('login'))
    return render_template('register.html', form=form)

@app.route('/login',methods=['GET','POST'])
def login():
    form=LoginForm()
    if form.validate_on_submit():
        email=form.email.data
        password=form.password.data
        user = User.query.filter_by(email=email).first()
        if user:
            if bcrypt.check_password_hash(user.password,password):
                login_user(user)
            else:
                flash(f"incorrect password!")
                return redirect(url_for('login', current_user=current_user))
        else:
            flash(f"The account doesnt exist, please sign up first.")
            return redirect(url_for('register'))
        return redirect(url_for('show_task',current_user=current_user))
    return render_template('login.html',form=form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True)


