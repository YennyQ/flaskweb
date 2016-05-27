# -*- coding: utf-8 -*-
import re
import threading
import unittest
from selenium import webdriver
from app import create_app, db

class SeleniumTestCase(unittest.TestCase):
	client = None

	@classmethod
	def setUpClass(cls):
		try:
			cls.client = webdriver.Firefox()
		except:
			pass
		if cls.client:
			cls.app = create_app('testing')
			cls.app_context = cls.app.app_context()
			cls.app_context.push()

			import logging
			logger = logging.getLogger('werkzeug')
			logger.setLevel('ERROR')

			db.create_all()
			Role.insert_roles()
			User.generate_fake(10)
			Post.generate_fake(10)

			admin_role = Role.query.filter_by(permissions=0xff).first()
			admin = User(email='yanni@example.com',
				username='yanni', password='123',
				role=admin_role, confirmed=True)
			db.session.add(admin)
			db.session.commit()

			threading.Thread(target=cls.app.run).start()

	@classmethod
	def tearDown(cls):
		if cls.client:
			cls.client.get('http://localhost:5000/shudown')
			cls.client.close()

			db.drop_all()
			db.session.remove()

			cls.app_context.pop()

	def setUp(self):
		if not self.client:
			self.skipTest('Web browser not available')

	def tearDown(self):
		pass

	def test_admin_home_page(self):
		self.client.get('http://localhost:5000/')
		self.assertTrue(re.search(u'你好,\s+陌生人!', 
			self.client.page_source))

		self.client.find_element_by_link_text(u'登入').click()
		self.assertTrue('<h1>登录</h1>' in self.client.page_source)
