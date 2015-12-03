# -*- coding: utf-8 -*-
import functools
import time
from flask import redirect, flash, request, url_for
from werkzeug.contrib.securecookie import SecureCookie
from config import Config

SECRET_KEY = Config.SECRET_KEY
COOKIE_EXPIRES = Config.COOKIE_EXPIRES


def check_cookie(func):
    "login required"
    @functools.wraps(func)
    def decorator(*args, **kwargs):
        cookie_info = request.cookies.get('info')
        if cookie_info:
            info = SecureCookie.unserialize(cookie_info, SECRET_KEY)
            user, uid, timesite = info.get('user'), \
                info.get('uid'), info.get('timestamp')
            permission, rn = info.get('permission'), info.get('rn')
            request.uid, request.user, request.permission = uid,\
                user, permission
            request.rn = rn
            if (time.time() - timesite) >= COOKIE_EXPIRES:
                flash('deco-1会话已过期，请重新登录')
                return redirect(url_for('account.login'))
        else:
            flash('deco-2会话已过期，请重新登录')
            return redirect(url_for('account.login'))
        return func(*args, **kwargs)
    return decorator

caches = {}


def cache(func):
    @functools.wraps(func)
    def __memorize(*args):
        key = ''.join([str(i) for i in list(args)])
        if key in caches:
            return caches[key]
        result = func(*args)
        caches[key] = result
        return result
    return __memorize
