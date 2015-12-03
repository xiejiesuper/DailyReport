# -*- coding: utf-8 -*-
from flask import Blueprint, render_template, request
import sys
import json
sys.path.append('..')
reload(sys)
sys.setdefaultencoding('utf-8')

from ..extend import db
from ..models import User, Team, Roles
from ..decorators import check_cookie
from config import Config

setting = Blueprint('setting', __name__)


def response(code, message, data=None):
    info = {'code': code, 'message': message, 'data': data}
    return json.dumps(info, ensure_ascii=False)


@setting.route('/')
@check_cookie
def index():
    uid = request.uid
    current_user = User.query.get(uid)
    user_team_id = current_user.team
    team = Team.query.all()
    teams, user_group, team_names = {}, [], []
    for i in team:
        team_names.append([i.id, i.name])
        teams[i.id] = {'team': i.name, 'member': []}
    user = User.query.filter(User.account != Config.ADMIN, User.id != uid).all()
    for i in user:
        if i.team:
            teams[i.team]['member'].append((i.id, i.username))
    for i in teams:
        user_group.append(teams[i])
    SQL = 'select distinct  leader from roles where member=%s' % uid
    leaders = [i.leader for i in db.engine.execute(SQL)]
    return render_template('setting.html', user_group=user_group,
                           leaders=leaders, team_names=team_names,
                           account=request.user, user_team_id=user_team_id,
                           permission=request.permission, rn=request.rn)


@setting.route('/createRoles', methods=['POST'])
@check_cookie
def createRoles():
    uid = request.uid
    val = request.form.get('val')
    if val:
        role_exist = Roles.query.filter_by(member=uid).all()
        for i in role_exist:
            db.session.delete(i)
        if val != 'null':
            for i in val.split(','):
                role = Roles(uid, i)
                db.session.add(role)
        db.session.commit()
        return response('200', 'ok')
    else:
        return response('500', '提交参数错误')


@setting.route('/changeTeam', methods=['POST'])
@check_cookie
def changeTeam():
    uid = request.uid
    val = request.form.get('val')
    if val:
        user = User.query.get(uid)
        user.team = val
        db.session.commit()
        return response('200', 'ok')
    else:
        return response('500', '提交参数错误')


@setting.route('/changePassword', methods=['POST'])
@check_cookie
def changePassword():
    uid = request.uid
    old, new, confirm = request.form.get('old'), request.form.get('new'),\
        request.form.get('confirm')
    if old and new and confirm:
        if len(old) < 4 or len(new) < 4 or len(confirm) < 4:
            return response('2', '字符长度小于4')
        elif new != confirm:
            return response('2', '两次密码不一致')
        else:
            user = User.query.get(uid)
            if user and user.verify_password(old):
                user.password = new
                db.session.add(user)
                db.session.commit()
                return response('200', 'ok')
            else:
                return response('2', '密码错误')
    else:
        return response('2', '缺少参数')
