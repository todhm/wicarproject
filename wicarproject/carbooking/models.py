import os
from application import db
from flask import current_app as app
from datetime import datetime as dt
from werkzeug.security import generate_password_hash, check_password_hash
from geoalchemy2.types import Geometry
import sqlalchemy as sa
from utilities.formutil import to_json
from flask import url_for
import uuid
from utilities.hashutil import encrypt_hash,decrypt_hash


#availability==2:이날은 항상예약가능.
#availability==1:이날은 특정시간만 예약가능.
#availability==0:이날은 예약 불가.
#데이터가 존재하지 않는 경우 상시 예약 가능
class UserTime(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String,db.ForeignKey('user.id'),index=True)
    dow = db.Column(db.Integer)
    availability = db.Column(db.Integer)
    start_time = db.Column(db.Integer,nullable=True)
    end_time = db.Column(db.Integer,nullable=True)
    register_date = db.Column(db.DateTime)

    def __init__(self,user_id,dow,availability,start_time,end_time,register_date=None):
        self.user_id = user_id
        self.dow= dow
        self.availability=availability
        self.start_time = start_time
        self.end_time=end_time
        if register_date is None:
            self.register_date = dt.now()
        else:
            self.register_date = register_date


class VacationData(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String,db.ForeignKey('user.id'),index=True)
    start_time = db.Column(db.DateTime)
    end_time = db.Column(db.DateTime)
    register_date = db.Column(db.DateTime)


    @property
    def start_time_fmt(self):
        return dt.strftime(self.start_time,"%Y-%m-%d %H:%M")


    @property
    def end_time_fmt(self):
        return dt.strftime(self.end_time,"%Y-%m-%d %H:%M")

    @classmethod
    def get_time_format(self):
        return "%Y-%m-%d %H:%M"


    def __init__(self,user_id,start_time,end_time,register_date=None):
        self.user_id = user_id
        self.start_time = start_time
        self.end_time = end_time
        if register_date is None:
            self.register_date = dt.now()
        else:
            register_date = register_date


class CarPriceSchedule(db.Model):

    id = db.Column(db.String, primary_key=True)
    car_id = db.Column(db.String,db.ForeignKey('car.id'),index=True)
    start_time = db.Column(db.DateTime)
    end_time = db.Column(db.DateTime)
    price = db.Column(db.Integer)
    register_date = db.Column(db.DateTime)

    def __init__(self,car_id,price,start_time,end_time,register_date=None):
        self.id = uuid.uuid4().hex[:8].upper()
        self.car_id = car_id
        self.price = price
        self.start_time= start_time
        self.end_time=end_time
        if register_date is None:
            self.register_date = dt.now()
        else:
            self.register_date = register_date

    @property
    def to_json(self):
        return {
        "id":self.id,
        "startDate":dt.strftime(self.start_time,"%Y-%m-%d %H:%M"),
        "endDate":dt.strftime(self.end_time,"%Y-%m-%d %H:%M"),
        "price":self.price,
        'title':"{}￦".format(self.price),
        'allDay':True
        }

class CarVacation(db.Model):

    id = db.Column(db.String, primary_key=True)
    car_id = db.Column(db.String,db.ForeignKey('car.id'),index=True)
    start_time = db.Column(db.DateTime)
    end_time = db.Column(db.DateTime)
    register_date = db.Column(db.DateTime)

    def __init__(self,car_id,start_time,end_time,register_date=None):
        self.id = uuid.uuid4().hex[:8].upper()
        self.car_id = car_id
        self.start_time= start_time
        self.end_time=end_time
        if register_date is None:
            self.register_date = dt.now()
        else:
            self.register_date = register_date

    @property
    def to_json(self):
        return {
        "id":self.id,
        "startDate":dt.strftime(self.start_time,"%Y-%m-%d %H:%M"),
        "endDate":dt.strftime(self.end_time,"%Y-%m-%d %H:%M"),
        'title':"차량휴무",
        'allDay':True
        }

# Status: 4 지급완료
# Status: 3 서비스완료
# Status: 2:예약 완료.
# Status: 1:차임대인 결제대기
# Status: 0:차주 수락대기
# Status: -1: 차주 예약전 취소.
# Status: -2: 차주 미응답.
# Status: -3: 임대인 예약 1시간 이전 취소. 전액환불
# Status: -4: 임대인 서비스 시작 7일이상취소. 전액환불 수수료미환불
# Status: -5: 임대인 서비스 시작 1일 ~ 7일취소. 부분미환불
# Status: -6: 임대인 서비스 24시간 전 취소. 전액 미환불
# Status: -7: 차주 예약 체결 후 서비스 시작 24시간 확보 취소 차주측 3만원 벌금 부과
# Status: -8: 차주 예약 체결 후 서비스 시작 24시간 이내 취소 차주측 5만원 벌금 부과.
class CarBooking(db.Model):
    id = db.Column(db.String,primary_key=True)
    car_id = db.Column(db.String,db.ForeignKey('car.id'),index=True)
    renter_id =  db.Column(db.String,db.ForeignKey('user.id'),index=True)
    total_price = db.Column(db.Integer)
    insurance_price = db.Column(db.Integer)
    owner_earning = db.Column(db.Integer)
    total_distance = db.Column(db.Integer)
    start_time = db.Column(db.DateTime)
    end_time = db.Column(db.DateTime)
    status = db.Column(db.Integer)
    register_date = db.Column(db.DateTime)
    payment = db.relationship('Payment',backref='booking',lazy='dynamic')
    owner_send = db.relationship('OwnerSend',backref='booking',lazy='dynamic')
    owner_review = db.relationship('OwnerReview',backref='booking',lazy='dynamic')
    renter_review = db.relationship('RenterReview',backref='booking',lazy='dynamic')



    def __init__(self,car_id,renter_id,total_price,insurance_price,owner_earning,start_time,end_time,status,total_distance,register_date =None):
        self.id = uuid.uuid4().hex[:8].upper()
        self.car_id = car_id
        self.renter_id = renter_id
        self.total_price = total_price
        self.insurance_price = insurance_price
        self.owner_earning = owner_earning
        self.start_time = start_time
        self.end_time = end_time
        self.status = status
        self.total_distance = total_distance
        if register_date is None:
            self.register_date = dt.now()
        else:
            self.register_date = register_date

    @classmethod
    def get_time_format(self):
        return "%Y-%m-%d %H:%M"


    @property
    def to_json(self):
        return {
        "car_id":self.car_id,
        "renter_id":self.renter_id,
        "total_price":self.total_price,
        "owner_earning":self.owner_earning,
        "start_time":self.start_time ,
        "end_time":self.end_time,
        "status":self.status,
        "register_date":dt.strftime(self.register_date,"%Y-%m-%d %H:%M"),
        }


class Payment(db.Model):
    id = db.Column(db.String,primary_key=True)
    booking_id = db.Column(db.String, db.ForeignKey('car_booking.id'),index=True)
    mid = db.Column(db.String)
    tid = db.Column(db.String)
    price = db.Column(db.Integer)
    register_date = db.Column(db.DateTime)
    is_cancel = db.Column(db.Boolean,default=False)


    def __init__(self,booking_id,mid,tid,price,is_cancel=False,register_date = None ):
        self.id = uuid.uuid4().hex[:8].upper()
        self.booking_id = booking_id
        self.mid = mid
        self.tid = tid
        self.price = price
        self.is_cancel = is_cancel

        if register_date is None:
            self.register_date = dt.now()
        else:
            self.register_date = register_date

class OwnerSend(db.Model):
    id = db.Column(db.String,primary_key=True)
    booking_id = db.Column(db.String, db.ForeignKey('car_booking.id'),index=True)
    user_id = db.Column(db.String, db.ForeignKey('user.id'),index=True)
    tran_amt = db.Column(db.Integer,nullable=False)
    rsp_code = db.Column(db.String(128),nullable=False)
    bank_tran_id = db.Column(db.String(128),nullable=False)
    bank_name = db.Column(db.String(128),nullable=True)
    bank_rsp_code = db.Column(db.String(128),nullable=False)
    account_holder_name = db.Column(db.String(128),nullable=True)
    bank_rsp_message = db.Column(db.String(128),nullable=True)
    account_num = db.Column(db.String(128),nullable=True)
    account_num_masked = db.Column(db.String(128),nullable=True)
    bank_tran_date = db.Column(db.String(128),nullable=True)
    print_content = db.Column(db.String(128),nullable=True)
    wd_bank_name = db.Column(db.String(128),nullable=True)
    wd_account_holder_name = db.Column(db.String(128),nullable=True)
    register_date = db.Column(db.DateTime)



    def __init__(self,booking_id,user_id,tran_amt,rsp_code,bank_tran_id,
        bank_name, bank_rsp_code, account_holder_name, bank_rsp_message,
        account_num, account_num_masked, bank_tran_date, print_content,
        wd_bank_name, wd_account_holder_name, register_date=None):
        self.id = uuid.uuid4().hex[:8].upper()
        self.booking_id = booking_id
        self.user_id = user_id
        self.tran_amt = tran_amt
        self.rsp_code = rsp_code
        self.bank_tran_id = bank_tran_id
        self.bank_name = bank_name
        self.bank_rsp_code = bank_rsp_code
        self.account_holder_name = account_holder_name
        self.bank_rsp_message = bank_rsp_message
        self.account_num = account_num
        self.account_num_masked = account_num_masked
        self.bank_tran_date = bank_tran_date
        self.print_content = print_content
        self.wd_bank_name = wd_bank_name
        self.wd_account_holder_name = wd_account_holder_name
        if register_date is None:
            self.register_date = dt.now()
        else:
            self.register_date = register_date

class UserCard(db.Model):
    id = db.Column(db.String,primary_key=True)
    name = db.Column(db.String(15),nullable=False)
    user_id = db.Column(db.String,db.ForeignKey('user.id'),index=True)
    customer_uid= db.Column(db.String(128),nullable=False)
    active = db.Column(db.Boolean,default=True,nullable=False)
    register_date = db.Column(db.DateTime)

    def __init__(self,user_id,name,customer_uid,active=1,register_date=None):
        self.id = uuid.uuid4().hex[:6].upper()
        self.name = name
        self.user_id = user_id
        self.customer_uid = customer_uid
        self.active = active
        if register_date is None:
            self.register_date = dt.now()
        else:
            self.register_date = register_date


    @property
    def to_json(self):
        return {
        "name":self.name,
        "register_date":dt.strftime(self.register_date,"%Y-%m-%d %H:%M"),
        }


class Message(db.Model):
    id = db.Column(db.String,primary_key=True)
    sender_id = db.Column(db.String,db.ForeignKey('user.id'),index=True)
    receiver_id =  db.Column(db.String,db.ForeignKey('user.id'),index=True)
    booking_id = db.Column(db.String, db.ForeignKey('car_booking.id'),index=True)
    message = db.Column(db.Text)
    register_date = db.Column(db.DateTime)

    def __init__(self,sender_id, receiver_id, booking_id,message,register_date=None):
        self.id = uuid.uuid4().hex[:8].upper()
        self.sender_id = sender_id
        self.receiver_id = receiver_id
        self.booking_id = booking_id
        self.message = message
        if register_date is None:
            self.register_date = dt.now()
        else:
            self.register_date = register_date



class OwnerReview(db.Model):
    id = db.Column(db.String,primary_key=True)
    booking_id = db.Column(db.String, db.ForeignKey('car_booking.id'),index=True)
    owner_id =  db.Column(db.String,db.ForeignKey('user.id'),index=True)
    review_point = db.Column(db.Float,nullable=False)
    review = db.Column(db.Text,nullable=True)
    register_date = db.Column(db.DateTime)

    def __init__(self,booking_id,owner_id,review,review_point,register_date = None ):
        self.id = uuid.uuid4().hex[:6].upper()
        self.booking_id = booking_id
        self.owner_id = owner_id
        self.review = review
        self.review_point = review_point
        if register_date is None:
            self.register_date = dt.now()
        else:
            self.register_date = register_date


class RenterReview(db.Model):
    id = db.Column(db.String,primary_key=True)
    booking_id = db.Column(db.String, db.ForeignKey('car_booking.id'),index=True)
    renter_id =  db.Column(db.String,db.ForeignKey('user.id'),index=True)
    review_point = db.Column(db.Float,nullable=False)
    review = db.Column(db.Text,nullable=True)
    register_date = db.Column(db.DateTime)

    def __init__(self,booking_id,renter_id,review,review_point,register_date = None):
        self.id = uuid.uuid4().hex[:6].upper()
        self.booking_id = booking_id
        self.renter_id = renter_id
        self.review = review
        self.review_point = review_point
        if register_date is None:
            self.register_date = dt.now()
        else:
            self.register_date = register_date


class BookingImage(db.Model):
    id = db.Column(db.String, primary_key=True)
    booking_id = db.Column(db.String,db.ForeignKey('car_booking.id'),index=True)
    sender_id = db.Column(db.String,db.ForeignKey('user.id'),index=True)
    image = db.Column(db.Integer)
    image_index = db.Column(db.Integer)
    filename = db.Column(db.String)
    description = db.Column(db.Text)
    active = db.Column(db.Boolean)
    register_date = db.Column(db.DateTime)



    @property
    def imgsrc(self):
        UPLOADED_FOLDER=app.config['BOOKING_IMAGE_FOLDER']
        filename_template = self.filename
        AWS_BUCKET  = app.config.get("AWS_BUCKET")
        AWS_CONTENT_URL = app.config.get("AWS_CONTENT_URL")

        if AWS_BUCKET:
            url_path = os.path.join(AWS_CONTENT_URL,AWS_BUCKET)
            file_path = os.path.join(UPLOADED_FOLDER,filename_template)
            img_src= url_path + file_path
        else:
            img_src = os.path.join(UPLOADED_FOLDER,filename_template)
        return img_src

    @property
    def originalImgSrc(self):
        UPLOADED_FOLDER=app.config['BOOKING_IMAGE_FOLDER']
        filename_template =  '{}.{}.raw.png'.format(self.booking_id, self.image)
        return filename_template


    def __init__(self,booking_id,sender_id,image,image_index,description=None,active=1,register_date=None,filename=None):
        self.id = str(uuid.uuid4())
        self.booking_id = booking_id
        self.sender_id = sender_id
        self.image = image
        self.image_index = image_index
        self.active =active
        self.description= description
        self.filename = filename if filename else  '{}.{}.jpg'.format(booking_id, image)

        if register_date is None:
            self.register_date = dt.now()
        else:
            self.register_date = register_date
