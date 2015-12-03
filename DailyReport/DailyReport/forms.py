# -*- coding: utf-8 -*-
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

from flask_wtf import Form
from wtforms import (TextField, PasswordField, SelectField, RadioField)
from wtforms.validators import DataRequired, Length


class LoginForm(Form):
    name = TextField('name', validators=[DataRequired(), Length(min=1)])
    password = PasswordField('password', validators=[DataRequired(),
                             Length(min=4)])
    
    
class TeamForm(Form):
    id = TextField('id')
    name = TextField('name', validators=[DataRequired(),
                     Length(min=1, message='Little short for an email address?')])


class UserForm(Form):
    name = TextField('name', validators=[DataRequired(), Length(min=1)])
    account = TextField('account', validators=[DataRequired(), Length(min=1)])
    password = TextField('password', validators=[DataRequired(), Length(min=4)])
    team = SelectField('team', choices=[], validators=[])
    leader = TextField('leader', validators=[])
    permission = RadioField('permission', choices=[('0', 'normal'),
                            ('1', 'admin')], validators=[DataRequired()])
    
    def validate(self):
        not_validate = ['team', 'leader']
        for f, i in self._fields.iteritems():
            if f not in not_validate:
                if not i.validate(self):
                    return False
        return True
        
        
class UserUpdateForm(Form):
    id = TextField('id', validators=[DataRequired()])
    name = TextField('name', validators=[DataRequired(message='不能为空'), Length(min=1)])
    account = TextField('account', validators=[DataRequired(), Length(min=1)])
    team = SelectField('team', choices=[], validators=[])
    permission = RadioField('permission', choices=[('0', 'normal'),
                            ('1', 'admin')], validators=[DataRequired()])
    
    def validate(self):
        not_validate = ['team']
        for f, i in self._fields.iteritems():
            if f not in not_validate:
                if not i.validate(self):
                    return False
        return True
