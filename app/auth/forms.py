# -*- coding: utf-8 -*-
from flask.ext.wtf import Form
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import Required, Length, Email, Regexp, EqualTo
from wtforms import ValidationError
from ..models import User

class BaseForm(Form):
	LANGUAGES = ['zh']

class LoginForm(BaseForm):
	email = StringField(u'邮箱', validators = [Required(), Length(1, 64),
		Email()])
	password = PasswordField(u'密码', validators = [Required()])
	remember_me = BooleanField(u'记住密码')
	submit = SubmitField(u'登录')


class RegistrationForm(BaseForm):
	email = StringField(u'邮箱', validators = [Required(), Length(1, 64),
		Email()])
	username = StringField(u'用户名', validators = [Required(), 
		Length(1, 64), Regexp('^[A-Za-z][A-Za-z0-9_.]*$', 0,
		 u'用户名必须由字母、数字、下划线、点号组成')])
	password = PasswordField(u'密码', validators = [Required(), 
		EqualTo('password2', message = u'密码不一致')])
	password2 = PasswordField(u'确认密码', validators = [Required()])
	submit = SubmitField(u'注册')

	def validate_email(self, field):
		if User.query.filter_by(email = field.data).first():
			raise ValidationError(u'邮箱已被注册')

	def validate_username(self, field):
		if User.query.filter_by(username = field.data).first():
			raise ValidationError(u'用户名已存在')

class ChangePasswordForm(BaseForm):
	old_password = PasswordField(u'旧密码', validators = [Required()])
	password = PasswordField(u'新密码', validators = [Required(), 
		EqualTo('password2', message = u'密码不一致')])
	password2 = PasswordField(u'确认新密码', validators = [Required()])
	submit = SubmitField(u'更改密码')

class PasswordResetRequestForm(BaseForm):
	email  = StringField(u'邮箱', validators = [Required(), Length(1, 64),
		Email()])
	submit = SubmitField(u'确认')

class PasswordResetForm(BaseForm):
	email  = StringField(u'邮箱', validators = [Required(), Length(1, 64),
		Email()])
	password = PasswordField(u'新密码', validators = [Required(), 
		EqualTo('password2', message = u'密码不一致')])
	password2 = PasswordField(u'确认新密码', validators = [Required()])
	submit = SubmitField(u'重置密码')

	def validate_email(self, field):
		if User.query.filter_by(email=field.data).first() is None:
			raise ValidationError(u'未知的邮箱地址.')

class ChangeEmailForm(BaseForm):
	email = StringField(u'新邮箱', validators = [Required(), Length(1, 64),
		Email()])
	password = PasswordField(u'密码', validators = [Required()])
	submit = SubmitField(u'更换邮箱')

	def validate_email(self, field):
		if User.query.filter_by(email = field.data).first():
			raise ValidationError(u'邮箱已被注册')
