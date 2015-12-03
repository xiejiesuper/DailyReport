# -*- coding: utf-8 -*-
from werkzeug.security import generate_password_hash, check_password_hash
from extend import db


class Team (db.Model):
    __tablename__ = 'teams'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    user = db.relationship('User', backref='teams', lazy='dynamic')
    
    def __init__(self, name):
        self.name = name
        
    def __repr__(self):
        return '<Team %r>' % self.name
        
        
class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50))
    account = db.Column(db.String(64), unique=True, index=True)
    password_hash = db.Column(db.String(128), unique=False)
    permission = db.Column(db.Integer, default=2)      # 1:admin    2:user
    team = db.Column(db.Integer, db.ForeignKey('teams.id'))

    def __init__(self, username, password, account, permission=2, team=None):
        self.username = username
        self.password_hash = generate_password_hash(password)
        self.account = account
        self.permission = permission
        self.team = team

    def __repr__(self):
        return '<User %r>' % self.username
        
    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')
        
    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)
   
   
class DailyReport(db.Model):
    __tablename__ = 'dailyreport'
    id = db.Column(db.Integer, primary_key=True)
    author = db.Column(db.Integer, index=True)
    content = db.Column(db.String(3000))
    type = db.Column(db.Integer)  # 1：日报  2：周报
    Y = db.Column(db.Integer)
    M = db.Column(db.Integer)
    D = db.Column(db.Integer)
    timestamp = db.Column(db.Integer, index=True)
    author = db.Column(db.Integer, db.ForeignKey('users.id'))
    
    def __init__(self, author, content, Y, M, D, timestamp, type):
        self.author = author
        self.content = content
        self.Y = Y
        self.M = M
        self.D = D
        self.timestamp = timestamp
        self.type = type


class Roles(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    member = db.Column(db.Integer, index=True)
    leader = db.Column(db.Integer, index=True)
    member = db.Column(db.Integer, db.ForeignKey('users.id'))
    leader = db.Column(db.Integer, db.ForeignKey('users.id'))

    def __init__(self, member, leader):
        self.member = member
        self.leader = leader
