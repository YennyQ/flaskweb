# -*- coding: utf-8 -*-
from flask import Blueprint

# 蓝本构造函数需传入两个指定参数，蓝本名和蓝本所在模块
# 只有蓝本注册到程序上后，路由才成为程序一部分
main = Blueprint('main', __name__)

from . import views, errors
from ..models import Permission

@main.app_context_processor
def inject_permissions():
	return dict(Permission = Permission)