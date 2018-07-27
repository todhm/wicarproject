import os
from application import db
from flask import current_app as app
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from geoalchemy2.types import Geometry
import sqlalchemy as sa
from utilities.formutil import to_json
from flask import url_for
import urllib.parse
import uuid

class Car(db.Model):
    id = db.Column(db.String(80), primary_key=True)
    user_id = db.Column(db.String,db.ForeignKey('user.id'),index=True)
    address = db.Column(db.String(256))
    detail_address = db.Column(db.Text)
    lat = db.Column(sa.types.DECIMAL(precision=10,scale=7,decimal_return_scale=7))
    lng = db.Column(sa.types.DECIMAL(precision=10,scale=7,decimal_return_scale=7))
    year = db.Column(db.Integer)
    distance = db.Column(db.Integer)
    brand = db.Column(db.String(80))
    class_name = db.Column(db.String(80))
    model = db.Column(db.String(80))
    transmission = db.Column(db.String(80))
    cartype = db.Column(db.String(80),default="sedan")
    register_date = db.Column(db.DateTime)
    active = db.Column(db.Boolean)

    booking = db.relationship('CarBooking',backref='car')
    caroption = db.relationship('CarOption',uselist=False,backref='car')
    carimage = db.relationship('CarImage',backref='car',lazy='dynamic')


    def __init__(self,user_id, address,detail_address, lat, lng,distance,brand,cartype,class_name, model,year,register_date=None,transmission="auto",active=0):
        self.id = uuid.uuid4().hex[:6].upper()
        self.user_id = user_id
        self.address = address
        self.detail_address = detail_address
        self.lat = lat
        self.lng = lng
        self.distance = distance
        self.year = year
        self.brand = brand
        self.cartype=cartype
        self.class_name = class_name
        self.model = model
        self.active = active
        self.transmission=transmission
        if register_date is None:
            self.register_date = datetime.now()
        else:
            self.register_date = register_date



    @property
    def json(self):
        return to_json(self, self.__class__)

    def __repr__(self):
        return '<Car %r>' % self.model



class CarOption(db.Model):
    id = db.Column(db.String,db.ForeignKey('car.id'),primary_key=True)
    advance_notice = db.Column(db.Integer,nullable=False,default=0)
    price = db.Column(db.Integer,nullable=False)
    weekly_discount = db.Column(db.Integer,nullable=True)
    monthly_discount = db.Column(db.Integer,nullable=True)
    plate_num = db.Column(db.String(20),nullable=False)
    description = db.Column(db.Text,nullable=False)
    register_date = db.Column(db.DateTime)
    roof_box = db.Column(db.Boolean)
    hid = db.Column(db.Boolean)
    led = db.Column(db.Boolean)
    auto_trunk = db.Column(db.Boolean)
    leather_seater = db.Column(db.Boolean)
    room_mirror = db.Column(db.Boolean)
    seat_6_4 = db.Column(db.Boolean)
    seat_heater_1st = db.Column(db.Boolean)
    seat_heater_2nd = db.Column(db.Boolean)
    seat_cooler = db.Column(db.Boolean)
    high_pass = db.Column(db.Boolean)
    button_starter = db.Column(db.Boolean)
    handle_heater = db.Column(db.Boolean)
    premium_audio = db.Column(db.Boolean)
    hud = db.Column(db.Boolean)
    smart_cruz_control = db.Column(db.Boolean)
    tpms = db.Column(db.Boolean)
    curtton_airbag= db.Column(db.Boolean)
    esp= db.Column(db.Boolean)
    isofix= db.Column(db.Boolean)
    slope_sleepery= db.Column(db.Boolean)
    front_collusion= db.Column(db.Boolean)
    lane_alarm= db.Column(db.Boolean)
    high_bim= db.Column(db.Boolean)
    aux_bluetooth= db.Column(db.Boolean)
    usb= db.Column(db.Boolean)
    auto_head_light= db.Column(db.Boolean)
    android_conn= db.Column(db.Boolean)
    apple_conn= db.Column(db.Boolean)
    electric_brake= db.Column(db.Boolean)
    navigation= db.Column(db.Boolean)
    backword_cam= db.Column(db.Boolean)
    surround_view_cam= db.Column(db.Boolean)
    bolt_220= db.Column(db.Boolean)
    smartphone_charge= db.Column(db.Boolean)


    def __init__(self,register_date = None):
        if register_date is None:
            self.register_date = datetime.now()
        else:
            self.register_date = register_date


    def __repr__(self):
        return '<CarOption %r>' % self.id


    @property
    def json(self):
        return to_json(self, self.__class__)

class CarImage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    car_id = db.Column(db.String,db.ForeignKey('car.id'),index=True)
    image = db.Column(db.Integer)
    filename = db.Column(db.String)
    image_index = db.Column(db.Integer)
    active = db.Column(db.Boolean)

    @property
    def originalImgSrc(self):
        UPLOADED_FOLDER=app.config['UPLOADED_FOLDER']
        filename_template =  '{}.{}.raw.png'.format(self.car_id, self.image)
        return filename_template



    @property
    def imgsrc(self):
        UPLOADED_FOLDER=app.config['UPLOADED_FOLDER']
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



    def __init__(self,car_id,image,active,image_index=None,filename=None):
        self.car_id = car_id
        self.image = image
        self.active =active
        self.image_index = image_index
        self.filename = filename if filename else  '{}.{}.jpg'.format(car_id, image)
