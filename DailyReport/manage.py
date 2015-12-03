# -*- coding: utf-8 -*-
from flask.ext.script import Manager, prompt_bool
import MySQLdb
from DailyReport import create_app
from DailyReport import db
from config import Config
from DailyReport.models import User, Team

app = create_app()
manager = Manager(app)


@manager.command
def createall():
    "Creates database tables"
    try:
        conn = MySQLdb.connect(host=Config.DB_HOST,
                               user=Config.DB_USER,
                               passwd=Config.DB_PASSWORD,
                               port=3306)
        cur = conn.cursor()
        cur.execute('create database if not exists %s' % Config.DB_NAME)
        conn.commit()
        cur.close()
        conn.close()
    except MySQLdb.Error, e:
        print "Mysql Error %d: %s" % (e.args[0], e.args[1])
    # create admin account
    db.create_all()
    admin = User(Config.ADMIN, Config.PASSWORD, Config.ADMIN, 1)
    team = Team('null')
    db.session.add(admin)
    db.session.add(team)
    db.session.commit()


@manager.command
def dropall():
    "Drops all database tables"
    if prompt_bool("Are you sure ? You will lose all your data !"):
        db.drop_all()


if __name__ == "__main__":
    manager.run()
