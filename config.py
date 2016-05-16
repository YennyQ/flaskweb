import os

class Config:
	SECRET_KEY = os.environ.get('SECRET_KEY') or 'hard to guess string'
	SQLALCHEMY_COMMIT_ON_TEARDOWN = True
	SQLALCHEMY_TRACK_MODIFICATIONS = True
	MAIL_SUBJECT_PREFIX = '[萌宠皮卡丘]'
	MAIL_SENDER = os.environ.get('MAIL_SENDER') or '2842413757@qq.com'
	FLASKWEB_ADMIN = os.environ.get('FLASKWEB_ADMIN') or '2842413757@qq.com'

	@staticmethod
	def init_app(app):
		pass


class DevelopmentConfig(Config):
	DEBUG = True
	MAIL_SERVER = 'smtp.qq.com'
	MAIL_PORT = 465
	MAIL_USE_SSL = True
	MAIL_USERNAME = os.environ.get('MAIL_USERNAME') or '2842413757' 
	MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD') or 'lagujbqrfruzdffh'
	SQLALCHEMY_DATABASE_URI = os.environ.get('DEV_DATABASE_URL') or 'mysql+pymysql://root:7027010526@localhost/dev_data'

class TestingConfig(Config):
	TESTING = True
	SQLALCHEMY_DATABASE_URI = os.environ.get('TEST_DATABASE_URL') or 'mysql+pymysql://root:7027010526@localhost/test_data'

class ProductionConfig(Config):
	SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'mysql+pymysql://root:7027010526@localhost/data'

config = {
	'development': DevelopmentConfig,
	'testing': TestingConfig,
	'production': ProductionConfig,
	'default': DevelopmentConfig
}