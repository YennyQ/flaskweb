from flask import Flask
from flask.ext.bootstrap import Bootstrap
from flask.ext.moment import Moment
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.mail import Mail
from config import config
from flask.ext.login import LoginManager
from flask.ext.pagedown import PageDown
import pymysql

bootstrap = Bootstrap()
mail = Mail()
moment = Moment()
db = SQLAlchemy()
pagedown = PageDown()

login_manager = LoginManager()
# None\basic\strong不同安全等级以防止用户会话被篡改
# strong级别记录客户端IP地址和浏览器代理信息，异动则登出
login_manager.session_protection = 'strong'
login_manager.login_view = 'auth.login'


def create_app(config_name):
	app = Flask(__name__)
	# app.config这个对象提供的方法from_object()可以导入保存之前的配置
	app.config.from_object(config[config_name])
	config[config_name].init_app(app)

	bootstrap.init_app(app)
	mail.init_app(app)
	moment.init_app(app)
	db.init_app(app)
	login_manager.init_app(app)
	pagedown.init_app(app)

	# app实例的方法register_blueprint()注册蓝本
	from .main import main as main_blueprint
	app.register_blueprint(main_blueprint)

	from .auth import auth as auth_blueprint
	app.register_blueprint(auth_blueprint, url_prefix='/auth')

	from .api_1_0 import api as api_1_0_blueprint
	app.register_blueprint(api_1_0_blueprint, url_prefix='/api/v1.0')


	return app


