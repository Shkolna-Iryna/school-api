from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()  # echo=True виводить всі SQL запити

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False) 
    email = db.Column(db.String(150), nullable=False)
    password = db.Column(db.String, nullable=False)
    tasks = db.relationship("Task", backref='user', lazy='select')  # lazy='select'
    
    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)

class Subject(db.Model):
    __tablename__ = 'subjects'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(50), nullable=False)
    tasks = db.relationship('Task', backref='subject', lazy='select')  # lazy='select'

class Task(db.Model):
    __tablename__ = 'tasks'
    id = db.Column(db.Integer, primary_key=True)
    task = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    subject_id = db.Column(db.Integer, db.ForeignKey('subjects.id'), nullable=False)
    answers = db.relationship('Answer', backref='task', lazy='select')
    correct_answer_id = db.Column(db.Integer, db.ForeignKey('answers.id'), nullable=True, unique=True)
    answers = db.relationship('Answer', backref='task', lazy='select', foreign_keys='Answer.task_id')
    correct_answer = db.relationship('Answer', foreign_keys=[correct_answer_id], post_update=True)
   

class Answer(db.Model):
    __tablename__ = 'answers'
    id = db.Column(db.Integer, primary_key=True)
    answer = db.Column(db.Text)
    task_id = db.Column(db.Integer, db.ForeignKey('tasks.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    user = db.relationship('User', lazy='select')
