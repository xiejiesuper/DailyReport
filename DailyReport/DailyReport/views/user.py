# -*- coding: utf-8 -*-
from flask import Blueprint, render_template, request
import sys
import json
import datetime
import time
sys.path.append('..')
reload(sys)
sys.setdefaultencoding('utf-8')

from ..extend import db
from ..models import DailyReport, Team
from ..decorators import check_cookie
from ..utils import getDateOfWeek

user = Blueprint('user', __name__)


def response(code, message, data=None):
    info = {'code': code, 'message': message, 'data': data}
    return json.dumps(info, ensure_ascii=False)


@user.route('/getDailyReport')
@check_cookie
def getDailyReport():
    try:
        content_dic = {}
        user, year, index = request.uid, int(request.args.get('year')),\
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
        
        
@user.route('/createDailyReport', methods=['POST'])
@check_cookie
def craete_dailyReport():
    form = request.form
    uid, content, type, date = form.get('uid'), form.get('content'), form.get('type'),\
                             form.get('date')
    if content and uid and type and date:
        Y, M, D = [int(i) for i in date.split('-')]
        timestamp = time.mktime(datetime.datetime(Y, M, D).timetuple())
        test_exist = DailyReport.query.filter_by(author=uid, timestamp=timestamp).first()
        if test_exist:
            return response(2, '已经提交过')
        dailyreport = DailyReport(uid, content, Y, M, D, timestamp, type)
        db.session.add(dailyreport)
        db.session.commit()
        return response('200', 'ok')
    else:
        return response('500', '提交参数错误')


@user.route('/updateDailyReport', methods=['POST'])
@check_cookie
def update_dailyReport():
    form = request.form
    id, content = form.get('id'), form.get('content')
    if content and id:
        log = DailyReport.query.filter_by(id=id).first()
        log.content = content
        db.session.add(log)
        db.session.commit()
        return response('200', 'ok')
    else:
        return response('500', '提交参数错误')


@user.route('/getDatesOfWeek/<int:year>')
@check_cookie
def getDatesOfWeek(year):
    today = datetime.datetime.now().date()
    now = today.isocalendar()
    if year > now[0]:
        dates = [getDateOfWeek(year, i) for i in range(1, now[1] + 1)]
        dates_str = [{'index': i + 1, 'data': '第%s周 (%s - %s)' % (i + 1, value[0].strftime("%m.%d"),\
                    value[-1].strftime("%m.%d"))} for i, value in enumerate(dates)]
        return response('200', 'ok', dates_str)
    elif year == now[0]:
        dates = [getDateOfWeek(year, i) for i in range(1, now[1] + 1)]
        dates_str = [{'index': i + 1, 'data': '第%s周 (%s - %s)' % (i + 1, value[0].strftime("%m.%d"),\
                    value[-1].strftime("%m.%d"))} for i, value in enumerate(dates)]
        return response('200', 'ok', dates_str)
    else:
        end = datetime.datetime(year, 12, 31)
        now = end.isocalendar()
        if now[1] < 50:
            _end = end - datetime.timedelta(days=(now[2] + 1))
            now = _end.isocalendar()
        dates = [getDateOfWeek(year, i) for i in range(1, now[1] + 1)]
        dates_str = [{'index': i + 1, 'data': '第%s周 (%s - %s)' % (i + 1, value[0].strftime("%m.%d"),\
                    value[-1].strftime("%m.%d"))} for i, value in enumerate(dates)]
        return response('200', 'ok', dates_str)


@user.route('/dailyreport/team')
@check_cookie
def dailyreport_team():
    display = 'none'
    now = datetime.datetime.now().date()
    today, week = now.strftime("%Y-%m-%d"), now.weekday()
    Y, M, D = [int(i) for i in today.split('-')]
    dateC = datetime.datetime(Y, M, D)
    timestamp = int(time.mktime(dateC.timetuple()))
    teams = [i.name for i in Team.query.all()]
    dic = {}
    for i in teams:
        dic[i] = []
    SQL = 'select u.username,t.name,dr.content \
            from roles r\
            LEFT JOIN users u\
            ON r.member=u.id\
            LEFT JOIN teams t\
            ON u.team=t.id\
            LEFT JOIN dailyreport dr\
            ON  dr.author=r.member \
            and dr.timestamp=%s\
            where r.leader=%s ' % (timestamp, request.uid)
    data = db.engine.execute(SQL)
    try:
        for i in data:
            dic[i[1]].append((i[0], i[2]))
    except KeyError:
        print i
    team_list, content = [], []
    for i in dic:
        if(dic[i]):
            team_list.append(i)
            content.append(dic[i])
    if not team_list:
        display = 'block'
    data = {'team': team_list, 'content': content}
    # print data
    return render_template('team_dailyreport.html', data=data,
                           today=today, display=display, week=week,
                           account=request.user, permission=request.permission,
                           rn=request.rn)

@user.route('/dailyreport/team_member')
@check_cookie
def dailyreport_team_member():
    today = datetime.datetime.now()
    year = today.isocalendar()[0]
    SQL = '''
            select r.member id,u.username,t.name from roles r 
            left join users u
            on r.member=u.id
            left join teams t
            on u.team=t.id
            where r.leader=%s
          '''%request.uid
    data = [i for i in db.engine.execute(SQL)]
    infos = {}
    for i in data:
        if i.name not in infos:
            infos[i.name] = []
        infos[i.name].append([i.id, i.username])
    if infos:
        infos = infos.items()
    return render_template('team_dailyreport_member.html',account=request.user, permission=request.permission,
                           rn=request.rn, infos=infos, year=year)


@user.route('/dailyreport/team/<teamname>')
@check_cookie
def dailyreport_team_search(teamname):
    date_str = request.args.get('date')
    if date_str:
        Y, M, D = [int(i) for i in date_str.split('-')]
        dateC = datetime.datetime(Y, M, D)
        timestamp = int(time.mktime(dateC.timetuple()))
    else:
        return response(1, '输入不符要求')
    dic = {teamname: []}
    SQL = 'select u.username,t.name,dr.content \
            from roles r\
            LEFT JOIN users u\
            ON r.member=u.id\
            RIGHT JOIN teams t\
            ON u.team=t.id and t.name="%s"\
            LEFT JOIN dailyreport dr\
            ON  dr.author=r.member \
            and dr.timestamp=%d\
            where r.leader=%d ' % (teamname, timestamp, request.uid)
    data = db.engine.execute(SQL)
    for i in data:
        dic[i[1]].append((i[0], i[2]))
    team_list, content = [], []
    for i in dic:
        if(dic[i]):
            team_list.append(i)
            content.append(dic[i])
    content = content[0] if content else content
    result = {'team': teamname, 'content': content}
    return response('200', 'ok', result)
