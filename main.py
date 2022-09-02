from flask import Flask, url_for, flash, redirect, render_template, request
from flask_wtf import FlaskForm
from wtforms import StringField, DateField,SubmitField, PasswordField
from wtforms.validators import DataRequired
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
import os
from flask_login import LoginManager, UserMixin, login_user, current_user, login_required
from datetime import datetime


app=Flask(__name__)
SECRET_KEY = os.urandom(32)
app.config['SECRET_KEY'] = SECRET_KEY
login_manager=LoginManager()
login_manager.init_app(app)
Bootstrap(app)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///task.db'
db=SQLAlchemy(app)

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
    return render_template('index.html')


@app.route('/show_task')
def show_task():
    tasks = db.session.query(Task).all()
    return render_template('show_task.html',tasks=tasks)

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
    return render_template('add_task.html',form=form)


@app.route('/delete-task/<int:task_id>', methods=['GET','POST'])
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
        if password==confirm_password:
            new_user=User(
                email=email,
                password=password
            )
            db.session.add(new_user)
            db.session.commit()
            flash('sign up successfully')
            print(email)
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
            if password==user.password:
                login_user(user)
            else:
                flash(f"incorrect password!")
                return redirect(url_for('login'))
        else:
            flash(f"The account doesnt exist, please sign up first.")
            return redirect(url_for('register'))
        return redirect(url_for('show_task'))
    return render_template('login.html',form=form)

if __name__ == '__main__':
    app.run(debug=True, port=8080)


