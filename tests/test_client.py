# -*- coding: utf-8 -*-
import re
import unittest
from flask import url_for
from app import create_app, db
from app.models import User, Role

class FlaskClientTestCase(unittest.TestCase):
	def setUp(self):
		self.app = create_app('testing')
		self.app_context = self.app.app_context()
		self.app_context.push()
		db.create_all()
		Role.insert_roles()
		self.client = self.app.test_client(use_cookies=True)

	def tearDown(self):
		db.session.remove()
		db.drop_all()
		self.app_context.pop()

	def test_home_page(self):
		response = self.client.get(url_for('main.index'))
		self.assertTrue(u'陌生人' in response.get_data(as_text=True))

	def test_register_and_login(self):
		# 注册新账户
		response = self.client.post(url_for('auth.register'), data={
			'email': 'yanni@example.com',
			'username': 'yanni',
			'password': 123,
			'password2': 123
			})
		self.assertTrue(response.status_code == 302)

		# 登录
		response = self.client.post(url_for('auth.login'), data={
			'email': 'yanni@example.com',
			'password': 123
			}, follow_redirects=True)
		data = response.get_data(as_text=True)
		# self.assertTrue(re.search(u'你好,\s*yanni\s*!', data))
		self.assertTrue(u'您还没有确认您的账户。' in data)

		# 发送确认令牌
		user = User.query.filter_by(email='yanni@example.com').first()
		token = user.generate_confirmation_token()
		response = self.client.get(url_for('auth.confirm', token=token),
			follow_redirects=True)
		data = response.get_data(as_text=True)
		self.assertTrue(u'你已经成功确认你的账户，谢谢！' in data)

		# 退出
		response = self.client.get(url_for('auth.logout'), 
			follow_redirects=True)
		data = response.get_data(as_text=True)
		self.assertTrue(u'您已经退出登录。' in data)
