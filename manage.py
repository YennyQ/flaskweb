#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
COV = None
if os.environ.get('FLASK_COVERAGE'):
	import coverage
	COV = coverage.coverage(branch=True, include='app/*')
	COV.start()

from app import create_app, db
from app.models import User, Role, Post, Follow, Permission, Comment
from app.models import Category, Tag
from flask.ext.script import Manager, Shell
from flask.ext.migrate import Migrate, MigrateCommand

app = create_app(os.getenv('FLASK_CONFIG') or 'default')
manager = Manager(app)
migrate = Migrate(app, db) 

#app，db，表，集成到Python Shell
def make_shell_context():
	return dict(app=app, db=db, User=User, Role=Role, Post=Post,
		Follow=Follow, Permission=Permission, Comment=Comment, 
		Category=Category, Tag=Tag)
manager.add_command("shell", Shell(make_context = make_shell_context))
manager.add_command('db', MigrateCommand)



@manager.command
def test(coverage=False):
	"""Run the unit tests."""
	if coverage and not os.environ.get('FLASK_COVERAGE'):
		import sys
		os.environ['FLASK_COVERAGE'] = '1'
		os.execvp(sys.executable, [sys.executable] + sys.argv)
	import unittest
	tests = unittest.TestLoader().discover('tests')
	unittest.TextTestRunner(verbosity=2).run(tests)
	if COV:
		COV.stop()
		COV.save()
		print('Coverage Summary:')
		COV.report()
		basedir = os.path.abspath(os.path.dirname(__file__))
		covdir = os.path.join(basedir, 'tmp/coverage')
		COV.html_report(directory=covdir)
		print('HTML version: file://%s/index.html' % covdir)
		COV.erase()

@manager.command
def profile(length=25, profile_dir=None):
	"""Start the application under the code profiler."""
	from werkzeug.contrib.profiler import ProfilerMiddleware
	app.wsgi_app = ProfilerMiddleware(app.wsgi_app, restrictions=[length],
		profile_dir=profile_dir)
	app.run()

@manager.command
def deploy():
	"""Run deployment tasks."""
	from flask.ext.migrate import upgrade, revision
	from app.models import Role, User, Category, Tag
	db.drop_all()
	db.create_all()

	upgrade()

	Role.insert_roles()

	User.admin_update()

	User.add_self_follows()

	Category.create_categories()

	Tag.create_tags()


if __name__ == '__main__':
	manager.run()