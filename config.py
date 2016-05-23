# -*- coding: utf-8 -*-
import os

class Config:
	SECRET_KEY = os.environ.get('SECRET_KEY') or 'hard to guess string'
	SQLALCHEMY_COMMIT_ON_TEARDOWN = True
	SQLALCHEMY_TRACK_MODIFICATIONS = True
	MAIL_SUBJECT_PREFIX = u'[萌宠皮卡丘]'
	MAIL_SENDER = os.environ.get('MAIL_SENDER')
	FLASKWEB_ADMIN = os.environ.get('FLASKWEB_ADMIN')
	MAIL_SERVER = 'smtp.qq.com'
	MAIL_PORT = 465
	MAIL_USE_SSL = True
	MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
	MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
	FOLLOWERS_PER_PAGE = 10
	COMMENTS_PER_PAGE = 10
	SQLALCHEMY_RECORD_QUERIES = True
	SLOW_DB_QUERY_TIME = 0.5

	@staticmethod
	def init_app(app):
		pass


class DevelopmentConfig(Config):
	DEBUG = True
	SQLALCHEMY_DATABASE_URI = os.environ.get('DEV_DATABASE_URL')

class TestingConfig(Config):
	TESTING = True
	WTF_CSRF_ENABLED = False
	SQLALCHEMY_DATABASE_URI = os.environ.get('TEST_DATABASE_URL')

class ProductionConfig(Config):
	SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')

	@classmethod
	def init_app(cls, app):
		Config.init_app(app)

		import logging
		from logging.handlers import SMTPHandler
		credentials = None
		secure = None
		if getattr(cls, 'MAIL_USERNAME', None) is not None:
			credentials = (cls.MAIL_USERNAME, cls.MAIL_PASSWORD)
			if getattr(cls, 'MAIL_USE_SSL', None):
				secure = ()
			mail_handler = SMTPHandler(
				mailhost=(cls.MAIL_SERVER, cls.MAIL_PORT),
				fromaddr=cls.MAIL_SENDER,
				toaddrs=[cls.FLASKWEB_ADMIN],
				subject=cls.MAIL_SUBJECT_PREFIX + '应用错误',
				credentials=credentials,
				secure=secure)
			mail_handler.setLevel(logging.ERROR)
			app.logger.addHandler(mail_handler)

config = {
	'development': DevelopmentConfig,
	'testing': TestingConfig,
	'production': ProductionConfig,
	
	'default': DevelopmentConfig
}