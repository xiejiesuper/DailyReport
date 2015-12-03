# -*- coding: utf-8 -*-
from flask import Blueprint, render_template, redirect, flash, request, url_for, make_response
import time
import datetime
import sys
sys.path.append('..')
reload(sys)
sys.setdefaultencoding('utf-8')

from werkzeug.contrib.securecookie import SecureCookie
from ..forms import LoginForm
from ..models import User
from ..decorators import check_cookie
from config import Config
account = Blueprint('account', __name__)

SECRET_KEY = Config.SECRET_KEY
COOKIE_EXPIRES = Config.COOKIE_EXPIRES


@account.route('/login', methods=['GET', 'POST'])
def login():
    #import logging
    #logging.info('sgvsevr')
    form = LoginForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            user = User.query.filter_by(account=form.name.data).first()
            if user is not None and user.verify_password(form.password.data):
                resp = make_response(redirect(url_for('account.index', account=user.account)))
                cookie_value = SecureCookie({'user': form.name.data, 'rn': user.username,
                                            'uid': user.id, 'permission': user.permission,
                                             'timestamp': time.time()}, SECRET_KEY).serialize()
                # x = SecureCookie.unserialize(value, SECRET_KEY)
                resp.set_cookie('info', cookie_value, expires=time.time() + COOKIE_EXPIRES)
                # expires=COOKIE_EXPIRES
                return resp
            flash('1-Invalid username or password.')
            return render_template('login.html', form=form)
        flash('用户名或密码错误')
        return render_template('login.html', form=form)
    else:
        cookie_info = request.cookies.get('info')
        if cookie_info:
            info = SecureCookie.unserialize(cookie_info, SECRET_KEY)
            user, timesite = info.get('user'), info.get('timestamp')
            _user = User.query.filter_by(account=user).first()
            if _user:
                if (time.time() - timesite) < COOKIE_EXPIRES:
                    return redirect(url_for('account.index', account=user))
                return render_template('login.html', form=form)
        return render_template('login.html', form=form)


@account.route('/logout')
@check_cookie
def logout():
    flash('You have been logged out.')
    resp = make_response(redirect(url_for('account.login')))
    resp.set_cookie('info', '')
    return resp


@account.route('/<account>')
@check_cookie
def index(account):
    form = LoginForm()
    # return 'sdbvgsdf'
    info = request.cookies.get('info')
    if info:
        cookie_value = SecureCookie.unserialize(info, SECRET_KEY)
        if account == cookie_value.get('user'):
            today = datetime.datetime.now()
            year = today.isocalendar()[0]
            week_total = today.isocalendar()[1]
            uid = cookie_value.get('uid')
            permission, rn = cookie_value.get('permission'), cookie_value.get('rn')
            return render_template('index.html', year=year, week_total=week_total,
                                   uid=uid, account=account, permission=permission,
                                   rn=rn)
        else:
            render_template('login.html', form=form)
    return render_template('login.html', form=form)
