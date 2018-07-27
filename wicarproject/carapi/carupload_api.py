from flask import Blueprint, render_template,session,make_response,request,flash,jsonify,redirect,url_for,send_from_directory,abort
from application import db,mdb
from utilities.dao.userdao import UserDao
from utilities.dao.cardao import CarDao
from utilities.dao.bookingdao import BookingDao
from utilities.decorators import logout_required,login_required, nophone_required,phonenumber_required,registered_phone_required,car_owner_match, api_login_match
from utilities.geoutil import parse_geocode,parse_search_api,get_geo_address
from utilities.timeutil import get_time_comb
from utilities.imaging import thumbnail_process,save_image
from utilities.common import verify_bank_data, get_bank_token,convert_wtf_error
from werkzeug.datastructures import MultiDict
from werkzeug import secure_filename
from carupload.models import Car, CarOption,CarImage
from carupload.forms import CarOptionForm,OrdinaryPriceForm,CarOptionEditForm
from carupload.mongomodels import CarBrand,CarClass,CarModel
from caruser.models import User, UserBank
from caruser.forms import BankAccountForm,UserLiscenceApiForm
import urllib.request
from utilities.common import verify_bank_data, get_bank_token
from datetime import datetime as dt
import requests
import json
import os

carupload_api_app = Blueprint('carupload_api_app',__name__)



@carupload_api_app.route('/api/get_car/<string:car_id>')
def return_car_data(car_id=""):
    car = Car.query.filter(Car.id ==car_id).first()
    car_data = {}
    if car:
        car_data['valueLabel'] = {'pointX':float(car.lng),'pointY':float(car.lat),'address':car.address}
        car_data['address'] = {'value':car.address,'label': car.address,'addressObj':car_data['valueLabel']}
        car_data['detail_address'] = car.detail_address
        car_data['distance'] = car.distance
        car_data['brand'] = car.brand
        car_data['model'] = car.model
        car_data['cartype'] = car.cartype
        car_data['className'] = car.class_name
        car_data['transmission'] = car.transmission
        car_data['year'] = car.year
        car_data['active'] = car.active
        car_data['message']="success"
        return jsonify(car_data)
    else:
        car_data['message']="fail"
        return jsonify(car_data)




@carupload_api_app.route('/api/getLastStatus')
@carupload_api_app.route('/api/getLastStatus/<string:car_id>')
def contacts(car_id=""):
    data={}
    data['stage_name'] = ["자동차 등록","세부사항조정","사진 등록","최종확인"]
    page_list = []
    email = session['email'] if session.get("email") else 'hmmon@sharemonsters.net'
    user = UserDao.get_user_obj(email)
    userBank = User.query.filter(UserBank.user_id==user.id).first()
    current_state = 0
    #get last status by completion of register process
    if not car_id:
        data['current_state'] =current_state
        data['status'] = [False,False,False,False,False]
        data['current_page'] = '/car_registeration'
        page_list.append(data['current_page'])
        if not user.liscence_1 or not userBank:
            data['stage_name'] = ["자동차 등록","면허*계좌등록","세부사항조정","사진 등록","최종확인"]
        data['page_list'] = page_list
        return jsonify(data)

    car = Car.query.filter(Car.id == car_id).first()

    #block unvalid api
    if car_id and not car:
        abort(403)

    elif car and  car.user_id != user.id:
        abort(403)

    if car_id:
        prev_page = '/car_registeration' + '/' + str(car_id)
        page_list.append(prev_page)
        if not user.liscence_1 or not userBank:
            data['stage_name'] = ["자동차 등록","면허*계좌등록","세부사항조정","사진 등록","최종확인"]
            current_state += 1
            data['current_page'] = '/liscence_info'+"/" + str(car_id)
            page_list.append(data['current_page'])
            data['current_state'] = current_state
            data['page_list'] = page_list
        else:
            current_state += 1
            data['current_page'] = '/time_price'+"/" + str(car_id)
            page_list.append(data['current_page'])
            data['page_list'] = page_list
            data['current_state'] = current_state
            carOption = CarOption.query.filter(CarOption.id == car_id).first()
            if  carOption:
                current_state += 1
                data['current_page'] = '/register_pic'+"/" + str(car_id)
                page_list.append(data['current_page'])
                data['current_state'] = current_state
                data['page_list'] = page_list
                carImage = CarImage.query.filter(CarImage.car_id == car_id).filter(CarImage.active==True).all()
                if carImage and len(carImage)< 4:
                    car.active =0
                    db.session.commit()

                if carImage and len(carImage)>=4:
                    current_state += 1
                    data['current_page'] = '/confirm_car'+"/" + str(car_id)
                    page_list.append(data['current_page'])
                    data['current_state'] = current_state
                    data['page_list'] = page_list
                    if car.active:
                        data['current_page'] = '/car_registeration'+"/" + str(car_id)
                        data['current_state'] = current_state
                        data['stage_name'] = ["자동차 등록","세부사항조정","사진 등록"]
                        data['page_list'] = page_list[:-1]

    return jsonify(data)



@carupload_api_app.route('/api/getLiscenceRegion')
def get_liscence_region():
    regionStr = '''
                경기
                서울
                경기북부
                강원
                충북
                충남
                전북
                경북
                경남
                제주
                대구
                인천
                광주
                대전
                울산
                부산
                11
                28
                13
                14
                15
                16
                17
                18
                19
                20
                21
                22
                23
                24
                25
                26
                12
                '''
    regionList = list(filter(lambda x: len(x) != 0,map(lambda x: x.strip(),regionStr.split('\n'))))
    return jsonify(regionList)


@carupload_api_app.route('/api/getCarBrand')
def get_brand_name():
    brandNameList = CarBrand.objects.values_list('codeName').to_json()
    return brandNameList

@carupload_api_app.route('/api/getCarClass')
def get_class_name():
    brand_name = request.args.get('brandName')
    classNameList = CarClass.objects.filter(makerName=brand_name).values_list('codeName').to_json()
    return classNameList

@carupload_api_app.route('/api/getCarModel')
def get_model_name():
    class_name = request.args.get('className')
    modelNameList = CarModel.objects.filter(className=class_name).values_list('codeName').to_json()
    return modelNameList



#Modify : Car
#Requires:
#Effects: insert row in Car Model
@carupload_api_app.route('/api/add_basic_info',methods=["POST"])
@carupload_api_app.route('/api/add_basic_info/<string:car_id>',methods=["POST"])
def add_basic_info(car_id=""):
    data = request.get_json()
    address_obj = data.get('address')
    if  not address_obj.get('pointX') or not address_obj.get('pointY'):
        address_query = address_obj['address']
        coord_data = get_geo_address(address_query)
        if len(coord_data) ==1 and coord_data[0].get('pointX'):
            address_obj['pointX'] = coord_data[0]['pointX']
            address_obj['pointY'] = coord_data[0]['pointY']
    user_id = UserDao.get_user_id(data.get('email'))


    if not car_id:
        car = Car(
                  user_id=user_id,
                  address=address_obj.get('address'),
                  detail_address = data.get('detail_address'),
                  year = data.get('year'),
                  lng = address_obj.get('pointX'),
                  lat = address_obj.get('pointY'),
                  cartype = data.get('cartype'),
                  distance = data.get('distance'),
                  brand= data.get('brandName'),
                  class_name = data.get('className'),
                  model = data.get('model'),
                  transmission = data.get('transmission'),
                  active=0
                  )
        db.session.add(car)
        db.session.commit()
    else:
        car = Car.query.filter(Car.id ==car_id).first()
        if car.user_id == user_id:
            car.address = address_obj.get('address')
            car.detail_address = data.get('detail_address')
            car.lng = address_obj.get('pointX')
            car.lat = address_obj.get('pointY')
            car.distance = data.get('distance')
            car.brand= data.get('brandName')
            car.cartype = data.get('cartype')
            car.class_name = data.get('className')
            car.model = data.get('model')
            car.year = data.get('year')
            car.transmission = data.get('transmission')
            db.session.commit()
    jsonData = {}
    jsonData['message'] = "success"
    jsonData['car_id'] = car.id
    return jsonify(jsonData)




@carupload_api_app.route('/api/get_address_info',methods=["POST"])
def return_address():
    data=request.get_json()
    address = data.get('address')
    if not address:
        return not_found()
    addressList = get_geo_address(address)
    return jsonify(addressList)


@carupload_api_app.route('/api/add_liscence_info',methods=["POST"])
@api_login_match
def add_liscence_info():
    data = request.get_json()
    form = UserLiscenceApiForm(data=data)
    result = {}
    if form.validate():
        userLiscence =UserDao.add_liscence_user(
            user_id=session['user_id'],
            liscence_1 = form.liscence_1.data,
            liscence_2 = form.liscence_2.data,
            liscence_3 = form.liscence_3.data,
            liscence_4 = form.liscence_4.data,
            serialNumber= form.serialNumber.data,
            birth = form.birth.data,
        )
        if userLiscence:
            result['message'] = "success"
        else:
            result['message']="fail"
            result['errorMessage']="통신에실패햐였습니다. 다시 시도해주세요"

    else:
        result= convert_wtf_error(result,form)

    return jsonify(result)

@carupload_api_app.route('/api/get_liscence')
@api_login_match
def get_liscence_info():
    user_id =session['user_id']
    result = UserDao.get_user_liscence(user_id)
    return jsonify(result)

@carupload_api_app.route('/api/add_car_option/<string:car_id>',methods=["POST"])
@car_owner_match
def add_car_time(car_id):
    request_data = request.get_json()
    request_data['id'] = car_id
    request_data['price'] = int(request_data['price']) if request_data.get('price') else ""
    request_data['advance_notice'] = int(request_data['advance_notice']) if request_data.get('advance_notice')  else 0
    form = CarOptionForm(**request_data,csrf_enabled=False)
    if form.validate():
        carOption = CarOption.query.filter(CarOption.id==car_id).first()
        if not carOption:
            carOption= CarOption()

        form.populate_obj(carOption)
        db.session.add(carOption)
        db.session.commit()
        return_data={}
        return_data['message'] = 'success'
        return jsonify(return_data)


    else:
        abort(403)

@carupload_api_app.route('/api/edit_car_option/<string:car_id>',methods=["POST"])
@car_owner_match
def edit_car_option(car_id):
    request_data = request.get_json()
    request_data['id'] = car_id
    request_data['advance_notice'] = int(request_data['advance_notice']) if request_data.get('advance_notice')  else 0
    return_data={}
    form = CarOptionEditForm(**request_data,csrf_enabled=False)
    if form.validate():
        carOption = CarOption.query.filter(CarOption.id==car_id).first()
        if not carOption:
            return_data['message']="fail"
            return_data['errorMessage']="해당옵션이 존재하지 않습니다"
            return jsonify(return_data)

        form.populate_obj(carOption)
        db.session.add(carOption)
        db.session.commit()
        return_data['message'] = 'success'
        return jsonify(return_data)

    else:
        result= convert_wtf_error(return_data,form)
        return jsonify(result)

@carupload_api_app.route('/api/get_car_option/<string:car_id>',methods=["GET"])
@car_owner_match
def get_car_time(car_id):
    carOption  = CarOption.query.filter(CarOption.id==car_id).first()
    if carOption:
        return carOption.json
    else:
        data = {}
        data['advance_notice'] = ""
        data['price'] = ""
        data['plate_num'] = ""
        data['description']=""
        data['roof_box']=False
        data['hid']=False
        data['led']=False
        data['auto_trunk']=False
        data['leather_seater']=False
        data['room_mirror']=False
        data['seat_6_4']=False
        data['seat_heater_1st']=False
        data['seat_heater_2nd']=False
        data['seat_cooler']=False
        data['high_pass']=False
        data['button_starter']=False
        data['handle_heater']=False
        data['premium_audio']=False
        data['hud']=False
        data['smart_cruz_control']=False
        data['tpms']= False
        data['curtton_airbag']=False
        data['esp']=False
        data['isofix']=False
        data['slope_sleepery']=False
        data['front_collusion']=False
        data['lane_alarm']=False
        data['high_bim']=False
        data['aux_bluetooth']=False
        data['usb']=False
        data['auto_head_light']=False
        data['android_conn']=False
        data['apple_conn']=False
        data['electric_brake']=False
        data['navigation']=False
        data['backword_cam']=False
        data['surround_view_cam']=False
        data['bolt_220']=False
        data['smartphone_charge']=False
        return jsonify(data)


@carupload_api_app.route('/api/get_car_price/<string:car_id>',methods=["GET"])
@car_owner_match
def get_car_price(car_id):
    carOption  = CarOption.query.filter(CarOption.id==car_id).first()
    result={}
    request_data = request.get_json()
    if carOption:
        result['message'] = "success"
        result['ordinaryPrice'] = carOption.price
        result['weeklyDiscount'] = carOption.weekly_discount if carOption.weekly_discount else 0
        result['monthlyDiscount'] = carOption.monthly_discount if carOption.monthly_discount else 0
    else:
        result['message']="fail"
    return jsonify(result)

@carupload_api_app.route('/api/add_car_ordinary_price/<string:car_id>',methods=["POST"])
@car_owner_match
def add_car_ordinary_price(car_id):
    result={}
    data = request.get_json()
    form = OrdinaryPriceForm(data = data)
    if form.validate():
        carOption  = CarOption.query.filter(CarOption.id==car_id).first()
        if carOption:
            carOption.price = form.ordinaryPrice.data
            carOption.weekly_discount = form.weeklyDiscount.data
            carOption.monthly_discount = form.monthlyDiscount.data
            db.session.commit()
            result['message'] = "success"

        else:
            result['message']="fail"
            result['errorMessage']="미등록 차량"

    else:
        result['message']="fail"
        error_list = []
        for field, errors in form.errors.items():
            for error in errors:
                error_list.append(error)
        result['errorMessage'] = error_list[0]
    return jsonify(result)

@carupload_api_app.route('/api/upload_image/<string:car_id>',methods=["POST"])
@car_owner_match
def upload_images(car_id = ""):
    file = request.files['image']
    image_id = save_image(file,car_id)
    file.close()

    #이미지가 성공적으로 저장되었으면 DB에 url저장.
    message={}
    imageList = []
    carImages =CarImage.query.filter(CarImage.car_id ==car_id).filter(CarImage.active==True).order_by(CarImage.image_index).all()
    if image_id:
        message['message'] = 'success'
        if carImages:
            last_index = carImages[-1].image_index
            new_image_index = last_index + 1
        else:
            new_image_index = 0
        carImage = CarImage(
            car_id = car_id,
            image = image_id,
            image_index = new_image_index,
            active = 1
        )
        db.session.add(carImage)
        db.session.commit()
        carImages.append(carImage)

    else:
        message['message'] = 'fail'
    for image in carImages:
        image_object = {}
        image_object['url'] = image.imgsrc
        image_object['image_index'] = image.image_index
        imageList.append(image_object)

    message['imgList'] = imageList
    return jsonify(message)



@carupload_api_app.route('/api/update_image/<string:car_id>',methods=["POST"])
@car_owner_match
def update_images(car_id = ""):
    file = request.files['image']
    image_index = request.form.get('image_index')
    image_id = save_image(file,car_id)
    file.close()
    #이미지가 성공적으로 저장되었으면 DB에 url저장.
    message={}
    imageList = []
    message['message'] = "fail"
    if image_id :
        image_index = int(image_index)
        carimage = CarDao.update_image(car_id,image_index,image_id)
        if carimage:
            message['message'] = 'success'


    carImages =CarImage.query\
        .filter(CarImage.car_id ==car_id)\
        .filter(CarImage.active==True)\
        .order_by(CarImage.image_index)\
        .all()

    if carImages:
        for image in carImages:
            image_object = {}
            image_object['url'] = image.imgsrc
            image_object['image_index'] = image.image_index
            imageList.append(image_object)

    message['imgList'] = imageList
    return jsonify(message)



@carupload_api_app.route('/api/get_images/<string:car_id>')
def get_images(car_id = ""):
    message={}
    message['message']="fail"
    carImages =CarImage.query.filter(CarImage.car_id ==car_id).filter(CarImage.active==True).order_by(CarImage.image_index).all()
    car = Car.query.filter(Car.id==car_id).first()
    if car:
        is_active = car.active
        message['active'] = is_active
    if carImages:
        imageList = []
        for image in carImages:
            image_object = {}
            image_object['url'] = image.imgsrc
            image_object['image_index'] = image.image_index
            imageList.append(image_object)
        message['message'] = 'success'
        message['imgList'] = imageList
    return jsonify(message)




@carupload_api_app.route('/api/remove_image/<string:car_id>',methods=["POST"])
@car_owner_match
def remove_image(car_id = ""):
    message={}
    data = request.get_json()
    image_index = data['image_index']
    carImage = CarImage.query.filter(CarImage.car_id==car_id).filter(CarImage.active==True).filter(CarImage.image_index==image_index).first()
    message['message'] = 'fail'
    if carImage:
        carImage.active = 0
        db.session.commit()
        message['message'] = 'success'
    carImages =CarImage.query.filter(CarImage.car_id ==car_id).filter(CarImage.active==True).order_by(CarImage.image_index).all()
    if carImages:
        imageList = []
        for image in carImages:
            image_object = {}
            image_object['url'] = image.imgsrc
            image_object['image_index'] = image.image_index
            imageList.append(image_object)
        message['imgList'] = imageList
        return jsonify(message)
    else:
        message['imgList'] = []
        return jsonify(message)



@carupload_api_app.route('/api/activate_car/<string:car_id>',methods=["POST"])
@car_owner_match
def activate_car(car_id = ""):
    car= Car.query.filter(Car.id==car_id).first()
    message = {}
    if car:
        car.active = 1
        db.session.commit()
        message['message'] = 'success'
        return jsonify(message)
    else:
        message['message'] = 'fail'
        return jsonify(message)



@carupload_api_app.route('/api/get_bank_account')
@api_login_match
def get_bank_account():
    result = {}
    user_id = session['user_id']
    bank = UserBank.query.filter_by(user_id = user_id).first()
    if bank:
        result['message']='success'
        result['bank_code_std'] = bank.bank_code_std
        result['account_holder_info'] = bank.account_holder_info
        result['account_holder_name']=bank.account_holder_name
        result['account_num'] = bank.account_num
        return jsonify(result)
    else:
        result['message']="fail"
        return jsonify(result)

@carupload_api_app.route('/api/add_bank_account',methods=["POST"])
@api_login_match
def add_bank_account():
    result = {}
    user_id = session['user_id']
    request_data = request.get_json()
    bankForm = BankAccountForm(data=request_data,csrf_enabled=False)
    if bankForm.validate():
        userBank =UserDao.add_bank_with_form(user_id=user_id,form=bankForm)
        if userBank:
            result['message']="success"
            return jsonify(result)
        else:
            result['message'] = "서버에 문제가 발생했습니다. 잠시 후 다시 시도해주세요."
            return jsonify(result),500

    else:
        bankError = list(bankForm.errors.items())[0][1][0]
        result['message'] = bankError
        return jsonify(result),400
