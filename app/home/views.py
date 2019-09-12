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


# pymysql的数据库连接
# conn = pymysql.connect(host='127.0.0.1', port=3306, user='root', passwd='1232123', db='musicdb')

# @ home = Blueprint("home",__name__)

username = ""

# 根路由
@home.route("/")
def index():
    page_data = []
    # board = Board.query.filter(
    # ).order_by(
    #     Board.board_id
    # )
    # for v in board:
    #     data = Music.query.filter(
    #         Music.music_id == v.music_id
    #     ).limit(1)
    #     page_data += data
    return render_template("home/index.html", page_data=page_data)


# 欢迎主页
@home.route("/welcome/")
def welcome():
    if "user" not in session:
        return abort(404)
    
    # board = Board.query.filter(
    # ).order_by(
    #     Board.board_id
    # )
    # for v in board:
    #     data = Music.query.filter(
    #         Music.music_id == v.music_id
    #     ).limit(1)
    #     page_data += data

    return render_template("home/welcome.html", name=session.get('user'))


# 音乐库
@home.route("/fav/")
def fav():
    if "user" not in session:
        return abort(404)
    conn = pymysql.connect(host='127.0.0.1', port=3306, user='root', passwd='1232123', db='musicdb')

    cursor = conn.cursor()
    sql = "SELECT music_id FROM library WHERE id = '%s' " % session.get("user_id")
    cursor.execute(sql)
    results = cursor.fetchall()
    musicd = []
    for rol in results:
        musicd.append(rol[0])
    page_data = []
    for fid in musicd:
        data = Music.query.filter(
            Music.music_id == fid
        )
        # print(fid)
        page_data += data
    # print(page_data)
    page_data.reverse()
    return render_template("home/fav.html", name=session.get('user'), page_data=page_data)


@home.route("/mybuy/")
def mybuy():
    if "user" not in session:
        return abort(404)
    conn = pymysql.connect(host='127.0.0.1', port=3306, user='root', passwd='1232123', db='musicdb')

    cursor = conn.cursor()
    sql = "SELECT music_id FROM buy WHERE id = '%s' " % session.get("user_id")
    cursor.execute(sql)
    results = cursor.fetchall()
    musicd = []
    for rol in results:
        musicd.append(rol[0])
    page_data = []
    for bid in musicd:
        data = Music.query.filter(
            Music.music_id == bid
        )
        # print(bid)
        page_data += data
    # print(page_data)
    page_data.reverse()
    return render_template("home/mybuy.html", name=session.get('user'), page_data=page_data)


@home.route("/pop/")
def pop():
    page_data = Music.query.filter(
        Music.style == 'Pop'
    ).order_by(
        Music.listen.desc()
    ).limit(10)
    return render_template("home/pop.html", name=session.get('user'), page_data=page_data)


@home.route("/jazz/")
def jazz():
    page_data = Music.query.filter(
        Music.style == 'Jazz'
    ).order_by(
        Music.listen.desc()
    ).limit(10)
    return render_template("home/jazz.html", name=session.get('user'), page_data=page_data)


@home.route("/rb/")
def rb():
    page_data = Music.query.filter(
        Music.style == 'R&B'
    ).order_by(
        Music.listen.desc()
    ).limit(10)
    return render_template("home/rb.html", name=session.get('user'), page_data=page_data)


@home.route("/cla/")
def cla():
    page_data = Music.query.filter(
        Music.style == 'classical'
    ).order_by(
        Music.listen.desc()
    ).limit(10)
    return render_template("home/cla.html", name=session.get('user'), page_data=page_data)


@home.route("/folk/")
def folk():
    page_data = Music.query.filter(
        Music.style == 'Folk'
    ).order_by(
        Music.listen.desc()
    ).limit(10)
    return render_template("home/folk.html", name=session.get('user'), page_data=page_data)


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
    return "正在生成报告"



# 播放音乐
@home.route("/play/")
def play():
    isbuy = 0

    conn = pymysql.connect(host='127.0.0.1', port=3306, user='root', passwd='1232123', db='musicdb')
    cursor = conn.cursor()
    musicid = int(request.args.get('id'))
    sql = "SELECT free FROM music WHERE music_id = '%s' " % musicid
    cursor.execute(sql)
    results0 = cursor.fetchall()
    for k in results0:
        if 1 == k[0]:
            isbuy = 1

    # conn = pymysql.connect(host='39.106.214.230', port=3306, user='root', passwd='nucoj', db='musicdb')
    if session.get('user') is None:
        if isbuy == 1:
            music = Music.query.filter(
                Music.music_id == musicid
            ).first()
            return render_template("home/play.html", mus=music)
        flash("请先登录才继续接下来的操作", "err")
        return redirect(url_for('home.login'))

    vclass = session.get('vclass')

    if vclass == 0:
        id = session.get('user_id')
        sql = "SELECT music_id FROM buy WHERE id = '%s' " % id
        cursor.execute(sql)
        results = cursor.fetchall()
        for rol in results:
            if musicid == rol[0]:
                isbuy = 1
        if isbuy == 1:
            music = Music.query.filter(
                Music.music_id == musicid
            ).first()
            add = music.address
            pla = music.listen
            # print(pla)
            pla = pla + 1
            music.listen = pla
            # print(music.listen)
            db.session.add(music)
            db.session.commit()
            return render_template("home/play.html", name=session.get('user'), user=session.get('user_id'), mus=music)
        else:
            flash('请先购买此歌曲或订阅会员-err:%d' % musicid)
            return render_template("home/msg.html", name=session.get('user'))
    else:
        music = Music.query.filter(
            Music.music_id == musicid
        ).first()
        add = music.address
        pla = music.listen
        # print(pla)
        pla = pla + 1
        music.listen = pla
        # print(music.listen)
        db.session.add(music)
        db.session.commit()
        return render_template("home/play.html", name=session.get('user'), user=session.get('user_id'), mus=music)



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




#
# # 购买
# @home.route("/buy")
# def buy():
#     conn = pymysql.connect(host='127.0.0.1', port=3306, user='root', passwd='1232123', db='musicdb')
#     musicd = int(request.args.get('id'))
#     user_id = session.get('user_id')
#     cursor = conn.cursor()
#     sql = "SELECT music_id FROM buy WHERE id = '%s' " % user_id
#     cursor.execute(sql)
#     results = cursor.fetchall()
#     sql = "SELECT free FROM music WHERE music_id = '%s' " % musicd
#     cursor.execute(sql)
#     results0 = cursor.fetchall()
#     for k in results0:
#         if 1 == k[0]:
#             flash("此歌曲为免费歌曲，无需购买")
#             return render_template("home/msg.html", name=session.get('user'))
#     if int(session.get("vclass")) == 1:
#         flash("您现在为会员，无需单独购买歌曲")
#         return render_template("home/msg.html", name=session.get('user'))
#     for rol in results:
#         if musicd == rol[0]:
#             flash("您已经购买过此歌曲，请勿重复购买！")
#             return render_template("home/msg.html", name=session.get('user'))
#     result = User.query.filter(User.id == session.get('user_id')).first()
#     uss = result.wallet
#     uss = uss - 2
#     # print(uss)
#     if uss < 0:
#         flash("账户余额不足，请充值后再试")
#     else:
#         sql = "UPDATE user SET wallet = '%s' WHERE id = '%s' " % (uss, user_id)
#         cursor.execute(sql)
#         conn.commit()
#         wallet = uss
#         buy = Buy(
#             id=session.get('user_id'),
#             music_id=musicd
#         )
#         db.session.add(buy)
#         db.session.commit()
#         flash("购买成功，账户扣除2元，当前余额%d元" % wallet)
#     return render_template("home/msg.html", name=session.get('user'))


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
    return render_template("home/search.html", name=session.get('user'), key=key, count=count, page_data=page_data, form=form)


# 上传Excel文档
@home.route('/uploade', methods=['GET', 'POST'])
def upload_e():
    if request.method == 'POST':
        ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])
        MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB
        f = request.files['file']
        filename = secure_filename(f.filename)
        f.save('./excel/' + filename)
        workbook = xlrd.open_workbook('./excel/' + filename)
        table = workbook.sheet_names()
        for sheet in table:
            sheet2 = workbook.sheet_by_name(sheet)
            for row in range(1, sheet2.nrows):
                # rows = sheet2.row_values(2)  # 获取第行内容
                accuse = sheet2.col_values(1)[row]  # 获取第列内容
                line = sheet2.col_values(2)[row]  # 获取第列内容
                # print(sheet2.nrows)
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
        f = request.files['file']
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
        # session["user"] = username
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
                lable_id=tag
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
        number.append(i.lable_id)
    print(number)
    number = ",".join('%s' % ed for ed in number)
    letter = Letter.query.filter_by(letter_id=key).first()
    return render_template("home/msg.html", name=session.get('user'), id=letter, form=form, number=number)

@home.route('/tag', methods=['GET', 'POST'])
def tag():
    flash("标签修改成功", "acc")
    return redirect(url_for('home.msg', id=key))