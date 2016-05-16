from flask import Flask, render_template, session, redirect, url_for, flash
from flask.ext.script import Manager, Shell
from flask.ext.bootstrap import Bootstrap
from flask.ext.moment import Moment
from datetime import datetime
from flask.ext.wtf import Form
from wtforms import StringField, SubmitField
from wtforms.validators import Required
from flask.ext.sqlalchemy import SQLAlchemy
import os, pymysql
from flask.ext.migrate import Migrate, MigrateCommand
from flask.ext.mail import Mail, Message
from threading import Thread

app = Flask(__name__)
app.config['SECRET_KEY'] = 'hard to guess string'
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
app.config['MAIL_SERVER'] = 'smtp.qq.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USE_SSL'] = True
app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME') 
app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD')
app.config['MAIL_SUBJECT_PREFIX'] = '[萌宠皮卡丘]'
app.config['MAIL_SENDER'] = os.environ.get('MAIL_SENDER')
app.config['FLASKWEB_ADMIN'] = os.environ.get('FLASKWEB_ADMIN')

manager = Manager(app)
bootstrap = Bootstrap(app)
moment = Moment(app)
db = SQLAlchemy(app)
migrate = Migrate(app, db)
mail = Mail(app)


class Role(db.Model):
	__tablename__ = 'roles'
	id = db.Column(db.Integer, primary_key = True)
	name = db.Column(db.String(64), unique = True)
	users = db.relationship('User', backref = 'role', lazy = 'dynamic')

	def __repr__(self):
		return '<Role %r>' % self.name

class User(db.Model):
	__tablename__ = 'users'
	id = db.Column(db.Integer, primary_key = True)
	username = db.Column(db.String(64), unique =True, index = True)
	role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))

	def __repr__(self):
		return '<User %r>' % self.username


class NameForm(Form):
	name = StringField("你的名字：", validators = [Required()])
	submit = SubmitField("提交")


#app，db，表，集成到Python Shell
def make_shell_context():
	return dict(app = app, db = db, User = User, Role = Role)
manager.add_command("shell", Shell(make_context = make_shell_context))
manager.add_command('db', MigrateCommand)

def send_async_email(app, msg):
	with app.app_context():
		mail.send(msg)

def send_email(to, subject, template, **kwargs):
	msg = Message(app.config['MAIL_SUBJECT_PREFIX'] + subject, 
		sender = app.config['MAIL_SENDER'], recipients = [to])
	msg.body = render_template(template + '.txt', **kwargs)
	msg.html = render_template(template + '.html', **kwargs)
	thr = Thread(target = send_async_email, args = [app, msg])
	thr.start()
	return thr


@app.route('/', methods = ['GET', 'POST'])
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
		return redirect(url_for('index'))
	return render_template('index.html', current_time = datetime.utcnow(), 
		form = form, name = session.get('name'), known = session.get('known', False))


@app.route('/user/<name>')
def user(name):
	return render_template('user.html', name = name)


@app.errorhandler(404)
def page_not_found(e):

	return render_template('404.html'), 404

@app.errorhandler(500)
def internal_server_error(e):
	return render_template('500.html'), 500


if __name__ == '__main__':
	manager.run()

