from flask.ext.sqlalchemy import SQLAlchemy
# from flask.ext.login import LoginManager
# from flask.ext.cache import Cache


__all__ = ['db']

db = SQLAlchemy()
'''
login_manager = LoginManager()
login_manager.session_protection = 'basic'     #None  'basic'  'strong'
login_manager.login_view = 'account.login'
'''
# cache = Cache()
