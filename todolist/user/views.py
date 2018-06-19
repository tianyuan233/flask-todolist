from flask import render_template, redirect, url_for, abort, flash, request, current_app
from werkzeug.security import generate_password_hash

from . import user
from .forms import UserRegister, UserLogin
from ..main.forms import AddProject
from ..models import User, Project
from .. import db
from flask_login import login_user, logout_user, login_required, current_user
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from ..email import send_email



@user.route('/register',methods=["GET","POST"])
def register():
    form = UserRegister()
    if form.validate_on_submit():
        user = User(
            username=form.username.data,
            password=generate_password_hash(form.password.data),
            email=form.email.data
        )
        db.session.add(user)
        db.session.commit()
        token = user.generate_confirmation_token()
        send_email(to=user.email, subject='请验证您的邮箱',
                   template='confirm', user=user, token=token)
        Project.default_project(user)
        flash('注册成功')
        return redirect(url_for('main.index'))
    return render_template('user/register.html', form=form)


@user.route('/login',methods=["GET","POST"])
def login():
    form = UserLogin()
    projectform = AddProject()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user:
            login_user(user, True)
            flash('登录成功')
            return redirect(request.args.get('next') or url_for('main.index'))
        flash('帐号/密码不正确')
        return redirect(url_for('user.login'))
    return render_template('user/login.html', form=form, projectform=projectform)


@user.route('/confirm/<token>')
@login_required
def confirm(token):
    if current_user.confirmed:
        return redirect(url_for('main.index'))
    if current_user.confirm(token):
        flash('您的邮箱验证通过，谢谢！')
    else:
        flash('请检查链接有效，并且没有过期。')
    return redirect(url_for('main.index'))


@user.route('/confirm')
@login_required
def resend_email():
    token = current_user.generate_confirmation_token()
    send_email(to=current_user.email, subject='请验证您的邮箱',
               template='confirm', user=current_user, token=token)
    flash('一封新的账户验证邮件已发送到您的邮箱，请注意查收。')
    return redirect(url_for('main.index'))