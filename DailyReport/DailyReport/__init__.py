# -*- coding: utf-8 -*-
from flask import Flask, render_template
from flask_wtf.csrf import CsrfProtect
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
sys.path.append('..')
from views import account, admin, user, setting
from extend import db
import config

DEFAULT_MODULES = (
    (account.account, ""),
    (admin.admin, "/admin"),
    (user.user, "/user"),
    (setting.setting, "/setting"),
)

def create_app():
    "main"
    app = Flask(__name__)
    # config
    app.config.from_object(config.Config)
    
    configure_extensions(app)
    configure_errorhandlers(app)
    configure_before_handlers(app)
    configure_template_filters(app)
    # register module
    
    configure_blueprint(app, DEFAULT_MODULES)
    return app


def configure_extensions(app):
    # configure extensions
    db.init_app(app)
    CsrfProtect(app)
   
    
def configure_errorhandlers(app):
    @app.errorhandler(404)
    def not_found(error):
        return render_template('404.html'), 404
 
 
def configure_before_handlers(app):
    pass
    
    
def configure_template_filters(app):
    @app.template_filter('members')
    def members_filter(s):
        s_new = ' , '.join([i[0] for i in s])
        return s_new
        
    @app.template_filter('week')
    def week_filter(s):
        a = [u'周一', u'周二', u'周三', u'周四', u'周五', u'周六', u'周日']
        return a[s]
    
    
def configure_blueprint(app, modules):
    for module, url_prefix in modules:
        # print module, url_prefix
        app.register_blueprint(module, url_prefix=url_prefix)
