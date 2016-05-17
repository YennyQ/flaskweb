# -*- coding: utf-8 -*-
from datetime import datetime
from flask import render_template, session, redirect, url_for

from . import main
from .forms import NameForm
from .. import db
from ..models import User
from manage import app
# -*- coding: utf-8 -*-
from ..email import send_email

@main.route('/', methods = ['GET', 'POST'])
def index():
	form = NameForm()
	# data能被validators的所有验证函数接受，下面这个方法就是True
	if form.validate_on_submit():
		#查询该用户是否已经在数据库记录
		user = User.query.filter_by(username = form.name.data).first()
		if user == None:
			user = User(username = form.name.data)
			db.session.add(user)
			session['known'] = False
			if app.config['FLASKWEB_ADMIN']:
				send_email(app.config['FLASKWEB_ADMIN'], 'New User', 
					'mail/new_user', user = user)
		else:
			session['known'] = True
		#将表单name的data保存在session中，并重定向以解决POST请求后刷新的警告
		session['name'] = form.name.data
		form.name.data = ''
		return redirect(url_for('.index'))
	return render_template('index.html', current_time = datetime.utcnow(), 
		form = form, name = session.get('name'), known = session.get('known', False))

@main.route('/user/<name>')
def user(name):
	return render_template('user.html', name = name)