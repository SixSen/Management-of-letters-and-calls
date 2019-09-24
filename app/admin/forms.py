# _*_ coding: utf-8 _*_
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, FileField, TextAreaField, SelectField, SelectMultipleField
from wtforms.validators import DataRequired, ValidationError, EqualTo
from app.models import Admin


class LoginForm(FlaskForm):
    """
    管理员登录表单
    """
    account = StringField(
        label="账号",
        validators=[
            DataRequired("账号不能为空")
        ],
        description="账号",
        render_kw={
            "class": "form-control",
            "placeholder": "请输入账号",
            # 注释此处显示forms报错errors信息
            # "required": "required"
        }
    )
    pwd = PasswordField(
        label="密码",
        validators=[
            DataRequired("密码不能为空")
        ],
        description="密码",
        render_kw={
            "class": "form-control",
            "placeholder": "请输入密码",
            # 注释此处显示forms报错errors信息
            # "required": "required"
        }
    )
    submit = SubmitField(
        '登录',
        render_kw={
            "class": "btn btn-primary btn-block btn-flat",
        }
    )

    def validate_account(self, field):
        account = field.data
        admin = Admin.query.filter_by(admin_id=account).count()
        if admin == 0:
            raise ValidationError("账号不存在! ")


class CloseForm(FlaskForm):
    """
    关键词表单
    """
    behalf_word = StringField(
        label="原有相关词",
        validators=[
            DataRequired("不可为空")
        ],
        description="关键词",
        render_kw={
            "class": "form-control",
            "placeholder": "关键词",
            # 注释此处显示forms报错errors信息
            # "required": "required"
        }
    )
    closedword = StringField(
        label="替换相关词",
        validators=[
            DataRequired("不可为空")
        ],
        description="替换词",
        render_kw={
            "class": "form-control",
            "placeholder": "替换词",
            # 注释此处显示forms报错errors信息
            # "required": "required"
        }
    )
    submit = SubmitField(
        '提交',
        render_kw={
            "class": "btn btn-primary btn-block btn-flat",
        }
    )

    def validate_account(self, field):
        account = field.data
        admin = Admin.query.filter_by(admin_id=account).count()
        if admin == 0:
            raise ValidationError("账号不存在! ")