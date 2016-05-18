# -*- coding: utf-8 -*-
from flask.ext.wtf import Form
from wtforms import StringField, SubmitField
from wtforms.validators import Required

class BaseForm(Form):
	LANGUAGES = ['zh']
		
class NameForm(BaseForm):
	name = StringField(u"你的名字：", validators = [Required()])
	submit = SubmitField(u"提交")
