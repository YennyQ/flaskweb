# -*- coding: utf-8 -*-
from flask import render_template, redirect, url_for, abort, flash
from flask import current_app, request, make_response
from flask.ext.login import login_required, current_user
from flask.ext.sqlalchemy import get_debug_queries
from datetime import datetime
from sqlalchemy.exc import IntegrityError
from . import main
from .forms import EditProfileForm, EditProfileAdminForm, PostForm, CommentForm
from .. import db
from ..models import Role, User, Permission, Post, Follow, Comment
from ..models import Category, post_tag_ref
from ..decorators import admin_required, permission_required


@main.route('/shutdown')
def server_shutdown():
	if not current_app.testing:
		abort(404)
	shutdown = request.environ.get('werkzeug.server.shutdown')
	if not shutdown:
		abort(500)
	shutdown()
	return "Shutting down..."

@main.after_app_request
def after_request(response):
	for query in get_debug_queries():
		if query.duration >= current_app.config['SLOW_DB_QUERY_TIME']:
			current_app.logger.warning(
				'Slow query: %s\nParameters: %s\nDuration: %f\nContext: %s\n' 
				% (query.statement, query.parameters, query.duration, 
					query.context))
	return response


@main.route('/', methods=['GET', 'POST'])
def index():
	show_followed = False
	if current_user.is_authenticated:
		show_followed = bool(request.cookies.get('show_followed', ''))
	if show_followed:
		query = current_user.followed_posts
	else:
		query = Post.query
	page = request.args.get('page', 1, type=int)
	pagination = query.order_by(Post.timestamp.desc()).paginate(
		page, per_page=current_app.config['POSTS_PER_PAGE'],
		error_out=False)
	posts = pagination.items
	return render_template('index.html', posts=posts, 
		show_followed=show_followed, pagination=pagination)

@main.route('/all')
@login_required
def show_all():
	resp = make_response(redirect(url_for('.index')))
	resp.set_cookie('show_followed', '', max_age=30*24*60*60)
	return resp

@main.route('/followed')
@login_required
def show_followed():
	resp = make_response(redirect(url_for('.index')))
	resp.set_cookie('show_followed', '1', max_age=30*24*60*60)
	return resp

@main.route('/user/<username>')
def user(username):
	user = User.query.filter_by(username=username).first_or_404()
	page = request.args.get('page', 1, type=int)
	pagination = user.posts.order_by(Post.timestamp.desc()).paginate(
		page, per_page=current_app.config['POSTS_PER_PAGE'],
		error_out=False)
	posts = pagination.items
	return render_template('user.html', user=user, posts=posts, 
		pagination=pagination)

@main.route('/edit_profile', methods=['GET','POST'])
@login_required
def edit_profile():
	form = EditProfileForm()
	if form.validate_on_submit():
		current_user.name = form.name.data
		current_user.location = form.location.data
		current_user.about_me = form.about_me.data
		db.session.add(current_user)
		db.session.commit()
		flash(u'您的个人资料已更新。')
		return redirect(url_for('.user', username=current_user.username))
	form.name.data = current_user.name
	form.location.data = current_user.location
	form.about_me.data = current_user.about_me
	return render_template('edit_profile.html', form=form)

@main.route('/edit_profile/<id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_profile_admin(id):
	user = User.query.get_or_404(id)
	form = EditProfileAdminForm(user=user)
	if form.validate_on_submit():
		user.email = form.email.data
		user.username = form.username.data
		user.confirmed = form.confirmed.data
		user.role = Role.query.get(form.role.data)
		user.name = form.name.data
		user.location = form.location.data
		user.about_me = form.about_me.data
		db.session.add(user)
		db.session.commit()
		flash(u"资料已更新。")
		return redirect(url_for('.user', username=user.username))
	form.email.data = user.email
	form.username.data = user.username
	form.confirmed.data = user.confirmed
	form.role.data = user.role_id
	form.name.data = user.name
	form.location.data = user.location
	form.about_me.data = user.about_me
	return render_template('edit_profile.html', form=form, user=user)


@main.route('/add_post', methods=['GET', 'POST'])
@login_required
def add_post():
	form = PostForm()
	if form.validate_on_submit():
		post = Post(title=form.title.data, body=form.body.data, 
			author=current_user._get_current_object())
		post.tags = form.tags.data
		post.category = Category.query.get(form.category.data)
		db.session.add(post)
		try:
			db.session.commit()
		except IntegrityError:
			db.session.rollback()
		flash(u'您的文章已发表。')
		return redirect(url_for('.post', id=post.id))
	return render_template('add_post.html', form=form, title=u'添加文章')

@main.route('/edit_post/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_post(id):
	post = Post.query.get_or_404(id)
	if current_user != post.author and \
	not current_user.can(Permission.ADMINISTER):
		abort(403)
	form = PostForm()
	if form.validate_on_submit():
		post.title = form.title.data
		post.body = form.body.data
		post.category = Category.query.get(form.category.data)
		for tag in post.tags.all():
			post.tags.remove(tag)
		for tag in form.tags.data:
			post.tags.append(tag)
		db.session.add(post)
		db.session.commit()
		flash(u'文章已更新。')
		return redirect(url_for('.post', id=post.id))
	form.title.data = post.title
	form.body.data = post.body
	form.tags.data = post.tags.all()
	form.category.data = post.category_id
	return render_template('add_post.html', form=form, title=u'编辑文章')



@main.route('/post/<int:id>', methods=['GET', 'POST'])
def post(id):
	post = Post.query.get_or_404(id)
	form = CommentForm()
	if form.validate_on_submit():
		# current_user是代理，真正的对象要_get_current_object()获取
		comment = Comment(body=form.body.data, post=post, 
			author=current_user._get_current_object())
		db.session.add(comment)
		db.session.commit()
		flash(u'您的评论已成功发表。')
		return redirect(url_for('.post', id=post.id, page=-1))
	page = request.args.get('page', 1, type=int)
	if page == -1:
		page = (post.comments.count() - 1) / current_app.config['COMMENTS_PER_PAGE'] + 1
	pagination = post.comments.order_by(Comment.timestamp.asc()).paginate(
		page, per_page=current_app.config['COMMENTS_PER_PAGE'],
		error_out=False)
	comments = pagination.items
	return render_template('post.html', post=post, comments=comments,
		form=form, pagination=pagination)



@main.route('/follow/<username>')
@login_required
@permission_required(Permission.FOLLOW)
def follow(username):
	user = User.query.filter_by(username=username).first()
	if user is None:
		flash(u'不合法的用户。')
		return redirect(url_for('.index'))
	if current_user.is_following(user):
		flash(u'您已经关注了该用户。')
		return redirect(url_for('.user', username=username))
	current_user.follow(user)
	flash(u'你关注了%s。' % username)
	return redirect(url_for('.user', username=username))

@main.route('/unfollow/<username>')
@login_required
@permission_required(Permission.FOLLOW)
def unfollow(username):
	user = User.query.filter_by(username=username).first()
	if user is None:
		flash(u'不合法的用户。')
		return redirect(url_for('.index'))
	if not current_user.is_following(user):
		flash(u'您没有关注该用户。')
		return redirect(url_for('.user', username=username))
	current_user.unfollow(user)
	flash(u'您已经取消了对%s的关注。' % username)
	return redirect(url_for('.user', username=username))

@main.route('/followers/<username>')
def followers(username):
	user = User.query.filter_by(username=username).first()
	if user is None:
		flash(u'不合法的用户。')
		return redirect(url_for('.index'))
	page = request.args.get('page', 1, type=int)
	pagination = user.followers.paginate(page,
		per_page=current_app.config['FOLLOWERS_PER_PAGE'],
		error_out=False)
	follows = [{'user': item.follower, 'timestamp':item.timestamp}
	for item in pagination.items]
	return render_template('followers.html', user=user, 
		title=u"关注我的人", endpoint='.followers', 
		pagination=pagination, follows=follows)

@main.route('/followed_by/<username>')
def followed_by(username):
	user = User.query.filter_by(username=username).first()
	if user is None:
		flash(u'不合法的用户。')
		return redirect(url_for('.index'))
	page = request.args.get('page', 1, type=int)
	pagination = user.followed.paginate(page,
		per_page=current_app.config['FOLLOWERS_PER_PAGE'],
		error_out=False)
	follows = [{'user': item.followed, 'timestamp': item.timestamp}
	for item in pagination.items]
	return render_template('followers.html', user=user,
		title="我关注的人", endpoint='.followed_by',
		pagination=pagination, follows=follows)


@main.route('/post/<int:post_id>/enable/<int:comment_id>')
@login_required
@permission_required(Permission.MODERATE_COMMENTS)
def comment_enable(post_id, comment_id):
	comment = Comment.query.get_or_404(comment_id)
	comment.disabled = False
	db.session.add(comment)
	db.session.commit()
	return redirect(url_for('.post', id=post_id))

@main.route('/post/<int:post_id>/disable/<int:comment_id>')
@login_required
@permission_required(Permission.MODERATE_COMMENTS)
def comment_disable(post_id, comment_id):
	comment = Comment.query.get_or_404(comment_id)
	comment.disabled = True
	db.session.add(comment)
	db.session.commit()
	return redirect(url_for('.post', id=post_id))


@main.route('/categories')
def categories():
	categories = Category.query.all()
	# 要显示的文章数
	amount = 3
	return render_template('showcategory.html', categories=categories, 
		amount=list(range(amount)), title=u'文章分类')

@main.route('/categories/<int:id>')
def category(id):
	category = Category.query.filter_by(id=id).first()
	title = category.name
	categories = Category.query.all()
	page = request.args.get('page', 1, type=int)
	pagination = category.posts.order_by(Post.timestamp.desc()).paginate(
		page, per_page=current_app.config['POSTS_PER_PAGE'],
		error_out=False)
	posts = pagination.items
	return render_template('category.html', id=id, posts=posts, 
		pagination=pagination, categories=categories, 
		title=category.name)

