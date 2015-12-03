# -*- coding: utf-8 -*-
import datetime
import time
from flask import Blueprint, render_template, request
import json
import sys
sys.path.append('..')
reload(sys)
sys.setdefaultencoding('utf-8')

from ..extend import db
from ..forms import TeamForm, UserForm, UserUpdateForm
from ..models import Team, User, Roles, DailyReport
from ..decorators import check_cookie
from ..utils import getDateOfWeek
from config import Config

admin = Blueprint('admin', __name__)


def response(code, message, data=None, op=None, **kwargs):
    info = {'code': code, 'message': message, 'data': data, 'op': op}
    info.update(kwargs)
    return json.dumps(info, ensure_ascii=False)


@admin.route('/main', methods=['GET'])
@check_cookie
def main():
    teamform = TeamForm()
    userform = UserForm()
    user = [i for i in User.query.filter(User.account != Config.ADMIN).all()]
    # userform.team.choices = [('3','ertrt')]
    return render_template('admin/admin.html', teamform=teamform, userform=userform,
                           user=user, account=request.user,
                           permission=request.permission, rn=request.rn)


@admin.route('/team')
@check_cookie
def team():
    teams = Team.query.order_by('id').all()
    data = []
    for i in teams[::-1]:
        data.append([i.id, i.name])
    return response(200, 'ok', data)


@admin.route('/user/<int:current_page>')
@check_cookie
def user(current_page):
    users_count = db.engine.execute('select count(id) as total from users').fetchone()
    count = users_count[0]
    per_page = 10
    temp = divmod(count, per_page)
    page_total = temp[0] if temp[1] == 0 else temp[0] + 1
    start = (current_page - 1) * per_page
    data, leaders = [], {}
    SQL = 'select member,username from roles,users where roles.leader=users.id'
    roles = db.engine.execute(SQL)
    for i in roles:
        if i.member in leaders:
            leaders[i.member].append(i.username)
        else:
            leaders[i.member] = []
            leaders[i.member].append(i.username)
    
    SQL1 = 'SELECT u.id,u.username,u.account,u.permission,t.name as teamname\
           from users u LEFT JOIN teams t ON u.team=t.id limit %s,%s' % (start, per_page)
    users = db.engine.execute(SQL1)
    index = per_page * (current_page - 1) + 1
    for i in users:
        data.append([i.id, i.username, i.account, i.permission,
                    i.teamname, leaders.get(i.id, []), index])
        index += 1
    return response(200, 'ok', data, pages=page_total)


@admin.route('/team/del/<int:team_id>')
@check_cookie
def team_del(team_id):
    team = Team.query.get(team_id)
    db.session.delete(team)
    db.session.commit()
    return response(200, 'ok')


@admin.route('/create_or_update_team', methods=['POST'])
@check_cookie
def create_or_update_team():
    form = TeamForm(request.form)
    if form.validate_on_submit():
        name = form.name.data
        id = form.id.data
        test_exist = Team.query.filter_by(name=name).first()
        if test_exist:
            return response(2, '该名称已存在')
        try:
            if id == '':
                team = Team(name)
                db.session.add(team)
                db.session.commit()
                return response(200, 'ok', op='create-team')
            else:
                team = Team.query.filter_by(id=id).first()
                team.name = name
                db.session.add(team)
                db.session.commit()
                return response(200, 'ok', op='update-team')
        except Exception as e:
            e = str(e)
            print e
            return response(500, e)
    else:
        return response(1, '输入不符要求')
    
    
@admin.route('/create_user', methods=['POST'])
@check_cookie
def create_user():
    form = UserForm(request.form)
    if form.validate_on_submit():
        test_exist = User.query.filter_by(account=form.account.data).first()
        if test_exist:
            return response(2, '登录账号已存在')
        user = User(form.name.data, form.password.data, form.account.data.strip(),
                    form.permission.data, form.team.data)
        db.session.add(user)
        db.session.commit()
        if form.leader.data:
            user = User.query.filter(User.account == form.account.data.strip()).first()
            for i in form.leader.data.split(','):
                role = Roles(user.id, i)
                db.session.add(role)
                db.session.commit()
        return response(200, 'ok', op='create-user')
    else:
        print form.errors
        return response(1, '输入不符要求')


@admin.route('/update_user', methods=['POST'])
@check_cookie
def update_user():
    form = UserUpdateForm(request.form)
    if form.validate_on_submit():
        user = User.query.get(form.id.data)
        if user.account != form.account.data.strip():
            test_exist = User.query.filter_by(account=form.account.data.strip()).first()
            if test_exist:
                return response(2, '登录账号已存在')
        user.username = form.name.data
        user.account = form.account.data.strip()
        user.team = form.team.data
        user.permission = form.permission.data
        db.session.add(user)
        db.session.commit()
        return response(200, 'ok', op='update-user')
    else:
        return response(1, '输入不符要求')
    
        
@admin.route('/user/del/<int:user_id>',)
@check_cookie
def delete_user(user_id):
    user = User.query.get(user_id)
    db.session.delete(user)
    db.session.commit()
    return response(200, 'ok')


@admin.route('/user/resetpassword/<int:user_id>',)
@check_cookie
def resetpasswordr(user_id):
    user = User.query.get(user_id)
    user.password = '123456'
    db.session.add(user)
    db.session.commit()
    return response(200, 'ok')
    
    
@admin.route('/user/changeLeader', methods=['POST'])
@check_cookie
def changeLeader():
    uid, val = request.form.get('uid'), request.form.get('val')
    if val and uid:
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

@admin.route('/daily_index')
@check_cookie
def daily_index():
    now = datetime.datetime.now().date()
    today = now.strftime("%Y-%m-%d")
    teams = [i for i in Team.query.all()][::-1]
    return render_template('admin/dailyreport_team.html', teams=teams, today=today,
                            permission=request.permission, account=request.user,
                            rn=request.rn)

@admin.route('/daily_date')
@check_cookie
def daily_date():
    today = datetime.datetime.now()
    year = today.isocalendar()[0]
    SQL = "select u.id,u.username,t.name from users u,teams t where u.team=t.id and u.username!='%s'"%(Config.ADMIN)
    data = [i for i in db.engine.execute(SQL)]
    infos = {}
    for i in data:
        if i.name not in infos:
            infos[i.name] = []
        infos[i.name].append([i.id, i.username])
    if infos:
        infos = infos.items()
    return render_template('admin/dailyreport_member.html',permission=request.permission,
                            account=request.user,rn=request.rn, year=year, infos=infos)

@admin.route('/daily')
@check_cookie
def daily():
    team, date = request.args.get('team'), request.args.get('date')
    if team and date:
        if team == 'all':
            SQL = 'select u.username,t.name as team,t.id,d.content from users u\
                    left join teams t\
                    on u.team=t.id\
                    left join dailyreport d\
                    on d.timestamp=%s and d.author=u.id\
                    where u.username!="%s" order by t.name'%(date, Config.ADMIN)
        else:
            SQL = 'select u.username,t.name as team,t.id,d.content from users u\
                    right join teams t\
                    on u.team=t.id and t.id=%s\
                    left join dailyreport d\
                    on d.timestamp=%s and d.author=u.id\
                    where u.username!="%s" order by t.name'%(team, date, Config.ADMIN)
        team_id = 1 if team=="all" else team
        team_exist = Team.query.get(team_id)
        if team_exist:
            flag = "所有人员" if team=="all" else team_exist.name
            data = [x for x in db.engine.execute(SQL)]
            if data:
                data = sorted(data, key=lambda x: x.username)
            infos, members = [], []
            for i in data:
                infos.append({'name': i.username, 'team': i.team, 'content': i.content})
                members.append(i.username)
            return response('200', 'ok', {"data": infos, 'flag': flag+"(%s)"%len(members), 'members': members})
        else:
            return response('400', 'the team does not exist')
    else:
        return "param error", 400

@admin.route('/getDailyReport')
@check_cookie
def getDailyReport():
    try:
        content_dic = {}
        user, year, index = int(request.args.get('uid')), int(request.args.get('year')),\
            int(request.args.get('index'))
        if user and year and index and index < 55:
            today = datetime.datetime.now().date()
            # today = datetime.datetime(2015,9,26)
            now = today.isocalendar()
            if year > now[0]:
                return response('5', '年份超出范围')
            elif year == now[0]:
                if now[1] < index:
                    return response('5', '周超出范围')
                elif now[1] == index:
                    info = []
                    dates = [today - datetime.timedelta(days=i) for i in range(now[2])]
                    dates_timestamp = [int(time.mktime(i.timetuple())) for i in dates]
                    content_exist = DailyReport.query.filter(DailyReport.author == user,
                                    DailyReport.timestamp.in_(dates_timestamp)).all()
                    for i in content_exist:
                        content_dic[i.timestamp] = {'content': i.content, 'id': i.id}
                    for i in dates[::-1]:
                        key = int(time.mktime(i.timetuple()))
                        value = content_dic.get(key, {})
                        info.append({
                            'id': value.get('id', ''),
                            'date': i.strftime("%Y-%m-%d"),
                            'content': value.get('content', ''),
                            'week': i.weekday() + 1
                        })
                    return response('200', "ok", info)
                else:
                    info = []
                    dates = getDateOfWeek(year, index)
                    dates_timestamp = [int(time.mktime(i.timetuple())) for i in dates]
                    content_exist = DailyReport.query.filter(DailyReport.author == user,
                                    DailyReport.timestamp.in_(dates_timestamp)).all()
                    for i in content_exist:
                        content_dic[i.timestamp] = {'content': i.content, 'id': i.id}
                    for i in dates:
                        key = int(time.mktime(i.timetuple()))
                        value = content_dic.get(key, {})
                        info.append({
                            'id': value.get('id', ''),
                            'date': i.strftime("%Y-%m-%d"),
                            'content': value.get('content', ''),
                            'week': i.weekday() + 1
                        })
                    return response('200', "ok", info)
            else:
                info = []
                dates = getDateOfWeek(year, index)
                dates_timestamp = [int(time.mktime(i.timetuple())) for i in dates]
                content_exist = DailyReport.query.filter(DailyReport.author == user,
                    DailyReport.timestamp.in_(dates_timestamp)).all()
                for i in content_exist:
                    content_dic[i.timestamp] = {'content': i.content, 'id': i.id}
                for i in dates:
                    key = int(time.mktime(i.timetuple()))
                    value = content_dic.get(key, {})
                    info.append({
                        'id': value.get('id', ''),
                        'date': i.strftime("%Y-%m-%d"),
                        'content': value.get('content', ''),
                        'week': i.weekday() + 1
                    })
                return response('200', "ok", info)
        else:
            return response('500', '提交参数错误')
    except Exception as e:
        print str(e)
        return response('500', str(e))     
