import os
from application import db
from datetime import datetime ,timedelta
from flask import current_app as app
from werkzeug.security import generate_password_hash, check_password_hash
import uuid
import jwt


class User(db.Model):
    id = db.Column(db.String(80), primary_key=True)
    name = db.Column(db.String(80),index=True)
    email = db.Column(db.String(80),index=True,unique=True)
    password = db.Column(db.String(128))
    phone = db.Column(db.String(80))
    admin = db.Column(db.Boolean)
    register_date = db.Column(db.DateTime)
    car = db.relationship('Car',backref='user',lazy='dynamic')
    bank = db.relationship('UserBank',backref='user',lazy='dynamic')
    booking = db.relationship('CarBooking',backref='renter',lazy='dynamic')
    message = db.relationship('Message', foreign_keys='Message.sender_id', backref='sender', lazy='dynamic')
    renter_review = db.relationship('RenterReview',backref='renter',lazy='dynamic')
    owner_review = db.relationship('OwnerReview',backref='owner',lazy='dynamic')

    liscence_1 =  db.Column(db.String(80))
    liscence_2 = db.Column(db.String(128))
    liscence_3 = db.Column(db.String(128))
    liscence_4 = db.Column(db.String(128))
    serial = db.Column(db.String(128))
    birth = db.Column(db.String(128))
    image = db.Column(db.Integer)


    @property
    def imgsrc(self):
        UPLOADED_FOLDER=app.config['USER_IMAGE_FOLDER']
        AWS_BUCKET  = app.config.get("AWS_BUCKET")
        AWS_CONTENT_URL = app.config.get("AWS_CONTENT_URL")
        if self.image:
            filename_template =  '{}.{}.raw.png'.format(self.id, self.image)
            if AWS_BUCKET:
                url_path = os.path.join(AWS_CONTENT_URL,AWS_BUCKET)
                file_path = os.path.join(UPLOADED_FOLDER,filename_template)
                img_src= url_path + file_path
            else:
                img_src = os.path.join(UPLOADED_FOLDER,filename_template)
        else:
            img_src = "/static/images/userphoto.png"
        return img_src

    def encode_auth_token(self, user_id):
        """Generates the auth token"""
        try:
            payload = {
                'exp': datetime.utcnow() + timedelta(
                        days=5
                    ),
                'iat': datetime.utcnow(),
                'sub': user_id
                }
            return jwt.encode(
                payload,
                app.config.get('SECRET_KEY'),
                algorithm='HS256'
                )
        except Exception as e:
            print(e)
            return False

    @staticmethod
    def decode_auth_token(auth_token):
        """
        Decodes the auth token - :param auth_token: - :return: integer|string
        """
        try:
            payload = jwt.decode(
                auth_token, app.config.get('SECRET_KEY'))
            return payload['sub']
        except jwt.ExpiredSignatureError:
            return "만료기간이 지났습니다 다시로그인해주세요"
        except jwt.InvalidTokenError:
            return '유요하지 않는 토큰입니다 다시로그인해주세요'


    def __init__(self, name, email, password, admin=False,register_date = None,phonenumber=None):
        self.id = uuid.uuid4().hex[:8].upper()
        self.name = name
        self.email = email
        self.password = self.set_password(password)
        self.admin = admin
        if register_date is None:
            register_date = datetime.now()
        self.register_date = register_date
        if phonenumber:
            self.phonenumber = phonenumber

    def set_password(self, password):
        return generate_password_hash(password)



    def check_password(self, password):
        return check_password_hash(self.password, password)


    def __repr__(self):
        return '<User %r>' % self.name


class UserBank(db.Model):
    id = db.Column(db.String,primary_key=True)
    user_id = db.Column(db.String,db.ForeignKey('user.id'),index=True)
    bank_code_std = db.Column(db.String(128),nullable=True)
    bank_code_sub = db.Column(db.String(128),nullable=True)
    bank_name = db.Column(db.String(128),nullable=True)
    account_holder_info = db.Column(db.String(128),nullable=False)
    account_num = db.Column(db.String(128),nullable=False)
    register_date = db.Column(db.DateTime)
    account_holder_name = db.Column(db.String(128),nullable=True)

    def __init__(self,user_id,bank_code_std, account_holder_info,bank_name,account_num,
                account_holder_name,bank_code_sub=None,register_date=None):
        self.id = uuid.uuid4().hex[:8].upper()
        self.user_id = user_id
        self.bank_code_std = bank_code_std
        self.account_holder_info = account_holder_info
        self.bank_name = bank_name
        self.account_num = account_num
        self.bank_code_sub = bank_code_sub
        self.account_holder_name = account_holder_name
        if register_date is None:
            self.register_date = datetime.now()
        else:
            self.register_date = register_date

    @property
    def to_json(self):
        return {
        "bank_name":self.bank_name,
        "register_date":datetime.strftime(self.register_date,"%Y-%m-%d %H:%M"),
        "bank_num":self.account_num[:4]
        }
