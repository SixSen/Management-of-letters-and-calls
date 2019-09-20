import datetime

import jieba
# from app import db, app, rd
import pymysql
import sys
import xlrd
from aip import AipOcr
from flask import render_template, redirect, flash, url_for, session, request, abort
from werkzeug import secure_filename
from werkzeug.security import generate_password_hash

from app.home.forms import LoginForm, RegisterForm, UserdetailForm, PwdForm, TagForm
from app.models import User, db, Letter, LetterTag
from . import home

'''
views是主要的路由文件
'''

# @ home = Blueprint("home",__name__)

# 根路由
@home.route("/")
def index():
    page_data = []

    return render_template("home/index.html", page_data=page_data)


# 欢迎主页
@home.route("/welcome/")
def welcome():
    # if "user" not in session:
    #     return abort(404)
    name = session.get('user')
    print(session.get('user'))
    return render_template("home/welcome.html", name=session.get('user'))


# 登录
@home.route("/login/", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        data = form.data
        user = User.query.filter_by(name=data["name"]).first()
        if user:
            if not user.check_pwd(data["pwd"]):  # 密码采用pbkdf2:sha256方式存储-所以要用这种方案判断密码
                flash("密码错误！", "err")
                return redirect(url_for("home.login"))
        else:
            flash("账户不存在！", "err")
            return redirect(url_for("home.login"))

        vclass = user.get_vclass()
        if vclass < 0:
            flash("账户已经被停用，请联系上级管理员！", "err")
            return redirect(url_for("home.login"))
        if vclass == 0:
            flash("账户为新用户，请联系管理员开通管理功能 ", "err")
            return redirect(url_for("home.login"))

        session["user"] = user.name
        session["user_id"] = user.id
        session["vclass"] = vclass
        username = user.name
        session.permanent = True
        return redirect(url_for("home.welcome"))
    return render_template("home/login.html", form=form)


# 退出登录
@home.route("/logout/")
def logout():
    session.pop("user", None)
    session.pop("user_id", None)
    session.pop("vclass", None)
    return redirect(url_for('home.login'))


@home.route("/out/")
def out():
    flash("您已成功登出！", "ok")
    return redirect(url_for('home.logout'))


# 个人中心——修改个人资料
@home.route("/user/", methods=["GET", "POST"])
def user():
    if "user" not in session:
        return abort(404)
    form = UserdetailForm()
    user = User.query.get(int(session["user_id"]))
    if request.method == "GET":
        form.name.data = user.name
        form.email.data = user.email
        form.phone.data = user.phone
    if form.validate_on_submit():
        data = form.data
        name_count = User.query.filter_by(name=data["name"]).count()
        if data["name"] != user.name and name_count == 1:
            flash("昵称已经存在！", "err")
            return redirect(url_for("home.user"))
        email_count = User.query.filter_by(email=data["email"]).count()
        if data["email"] != user.email and email_count == 1:
            flash("邮箱已经存在！", "err")
            return redirect(url_for("home.user"))

        phone_count = User.query.filter_by(phone=data["phone"]).count()
        if data["phone"] != user.phone and phone_count == 1:
            flash("手机号码已经存在！", "err")
            return redirect(url_for("home.user"))
        user.name = data["name"]
        user.email = data["email"]
        user.phone = data["phone"]
        db.session.add(user)
        db.session.commit()
        session["user"] = user.name
        flash("修改成功！", "ok")
        return redirect(url_for("home.user"))
    return render_template("home/user.html", name=session.get('user'), form=form, user=user)


# 个人中心——密码修改
@home.route("/pwd/", methods=["GET", "POST"])
def pwd():
    if "user" not in session:
        return abort(404)
    form = PwdForm()
    if form.validate_on_submit():
        data = form.data
        user1 = User.query.filter_by(name=session["user"]).first()
        if not user1.check_pwd(data["old_pwd"]):
            flash("旧密码错误！", "err")
            return redirect(url_for('home.pwd'))
        user1.pwd = generate_password_hash(data["new_pwd"])
        db.session.add(user1)
        db.session.commit()
        flash("修改密码成功，请重新登录！", "ok")
        return redirect(url_for('home.logout'))
    return render_template("home/pwd.html", name=session.get('user'), form=form)


# 个人中心——订阅会员
@home.route("/sub/", methods=["GET", "POST"])
def sub():
    if "user" not in session:
        return abort(404)
    form = PwdForm()
    if form.validate_on_submit():
        data = form.data
        user2 = User.query.filter_by(name=session["user"]).first()
        if not user2.check_pwd(data["old_pwd"]):
            flash("旧密码错误！", "err")
            return redirect(url_for('home.pwd'))
        user2.pwd = generate_password_hash(data["new_pwd"])
        db.session.add(user2)
        db.session.commit()
        flash("修改密码成功，请重新登录！", "ok")
        return redirect(url_for('home.logout'))
    return render_template("home/subscribe.html", name=session.get('user'), form=form)


# 管理中心——生成报告
@home.route("/getsub/")
def getsub():
    if "user" not in session:
        return abort(404)
    return "正在生成报告"


# 注册
@home.route("/register/", methods=["GET", "POST"])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        data = form.data
        new_user = User(
            name=data["name"],
            email=data["email"],
            phone=data["phone"],
            pwd=generate_password_hash(data["pwd"]),
        )
        db.session.add(new_user)
        db.session.commit()
        flash("注册成功！", "ok")
    return render_template("home/register.html", form=form)


# 搜索
@home.route("/search")
def search():
    if "user" not in session:
        flash("如需使用搜索功能请先登录", "err")
        return redirect(url_for('home.logout'))
    form = TagForm()
    key = request.args.get('key')
    # kee为防止SQL注入设置的过滤用字符串
    kee = key.replace('%', '`')
    if kee != key:
        key = ""
    if key == "":
        return redirect(url_for('home.welcome'))
    count = Letter.query.filter(
        Letter.contect.ilike('%' + key + '%')
    ).count()
    page_data = Letter.query.filter(
        Letter.contect.ilike('%' + key + '%')
    ).order_by(
        Letter.date.desc()
    )
    page_data.key = key

    return render_template("home/search.html", name=session.get('user'), key=key, count=count, page_data=page_data, form= form)


# 上传Excel文档
@home.route('/uploade', methods=['GET', 'POST'])
def upload_e():
    if request.method == 'POST':
        # ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])
        # MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB

        try:

            f = request.files['file']
        except Exception as e:
            if e:
                flash("请选择文件", "err")
                return redirect(url_for("home.welcome"))
        filename = secure_filename(f.filename)

        f.save('./excel/' + filename)
        workbook = xlrd.open_workbook('./excel/' + filename)
        table = workbook.sheet_names()
        for sheet in table:
            sheet2 = workbook.sheet_by_name(sheet)
            for row in range(1, sheet2.nrows):
                accuse = sheet2.col_values(1)[row]  # 获取第 列内容
                line = sheet2.col_values(2)[row]  # 获取第 列内容
                letter = Letter(
                    accuseArea=accuse,
                    contect=line
                )
                db.session.add(letter)
                db.session.commit()
        flash("信访信息文档上传成功", "acc")
        return redirect(url_for("home.welcome"))
    return "err"


# 上传信访信件照片
@home.route('/uploadp', methods=['GET', 'POST'])
def upload_p():
    if request.method == 'POST':
        UPLOAD_FOLDER = '/path/save'
        ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])
        MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB
        try:
            f = request.files['file']
        except Exception as e:
            if e:
                flash("请选择文件", "err")
                return redirect(url_for("home.welcome"))
        filename = secure_filename(f.filename)
        f.save(secure_filename(f.filename))

        # 定义常量
        APP_ID = '10379743'
        API_KEY = 'QGGvDG2yYiVFvujo6rlX4SvD'
        SECRET_KEY = 'PcEAUvFO0z0TyiCdhwrbG97iVBdyb3Pk'

        # 初始化文字识别分类器
        aipOcr = AipOcr(APP_ID, API_KEY, SECRET_KEY)

        # 读取图片
        filePath = f.filename

        def get_file_content(filePath):
            with open(filePath, 'rb') as fp:
                return fp.read()

        # 定义参数变量
        options = {
            'detect_direction': 'true',
            'language_type': 'CHN_ENG',
            # 'probability': 'true'
        }
        result = aipOcr.webImage(get_file_content(filePath), options)
        line = ""
        for word in result.get('words_result'):
            line = line + word.get("words")
        letter = Letter(
            accuseArea="来自照片上传",
            contect=line
        )
        db.session.add(letter)
        db.session.commit()
        # seg_list = jieba.cut(line, cut_all=True)
        # print("分词结果: " + "  ".join(seg_list))  # 全模式
        flash("信访文档照片上传成功", "acc")
        return redirect(url_for("home.welcome"))
    flash("信访文档照片上传失败", "err")
    return redirect(url_for("home.welcome"))


# 查看信件原文
@home.route('/msg', methods=['GET', 'POST'])
def msg():
    if request.method == 'POST':
        key = request.args.get('id')
        req = request.get_data("media", as_text=True)
        if req == '':
            flash("标签修改失败，请至少选择一个标签", "err")
            return redirect(url_for('home.msg', id=key))
        req = req.replace("&media=", " ")
        req = req.replace("media=", "")
        data = req.split(" ")
        tags = list(map(int, data))
        conn = pymysql.connect(host='127.0.0.1', port=3306, user='root', passwd='1232123', db='xinfang')
        cursor = conn.cursor()
        sql = "DELETE FROM `tag` WHERE `letter`=%s;" % (key)
        cursor.execute(sql)
        conn.commit()
        for tag in tags:
            letter_tag = LetterTag(
                letter=key,
                label_id=tag
            )
            db.session.add(letter_tag)
            db.session.commit()
        flash("标签修改成功", "acc")
        return redirect(url_for('home.msg', id=key))

    form = TagForm()
    key = request.args.get('id')
    tag = LetterTag.query.filter(LetterTag.letter == key)
    number = []
    for i in tag:
        number.append(i.label_id)
    number = ",".join('%s' % ed for ed in number)
    letter = Letter.query.filter_by(letter_id=key).first()
    return render_template("home/msg.html", name=session.get('user'), id=letter, form=form, number=number)


@home.route('/tag', methods=['GET', 'POST'])
def tag():
    if "user" not in session:
        return abort(404)
    key = request.args.get('key')
    count = LetterTag.query.filter(LetterTag.label_id == key).count()
    page_data = []
    letterTag = LetterTag.query.filter(LetterTag.label_id == key)
    qq=[]
    for t in letterTag:
        qq.append(t.letter)
    for i in qq:
        page_data += Letter.query.filter(Letter.letter_id == i)
    return render_template("home/tagbar.html", name=session.get('user'),page_data=page_data,count=count,key=key)