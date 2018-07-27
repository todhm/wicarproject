from flask import Blueprint, render_template,session,make_response,request,flash,jsonify,redirect,url_for,send_from_directory,abort
from application import db,mdb
from utilities.dao.userdao import UserDao
from utilities.dao.cardao import CarDao
from utilities.decorators import logout_required,login_required, nophone_required,phonenumber_required,registered_phone_required,car_owner_match
from utilities.geoutil import parse_geocode,parse_search_api,get_geo_address
from utilities.timeutil import get_time_comb
from utilities.imaging import thumbnail_process,save_image
from werkzeug.datastructures import MultiDict
from werkzeug import secure_filename
from carupload.models import Car, CarOption,CarImage
from carupload.forms import CarOptionForm
from carupload.mongomodels import CarBrand,CarClass,CarModel
from caruser.models import User
import urllib.request
import requests
import json
import os

carupload_app = Blueprint('carupload_app',__name__)
carupload_app.config = {}



@carupload_app.record
def record_params(setup_state):
    app = setup_state.app
    carupload_app.config = dict([(key,value) for (key,value) in app.config.items()])
    # carshare_app.config['CLIENT_FB_JSON'] = json.loads(
    #      open(carshare_app.config['CLIENT_FB_SECRET_FILE'], 'r').read())



@carupload_app.route('/get_car_list')
@login_required
def get_car_list():
    email = session['email']
    user_id = UserDao.get_user_id(email)
    car_list = Car.query.filter(Car.user_id==user_id).all()
    for car in car_list:
        carImage = car.carimage\
                    .filter(CarImage.image_index==0)\
                    .filter(CarImage.active==True)\
                    .first()
        if carImage:
            car.imgsrc = carImage.imgsrc
        else:
            car.imgsrc=None
    return render_template("carupload/car_list.html",car_list = car_list)




@carupload_app.route('/car_setting/price_setting/<string:car_id>')
@login_required
@car_owner_match
def car_price_setting(car_id=""):
    return render_template("carbooking/dashboard.html")

@carupload_app.route('/car_setting/vacation_setting/<string:car_id>')
@login_required
@car_owner_match
def car_vacation_setting(car_id=""):
    return render_template("carbooking/dashboard.html")

@carupload_app.route('/car_setting/basic_setting/<string:car_id>')
@login_required
@car_owner_match
def car_basic_setting(car_id=""):
    return render_template("carbooking/dashboard.html")

@carupload_app.route('/car_setting/option_setting/<string:car_id>')
@login_required
@car_owner_match
def car_option_setting(car_id=""):
    return render_template("carbooking/dashboard.html")

@carupload_app.route('/car_setting/photo_setting/<string:car_id>')
@login_required
@car_owner_match
def car_photo_setting(car_id=""):
    return render_template("carbooking/dashboard.html")

@carupload_app.route('/deactivate_car/<string:car_id>',methods=["GET"])
@login_required
def deactivate_car(car_id=""):
    car = Car.query.filter(Car.id==car_id).first()
    car.active= 0
    db.session.commit()
    return redirect(url_for('carupload_app.get_car_list'))


@carupload_app.route('/car_registeration')
@carupload_app.route('/car_registeration/<string:car_id>')
@registered_phone_required
def register_car(car_id=""):
    email = session['email']
    name = UserDao.get_user_name(email)
    if not car_id:
        user_id = UserDao.get_user_id(email)
        car = CarDao.get_active_car_obj(user_id)
        if car:
            car_id = car.id
            return redirect(url_for('carupload_app.register_car',car_id=car_id))
    return render_template("carupload/car_registeration.html",email = email,username = name)

@carupload_app.route('/liscence_info/<string:car_id>')
@registered_phone_required
def liscence_registeration(car_id=""):
    email = session['email']
    name = UserDao.get_user_name(email)
    return render_template("carupload/car_registeration.html",email = email,username = name)



@carupload_app.route('/time_price/<string:car_id>')
@registered_phone_required
def time_price(car_id=""):
    return render_template("carupload/car_registeration.html",email="",username="")


@carupload_app.route('/register_pic/<string:car_id>')
@registered_phone_required
def register_pic(car_id=""):
    return render_template("carupload/car_registeration.html",email = "",username ="")


@carupload_app.route('/confirm_car/<string:car_id>')
@registered_phone_required
def confirm_car(car_id=""):
    return render_template("carupload/car_registeration.html",email = "",username = "")


    
