# _*_ coding: utf-8 _*_
import datetime
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

'''
models文件是有关数据库相关文件
'''

app = Flask(__name__)

# 用于连接数据的数据库。
app.config['SQLALCHEMY_DATABASE_URI'] = "mysql+mysqlconnector://root:1232123@127.0.0.1:3306/xinfang"
# app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///:memory:"
# Flask-SQLAlchemy 将会追踪对象的修改并且发送信号。
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False


db = SQLAlchemy(app)


class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True, unique=True)  # 编号
    name = db.Column(db.String(100), nullable=False)  # 用户名
    pwd = db.Column(db.String(100), nullable=False)  # 密码
    email = db.Column(db.String(100), nullable=False)  # 邮箱
    vclass = db.Column(db.Integer, default=0, nullable=False)  # 管理员标识符
    phone = db.Column(db.String(11), nullable=False)  # 手机号

    def check_pwd(self, pwd):
        from werkzeug.security import check_password_hash
        return check_password_hash(self.pwd, pwd)

    def get_vclass(self):
        return self.vclass
    # user = db.relationship('Library')
    # def __repr__(self):
    #     return '<User %r>' % self.name


class Letter(db.Model):
    __tablename__ = 'letter'
    letter_id = db.Column(db.Integer, primary_key=True, unique=True)  # 信访信编号
    date = db.Column(db.DateTime, index=True, default=datetime.datetime.now())  # 发信日期
    sendAdr = db.Column(db.String(100), nullable=True)  # 发信地址
    receptAdr = db.Column(db.String(100), nullable=True)  # 受理地址
    byName = db.Column(db.String(100), nullable=True)  # 发信人
    byAdr = db.Column(db.String(100), nullable=True)  # 发信人地址
    byId = db.Column(db.String(100), nullable=True)  # 发信人身份证号
    byWork = db.Column(db.String(100), nullable=True)  # 发信人工作
    byTel = db.Column(db.String(100), nullable=True)  # 发信人电话
    contect = db.Column(db.Text, nullable=False)  # 信件内容
    accuseName = db.Column(db.String(100), nullable=True)  # 被举报人员
    accuseArea = db.Column(db.String(100), nullable=True)  # 被举报地区
    accuseDepartment = db.Column(db.String(100), nullable=True)  # 被举报部门

    def get_tag(self):
        tag = LetterTag.query.filter(LetterTag.letter == self.letter_id)
        number = []
        for i in tag:
            number.append(i.lable_id)
        pattern = {
            1: '不正当性关系',
            2: '贪污贿赂行为',
            3: '侵害群众利益',
            4: '挪用公款',
            5: '其他违法犯罪行为',
            6: '违反工作纪律',
            7: '违规参与公款宴请消费',
            8: '违规配备使用公务用车',
            9: '违法考试录取工作规定',
            10: '违反干部选拔任用规定',
            11: '权权交易和以权谋私',
            12: '损害党和政府的形象',
            13: '违反廉洁纪律',
            14: '违规操办婚丧喜庆事宜',
            15: '违规从事营利活动',
            16: '违规接受礼品礼金宴请服务',
            17: '违规发放津贴奖金',
            18: '在投票和选举中搞非组织活动',
        }
        tags = [pattern[x] if x in pattern else x for x in number]
        tags = "，".join('%s' % ed for ed in tags)
        return tags


class LetterTag(db.Model):
    __tablename__ = 'tag'
    tag_id = db.Column(db.Integer, primary_key=True, nullable=False, unique=True)  # tag主键
    letter = db.Column(db.Integer, nullable=False)  # 信访信编号
    lable_id = db.Column(db.Integer, nullable=False)  # 标签编号
    basis = db.Column(db.Text, nullable=True)  # 信件内容


class Admin(db.Model):
    __tablename__ = 'admin'
    admin_id = db.Column(db.String(10), primary_key=True, nullable=False, unique=True)  # 管理员账号
    admin_pwd = db.Column(db.String(100), nullable=False)  # 管理员密码


if __name__ == "__main__":
    db.drop_all()
    db.create_all()
