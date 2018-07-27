import random
import bcrypt
import string
import json
import requests
from flask import Blueprint, render_template,session,make_response,request,flash,jsonify,redirect,url_for,current_app,abort
import httplib2
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
from caruser.forms import SignUpForm, LoginForm, PhoneForm, CodeForm,SearchForm, BankAccountForm, TermForm
from caruser.models import User, UserBank
from carupload.models import Car,CarImage
from carbooking.models import UserCard,CarBooking,OwnerReview, RenterReview
from carbooking.forms import  CardNumberForm
from application import db
from utilities.decorators import logout_required,login_required, nophone_required,phonenumber_required
from utilities.smsutil import send_sms, send_confirmation_code
from utilities.timeutil import get_current_day, get_time_comb,get_end_day
from utilities.dao.userdao import UserDao
from utilities.dao.bookingdao import BookingDao
from utilities.hashutil import encrypt_hash
from utilities.imaging import save_user_profile
from utilities.common import verify_bank_data, get_bank_token, get_count
from sqlalchemy import and_
from datetime import datetime as dt
import requests
import uuid
from facebook import get_user_from_cookie,GraphAPI

userinfo_api_app = Blueprint('userinfo_api_app',__name__,template_folder='templates')

@userinfo_api_app.route('/api/get_user_carinfo/<string:user_id>')
def get_user_carinfo(user_id=""):
    result = {}
    return_cars = []
    user = User.query.filter(User.id==user_id).first()
    if not user:
        result['message'] = "fail"
        jsonify(result),404
    car_list = Car.query.filter(Car.user_id ==user_id).filter(Car.active==True).all()
    if not car_list:
        result['message'] = "fail"
        return jsonify(result)
    for car in car_list:
        if not car.caroption:
            continue
        car_info = {}
        booking_count =get_count(CarBooking,and_(
            CarBooking.car_id == car.id,
            CarBooking.status>=3
            ))
        car_info['trip_count'] = booking_count
        carImage = car.carimage\
                    .filter(CarImage.image_index==0)\
                    .filter(CarImage.active==True)\
                    .first()
        car_info['carimg'] = carImage.imgsrc if carImage else ""
        car_info['brand'] = car.brand
        car_info['class_name'] = car.class_name
        car_info['price'] = car.caroption.price
        car_info['car_year'] = car.year
        car_info['car_id'] = car.id
        return_cars.append(car_info)
    result['message'] = "success"
    result['car_list'] = return_cars
    return jsonify(result),200


@userinfo_api_app.route('/api/get_user_ownerreview/<string:user_id>')
def get_user_ownerreview(user_id=""):
    user = User.query.filter(User.id==user_id).first()
    result = {}
    if not user:
        result['message'] = "fail"
        jsonify(result),404
    total_owner_count = get_count(CarBooking,and_(
        Car.user_id == user.id,
        CarBooking.status>=3
        ))
    owner_review_list,owner_rate = BookingDao.get_owner_review_json(user.id)
    if not owner_review_list:
        result['message'] = "fail"
        return jsonify(result)
    result['message'] = 'success'
    result['owner_rate'] = owner_rate
    result['owner_review_list'] = owner_review_list
    result['total_owner_count'] = len(owner_review_list)

    return jsonify(result)

@userinfo_api_app.route('/api/get_user_renterreview/<string:user_id>')
def get_user_renterreview(user_id=""):
    user = User.query.filter(User.id==user_id).first()
    result = {}
    if not user:
        result['message'] = "fail"
        jsonify(result),404
    total_renter_count = get_count(CarBooking,and_(
        CarBooking.renter_id == user.id,
        CarBooking.status>=3
        ))
    renter_review_list,renter_rate = BookingDao.get_renter_review_json(user.id)
    if not renter_review_list:
        result['message'] = "fail"
        return jsonify(result)
    result['message'] = 'success'
    result['renter_review_list'] = renter_review_list
    result['renter_rate'] = renter_rate
    result['total_renter_count'] = len(renter_review_list)
    return jsonify(result)

@userinfo_api_app.route('/api/get_user_info/<string:user_id>')
def get_user_info(user_id=""):
    user = User.query.filter(User.id==user_id).first()
    result = {}
    if not user:
        message['message']="fail"
        return jsonify(message),400

    result['user_name'] = user.name
    result['register_year'] = user.register_date.year
    result['register_month'] = user.register_date.month
    result['register_day'] = user.register_date.day
    result['user_id'] = user.id
    result['userimg'] = user.imgsrc
    result['message'] = "success"
    return jsonify(result)
