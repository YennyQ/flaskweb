import unittest
import json
from base64 import b64encode
from flask import url_for
from app import create_app, db
from app.models import Role, User, Post, Comment

class APITestCase(unittest.TestCase):
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

	def get_api_headers(self, username, password):
		return {
		'Authorization': 'Basic' + b64encode(
			(username + ':' + password).encode('utf-8')).decode('utf-8'),
		'Accept': 'application/json',
		'Content-Type': 'application/json'
		}

	# 测试匿名用户
	def test_on_auth(self):
		response = self.client.get(url_for('api.get_posts'),
			content_type='application/json')
		self.assertTrue(response.status_code == 200)

	def test_posts(self):
		r = Role.query.filter_by(name='User').first()
		self.assertIsNotNone(r)
		u = User(email='yanni@example.com', password='123', confirmed=True,
			role=r)
		db.session.add(u)
		db.session.commit()

		response = self.client.post(url_for('api.new_post'), 
			headers=self.get_api_headers('yanni@example.com', '123'),
			data=json.dumps({'body': ''}))
		self.assertTrue(response.status_code == 400)

		response = self.client.post(url_for('api.new_post'), 
			headers=self.get_api_headers('yanni@example.com', '123'),
			data=json.dumps({'body': 'body of test'}))
		self.assertTrue(response.status_code == 201)
		url = response.headers.get('Location')
		self.assertIsNotNone(url)

		response = self.client.get(url,
			headers=self.get_api_headers('yanni@example.com', '123'))
		self.assertTrue(response.status_code == 200)
		json_response = json.loads(response.data.decode('utf-8'))
		self.assertTrue(json_response['url'] == url)
		self.assertTrue(json_response['body'] == 'body of test')
		self.assertTrue(json_response['body_html'] == 
			'<p>body of the <em>blog</em> post</p>')
