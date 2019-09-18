# 从模块的初始化文件中导入蓝图。
from flask import Blueprint, render_template, redirect, flash, url_for, session, request, Response, abort
from . import admin
from app.models import User, db, Admin
from flask import render_template, redirect, url_for, flash, session, request
from app.admin.forms import LoginForm

# @admin.route("/", methods=["GET", "POST"])
# def index():
#     """
#     后台登录
#     """
#
#     return "<h1>Hello World!</h1>"
#


# 路由定义使用装饰器进行定义
@admin.route("/", methods=["GET", "POST"])
def index():
    """
    后台登录
    """
    form = LoginForm()
    if form.validate_on_submit():
        data = form.data
        admin = Admin.query.filter_by(admin_id=data["account"]).first()
        # 密码错误时，check_pwd返回false,则此时not check_pwd(data["pwd"])为真。
        if not admin.admin_pwd == (data["pwd"]):
            flash("密码错误!", "err")
            return redirect(url_for("admin.index"))
        session["admin_id"] = admin.admin_id
        return redirect(url_for("admin.all"))
    return render_template("admin/login.html", form=form)


@admin.route("/logout/")
def logout():
    session.pop("admin_id", None)
    return redirect(url_for('admin.index'))


@admin.route("/all/")
def all():
    if not "admin_id" in session:
        return abort(403)
    form = User.query.all()
    # print(form)
    admin_id = session.get("admin_id")
    return render_template("admin/all.html", id=admin_id, form=form)


# 注销用户
@admin.route("/deuser/")
def deuser():
    if not "admin_id" in session:
        return abort(403)
    uid = int(request.args.get("id"))
    form = User.query.all()
    admin_id = session.get("admin_id")
    user = User.query.filter(User.id == uid).first()
    # 会员注销后为-1
    if user.vclass == 1:
        user.vclass = -1
    # 非会员注销后为-2
    else:
        user.vclass = -2
    db.session.add(user)
    db.session.commit()
    flash("已经成功注销id为%d的用户" % uid, "ok")
    return redirect(url_for('admin.all'))


# 恢复注销
@admin.route("/reuser/")
def reuser():
    if not "admin_id" in session:
        return abort(403)
    uid = int(request.args.get("id"))
    form = User.query.all()
    admin_id = session.get("admin_id")
    user = User.query.filter(User.id == uid).first()

    if user.vclass == -1:
        user.vclass = 1
    else:
        user.vclass = 0
    db.session.add(user)
    db.session.commit()
    flash("已经成功恢复id为%d的用户" % uid, "ok")
    return redirect(url_for('admin.all'))


# 升级账户
@admin.route("/upuser/")
def upuser():
    if not "admin_id" in session:
        return abort(403)
    uid = int(request.args.get("id"))
    form = User.query.all()
    admin_id = session.get("admin_id")
    user = User.query.filter(User.id == uid).first()


    user.vclass = 1
    db.session.add(user)
    db.session.commit()
    flash("已经成功升级id为%d的用户为高级账户" % uid, "ok")
    flash("已经成功升级id为%d的用户为高级账户" % uid, "ok")
    return redirect(url_for('admin.all'))


#
# # 删除歌曲
# @admin.route('/delete_music/<music_id>')
# def delete_music(music_id):
#     music = Music.query.get(music_id)
#     musicna = music.music_name
#     if music:
#         try:
#             db.session.delete(music)
#             db.session.commit()
#         except Exception as e:
#             print(e)
#             flash('删除歌曲失败')
#             db.session.rollback()
#     else:
#         flash('歌曲找不到')
#     flash("删除成功歌曲%s" % musicna)
#     return redirect(url_for('admin.manage'))


@admin.route('/manage/', methods=['GET', 'POST'])
def manage():
    return "默认用户名：admin , 密码：admin"
