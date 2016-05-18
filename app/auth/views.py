from flask import render_template, redirect, request, url_for, flash
from flask.ext.login import login_user, logout_user, login_required, current_user
from datetime import datetime
from . import auth
from ..models import User
from .forms import LoginForm, RegistrationForm, ChangePasswordForm
from .forms import PasswordResetRequestForm, PasswordResetForm
from .forms import ChangeEmailForm
from ..email import send_email
from .. import db

# 用户登录
@auth.route('/login', methods = ['GET', 'POST'])
def login():
	form = LoginForm()
	if form.validate_on_submit():
		user = User.query.filter_by(email = form.email.data).first()
		if user is not None and user.verify_password(form.password.data):
			login_user(user, form.remember_me.data)
			# 用户未授权，显示登录表单，Flask-login保存原地址在'next'参数
			# request.args字典可读取
			return redirect(request.args.get('next') or url_for('main.index'))
		flash(u'用户名或密码无效！')
	return render_template('auth/login.html', form = form)

# 用户登出
@auth.route('/logout')
@login_required
def logout():
	logout_user()
	flash(u'您已经退出登录。')
	return redirect(url_for('main.index'))

# 用户注册
@auth.route('/register', methods = ['GET', 'POST'])
def register():
	form = RegistrationForm()
	if form.validate_on_submit():
		user = User(email = form.email.data, username = form.username.data,
			password = form.password.data)
		db.session.add(user)
		db.session.commit()
		token = user.generate_confirmation_token()
		send_email(user.email, u'确认你注册的【萌宠皮卡丘】的账户',
			'auth/email/confirm',user = user, token = token)
		flash(u"确认邮件已经发至您的邮箱，请查看！")
		return redirect(url_for('main.index'))
	return render_template('auth/register.html', form = form)

# 确认账户
@auth.route('/confirm/<token>')
@login_required
def confirm(token):
	if current_user.confirmed:
		return redirect(url_for('main.index'))
	if current_user.confirm(token):
		flash(u'你已经成功确认你的账户，谢谢！')
	else:
		flash(u'确认链接不合法或已经失效！')
	return redirect(url_for('main.index'))


@auth.before_app_request
def before_request():
	if current_user.is_authenticated and not current_user.confirmed \
	and request.endpoint[:5] != 'auth.' \
	and request.endpoint != 'static':
		return redirect(url_for('auth.unconfirmed'))

# 登录但是未确认
@auth.route('/unconfirmed')
def unconfirmed():
	if current_user.is_anonymous or current_user.confirmed:
		return redirect(url_for('main.index'))
	return render_template('auth/unconfirmed.html')

# 重新发送确认邮件
@auth.route('/confirm')
@login_required
def resend_confirmation():
	token = current_user.generate_confirmation_token()
	send_email(current_user.email, u'确认你注册的【萌宠皮卡丘】的账户',
		'auth/email/confirm',user = current_user, token = token)
	flash(u"确认邮件已经发至您的邮箱，请查看！")
	return redirect(url_for('main.index'))

# 修改密码
@auth.route('/change_password', methods = ['GET', 'POST'])
@login_required
def change_password():
	form = ChangePasswordForm()
	if form.validate_on_submit():
		if current_user.verify_password(form.old_password.data):
			current_user.password = form.password.data
			db.session.add(current_user)
			flash(u'您的密码已经重置。')
			return redirect(url_for('main.index'))
		else:
			flash(u'密码无效。')
	return render_template('auth/change_password.html', form = form)

# 忘记密码后申请重置
@auth.route('/reset', methods = ['GET', 'POST'])
def password_reset_request():
	if not current_user.is_anonymous:
		return redirect(url_for('main.index'))
	form = PasswordResetRequestForm()
	if form.validate_on_submit():
		user = User.query.filter_by(email = form.email.data).first()
		if user:
			token = user.generate_reset_password_token()
			send_email(user.email, u'请重置您的密码', 
				'auth/email/reset_password', user = user, token = token,
				next=request.args.get('next'))
			flash(u'重置密码的邮件已经发送至您的邮箱，请查看并按照提示操作。')
		return redirect(url_for('auth.login'))
	return render_template('auth/reset_password.html', form=form)

# 重置密码
@auth.route('/reset/<token>', methods = ['GET', 'POST'])
def password_reset(token):
	if not current_user.is_anonymous:
		return redirect(url_for('main.index'))
	form = PasswordResetForm()
	if form.validate_on_submit():
		user = User.query.filter_by(email = form.email.data).first()
		if user is None:
			return redirect(url_for('main.index'))
		if user.reset_password(token, form.password.data):
			flash(u'您已成功重置密码！')
			return redirect(url_for('auth.login'))
		else:
			return redirect(url_for('main.index'))
	return render_template('auth/reset_password.html', form = form)

# 申请更换邮箱地址
@auth.route('/change_email', methods = ['GET', 'POST'])
@login_required
def change_email_request():
	form = ChangeEmailForm()
	if form.validate_on_submit():
		if current_user.verify_password(form.password.data):
			new_email = form.email.data
			token = current_user.generate_email_change_token(new_email)
			send_email(new_email, u'请确认您的邮箱地址',
				'auth/email/change_email', user = current_user, 
				token = token)
			flash(u'确认邮件已发送至您的新邮箱，请查看并按照提示操作。')
			return redirect(url_for('main.index'))
		else:
			flash(u'邮箱或密码无效。')
	return render_template("auth/change_email.html", form = form)

@auth.route('/change_email/<token>', methods = ['GET', 'POST'])
@login_required
def change_email(token):
	if current_user.change_email(token):
		flash(u'您已成功更换邮箱。')
	else:
		flash(u'非法请求')
	return redirect(url_for('main.index'))

