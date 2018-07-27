from flask import Blueprint, render_template, session, make_response, request, flash, jsonify, redirect, url_for, send_from_directory, abort,current_app
from werkzeug.datastructures import MultiDict
from datetime import datetime as dt
from flask_wtf import FlaskForm,Form
from application import db, mdb
from caruser.forms import SearchForm
from caruser.models import User
from carupload.models import CarImage, Car
from carbooking.forms import *
from carbooking.models import *
from utilities.geoutil import get_geo_address
from utilities.smsutil import send_sms,send_lms, send_payment_error
from utilities.timeutil import find_duplicate_time, daterange,get_total_rental_days
from utilities.errorutil import return_booking_error
from utilities.dao.cardao import CarDao
from utilities.dao.userdao import UserDao
from utilities.dao.bookingdao import BookingDao
from utilities.decorators import *
from utilities.hashutil import encrypt_hash,decrypt_hash
from utilities.flask_tracking.documents import Tracking
from utilities.common import *
from utilities.imaging import save_image
from mongoengine.queryset.visitor import Q
from sqlalchemy import and_
from datetime import datetime as dt
from datetime import timedelta
import json
import uuid

carbooking_api_app = Blueprint('carbooking_api_app',__name__)



@carbooking_api_app.route('/api/get_car_list',methods=["GET"])
def get_car_list():
    if session.get('search_data'):
        search_data = session['search_data']
        if  not  search_data.get('pointX'):
            address_list = get_geo_address(search_data['address'])
            search_data['pointX'] = address_list[0]['pointX']
            search_data['pointY'] = address_list[0]['pointY']
        result = CarDao.get_searched_car(
            search_data,
            startDate=search_data.get('startDate'),
            endDate=search_data.get('endDate'),
            startTime=search_data.get('startTime'),
            endTime=search_data.get('endTime')
            )
        return jsonify(result)

    result = CarDao.get_all_car()
    return jsonify(result)


@carbooking_api_app.route('/api/get_car_for_booking/<string:car_id>')
def get_car_info(car_id):
    car = Car.query.filter(Car.id==car_id).first()
    if not car:
        abort(403)
    car_owner = car.user
    result =  {}
    result['username'] = car_owner.name
    result['user_id'] = car_owner.id
    result['userimg'] = car_owner.imgsrc
    result['address'] = car.address
    result['brand'] = car.brand
    result['model'] = car.model
    result['class_name'] = car.class_name
    result['year'] = car.year
    result['caroption'] = json.loads(car.caroption.json)
    if session.get('search_data'):
        search_data = session['search_data']
        result['bookingStartTime'] = search_data.get('startDate') + " "+search_data.get('startTime')
        result['bookingEndTime'] = search_data.get('endDate') + " "+search_data.get('endTime')
        startDateTime = dt.strptime(result['bookingStartTime'],"%m/%d/%Y %H:%M")
        endDateTime = dt.strptime(result['bookingEndTime'],"%m/%d/%Y %H:%M")
        result['caroption']['price'] = CarDao.get_median_car_price_without_discount(car.id,startDateTime,endDateTime)
    result['distance'] = car.distance
    ownerReviewList = OwnerReview\
        .query\
        .filter(OwnerReview.owner_id==car_owner.id)\
        .order_by(OwnerReview.register_date.desc()).all()
    review_list = []
    point = 0

    for owner_review in ownerReviewList:
        review = {}
        review['username'] = owner_review.booking.renter.name
        review['user_img'] = owner_review.booking.renter.imgsrc
        review['message'] = owner_review.review
        review['point'] = owner_review.review_point
        review['date'] = owner_review.register_date.strftime("%Y-%m-%d %H:%m")
        point += owner_review.review_point
        review_list.append(review)
    result['reviewList'] = review_list
    result['reviewRate'] = point / max(len(ownerReviewList),1)
    total_booking_count =get_count(CarBooking,Car.user_id==car_owner.id)
    response_count = get_count(CarBooking,
        and_(Car.user_id == car_owner.id,
            CarBooking.status>0))
    result['totalBookingCount'] = response_count
    result['responseRate'] = int( (response_count/max(total_booking_count,1)) * 100)
    return jsonify(result)


@carbooking_api_app.route('/api/get_time_availability')
@api_login_match
def get_time_availability():
    user_id = session['user_id']
    user_time_list = UserTime.query.filter(UserTime.user_id==user_id).order_by(UserTime.dow).all()
    result = {}
    availability =[
        {"start": "0", "end": "30", "dailyAlways": "2", "label": "월"},
        {"start": "0", "end": "30", "dailyAlways": "2", "label": "화"},
        {"start": "0", "end": "30", "dailyAlways": "2", "label": "수"},
        {"start": "0", "end": "30", "dailyAlways": "2", "label": "목"},
        {"start": "0", "end": "30", "dailyAlways": "2", "label": "금"},
        {"start": "0", "end": "30", "dailyAlways": "2", "label": "토"},
        {"start": "0", "end": "30", "dailyAlways": "2", "label": "일"}
        ]

    if not user_time_list:
        result['availability'] = availability
        result['rentAlways'] = True
    else:
        result['rentAlways'] = False
        for idx, user_time in enumerate(user_time_list):
            availability[idx]['dailyAlways'] = str(user_time.availability)
            if user_time.start_time :
                availability[idx]['start'] = str(user_time.start_time)
            if user_time.end_time:
                availability[idx]['end'] = str(user_time.end_time)
        result['availability'] = availability
    return jsonify(result)


@carbooking_api_app.route('/api/add_time_availability', methods=["POST"])
@api_login_match
def add_time_availaibility():
    user_id = session['user_id']
    request_data = request.get_json()
    request_data = request_data if request_data is not None else {}
    form = AvailableForm(data=request_data)
    if request_data.get('availability'):
        for av in request_data['availability']:
            form.availability.append_entry(av)
    result={}

    if form.validate():
        user_time_list = UserTime.query.filter(UserTime.user_id==user_id).order_by(UserTime.dow).all()
        if form.rentAlways.data:
            if user_time_list:
                for user_time in user_time_list:
                    db.session.delete(user_time)
                db.session.commit()
            result['message'] = "success"
            return jsonify(result)
        if user_time_list:
            for idx, available in  enumerate(form.availability.data):
                user_time_list[idx].availability= available['dailyAlways']
                user_time_list[idx].start_time = available['start']
                user_time_list[idx].end_time = available['end']

        else:
            for idx, available in  enumerate(form.availability.data):
                utt = UserTime(
                    user_id = user_id,
                    dow=idx,
                    availability=available['dailyAlways'],
                    start_time = available['start'],
                    end_time = available['end'],
                )
                db.session.add(utt)
        db.session.commit()
        result['message'] = "success"
        return jsonify(result)

    else:
        abort(403, "not valid data")

@carbooking_api_app.route('/api/add_vacation_time', methods=["POST"])
@api_login_match
def add_vacation_time():
    user_id = session['user_id']
    request_data = request.get_json()
    request_data['user_id'] = user_id
    form = VacationForm(data=request_data)
    result={}
    if form.validate():
        vacation = VacationData(
            user_id = user_id,
            start_time = form.start_time.data,
            end_time = form.end_time.data,
        )
        db.session.add(vacation)
        db.session.commit()
        result['message'] = "success"
    else:
        result['message']="fail"
        error_list = []
        for field, errors in form.errors.items():
            for error in errors:
                error_list.append(error)
        result['error'] = error_list
    return jsonify(result)



@carbooking_api_app.route('/api/get_vacation_time')
@api_login_match
def get_vacation_time():
    user_id = session['user_id']
    vacation_list = VacationData\
                    .query\
                    .filter(VacationData.user_id==user_id)\
                    .filter(VacationData.end_time> dt.now())\
                    .all()
    result = []
    for vacation in vacation_list:
        result_dict={}
        result_dict['id'] = vacation.id
        result_dict['start_time'] = dt.strftime(vacation.start_time, "%Y-%m-%d %H:%M")
        result_dict['end_time'] = dt.strftime(vacation.end_time, "%Y-%m-%d %H:%M")
        result.append(result_dict)
    return jsonify(result)


# Requires: Vacataion Data should be presents.
# Modifies: VacationData
# Effects: delete one row in VacationDataTable
@carbooking_api_app.route('/api/delete_vacation_time', methods=["POST"])
@api_login_match
def delete_vacation_time():
    user_id = session['user_id']
    data = request.get_json()
    vacation_id = data['vacation_id']
    vacationData = VacationData.query.filter(VacationData.id ==vacation_id).filter(VacationData.user_id==user_id).first()
    result = {}
    if vacationData:
        db.session.delete(vacationData)
        db.session.commit()
        result['message'] = 'success'
    else:
        result['message'] = 'fail'
    return jsonify(result)

@carbooking_api_app.route('/api/verify_booking', methods=["POST"])
@cannot_confirm_own_car
def verify_booking():
    request_data = request.get_json()
    form = BookCheckingForm(data=request_data)
    result={}
    if form.validate():
        start_time = form.start_time.data
        end_time = form.end_time.data
        car_id = form.car_id.data
        car = CarDao.get_car_by_carid(car_id)
        result=BookingDao.check_booking_availability(car, start_time, end_time)
        return jsonify(result)
    else:
        result = convert_wtf_error(result,form)
    return jsonify(result)


@carbooking_api_app.route('/api/register_nice_card', methods=['POST'])
@api_login_match
@auth_required
def add_nice_card():
    user_id = session['user_id']
    data = request.get_json()
    form = NiceCardForm(data = data,csrf_enabled=False)
    result = {}

    if form.validate():
        card = UserCard.query.filter(UserCard.user_id ==user_id).first()
        if card:
            customer_uid = str(uuid.uuid4())
            old_customer_uid = card.customer_uid
            card_registered,message = register_card(
                birth=form.birth.data,
                password=form.password.data,
                expire_month=form.expire_month.data,
                expire_year=form.expire_year.data,
                card_number=form.card_1.data,
                customer_uid = customer_uid,
                user_id=user_id
                )
            if card_registered:
                response,message = delete_card(old_customer_uid)
                if response :
                    if response.status_code==200 and response.json().get('code')==0:
                        card.name = form.name.data
                        card.customer_uid = customer_uid
                        db.session.commit()
                        result['message'] = "success"
                        request._tracking_data = {
                            'user_id':user_id,
                             'action':"modify_card"
                             }
                        return jsonify(result)
                    else:
                        result['message'] = "fail"
                        result['error_message']="기존카드 삭제 실패"
                        return jsonify(result)
                else:
                    result['message'] = "fail"
                    result['error_message']="기존카드 삭제 실패"
                    return jsonify(result)

            else:
                result['message'] = "fail"
                result['error_message']=message
                return jsonify(result)

        else:
            customer_uid = str(uuid.uuid4())
            card_registered,message = register_card(
                birth=form.birth.data,
                password=form.password.data,
                expire_month=form.expire_month.data,
                expire_year=form.expire_year.data,
                card_number=form.card_1.data,
                customer_uid = customer_uid,
                user_id=user_id
            )
            if card_registered:
                card = UserCard(
                    name=form.name.data,
                    user_id = user_id,
                    customer_uid =customer_uid,
                    )
                db.session.add(card)
                db.session.commit()
                request._tracking_data = {
                    'user_id':user_id,
                     'action':"add_card"
                     }
                result['message'] = "success"
                return jsonify(result)
            else:
                result['message'] = "fail"
                result['error_message']=message
                return jsonify(result)

    else:
        result['message']="fail"
        error_list = []
        for field, errors in form.errors.items():
            for error in errors:
                error_list.append(error)
        result['error'] = error_list
    return jsonify(result)



@carbooking_api_app.route('/api/register_card', methods=['POST'])
@api_login_match
@auth_required
def add_card():
    user_id = session['user_id']
    data = request.get_json()
    form = CardNumberForm(data = data,csrf_enabled=False)
    result = {}

    if form.validate():
        card = UserCard.query.filter(UserCard.user_id ==user_id).first()
        if card:
            card.name = form.name.data
            card.customer_uid = form.customer_uid.data
            db.session.commit()
        else:
            card = UserCard(
                name=form.name.data,
                user_id = user_id,
                customer_uid =form.customer_uid.data,
                )
            db.session.add(card)
            db.session.commit()
        result['message'] = "success"

    else:
        result['message']="fail"
        error_list = []
        for field, errors in form.errors.items():
            for error in errors:
                error_list.append(error)
        result['error'] = error_list
    return jsonify(result)


@carbooking_api_app.route('/api/authorization_token',methods=["GET"])
@api_login_match
def get_token():
    user_id = session['user_id']
    token = encrypt_hash(str(user_id))
    result = {}
    result['message'] = "success"
    result['auth_token'] = token
    return jsonify(result)


@carbooking_api_app.route('/api/get_card_info', methods=['GET'])
@api_login_match
def get_card():
    user_id = session['user_id']
    data = request.get_json()
    result = {}
    card = UserCard.query.filter(UserCard.user_id == user_id).first()
    if card:
        result['message'] = "success"
        result['data'] = card.to_json

    else:
        result['message']="fail"
    return jsonify(result)

@carbooking_api_app.route('/api/get_booking_time_price', methods=['POST'])
@api_login_match
def get_booking_time_price():
    user_id = session['user_id']
    result = {}
    data = request.get_json()
    form = BookingForm(data=data)
    if form.validate():
        start_time = form.start_time.data
        end_time = form.end_time.data
        car_id = form.car_id.data
        result= CarDao.get_car_price_info(result,car_id,start_time,end_time)
        result['message']="success"
        return jsonify(result)

    else:
        result={}
        result['message']="fail"
        error_list = []
        for field, errors in form.errors.items():
            for error in errors:
                error_list.append(error)
        result['errorMessage'] = error_list[0]
        return jsonify(result)


@carbooking_api_app.route('/api/add_booking',methods=['POST'])
@api_login_match
@auth_required
@user_card_registered
def request_booking():
    user_id = session['user_id']
    data = request.get_json()
    form = BookingForm(data=data)
    if form.validate():
        start_time = form.start_time.data
        end_time = form.end_time.data
        car_id = form.car_id.data
        car = CarDao.get_car_by_carid(car_id)
        bdo = BookingDao()
        result = bdo.check_booking_availability(
            car,
            start_time,
            end_time
            )
        if result.get('message')=="success":
            trip_price = CarDao.get_car_price(car.id,start_time,end_time)
            total_distance = get_price(car.distance,start_time,end_time)
            #회사 수수료
            rent_fee = int(trip_price * 0.05)
            total_price = trip_price + rent_fee
            bdo.add_booking(car.id,user_id,total_price,0,trip_price,start_time,end_time,status=0,total_distance=total_distance)

            try:
                if not current_app.config.get('TESTING'):
                    owner_phone = car.user.phone
                    body = "새로운 Wi-CAR예약이 들어왔습니다. www.wicar.co.kr/notifications 에서 확인해주세요."
                    send_sms(owner_phone,body)
            except:
                pass

            return jsonify(result)

        else:
            result['error'] = "이미 다른고객님의 예약이 생겼습니다. 다른날짜를 선택해주세요."
            return jsonify(result)
    else:
        result={}
        result['message']="fail"
        error_list = []
        for field, errors in form.errors.items():
            for error in errors:
                error_list.append(error)
        result['error'] = error_list
        return jsonify(result)


@carbooking_api_app.route('/api/add_booking_img/<string:booking_id>', methods=['POST'])
@api_login_match
@verify_booking_matched
def add_booking_img(booking_id="",**kwargs):
    booking = kwargs['booking']
    car_id = booking.car_id
    file = request.files['image']
    description = request.form.get('description')
    user_id= session['user_id']
    user = User.query.filter(User.id==user_id).first()
    user_name= user.name
    image_loc = current_app.config['BOOKING_IMAGE_FOLDER']
    image_id = save_image(file,booking_id,'BOOKING_IMAGE_FOLDER',image_width=400,image_height=400)
    file.close()
    #이미지가 성공적으로 저장되었으면 DB에 url저장.
    message={}
    imageList = []
    bookingImage=BookingImage.query.filter(BookingImage.booking_id ==booking_id).filter(BookingImage.active==True).order_by(BookingImage.image_index.desc()).first()
    if image_id:
        message['message'] = 'success'
        if bookingImage:
            last_index = bookingImage.image_index
            new_image_index = last_index + 1
        else:
            new_image_index = 0
        bookingImage = BookingImage(
            booking_id = booking_id,
            sender_id = user_id,
            image = image_id,
            description=description,
            image_index = new_image_index,
            active = 1
        )
        db.session.add(bookingImage)
        db.session.commit()
        message['url'] = bookingImage.imgsrc
        message['image_index'] = new_image_index
        message['description'] = bookingImage.description
        message['sender_name'] = user_name
        message['sender_id'] = user_id
        message['car_id'] = car_id
        message['dateString'] = dt.strftime(bookingImage.register_date,"%Y년 %m월 %d일 %H:%M",)
    else:
        message['message'] = 'fail'
    return jsonify(message)



@carbooking_api_app.route('/api/get_booking_img/<string:booking_id>')
@api_login_match
@verify_booking_matched
def get_booking_img(booking_id="",**kwargs):
    data={}
    dataList = []
    booking = kwargs['booking']
    car_id = booking.car_id
    bookingImageList=BookingImage.query.filter(BookingImage.booking_id ==booking_id).filter(BookingImage.active==True).order_by(BookingImage.image_index).all()
    if bookingImageList:
        data['message'] = 'success'
        for bookingImage in bookingImageList:
            user = User.query.filter(User.id==bookingImage.sender_id).first()
            if user:
                message={}
                message['url'] = bookingImage.imgsrc
                message['image_index'] = bookingImage.image_index
                message['description'] = bookingImage.description
                message['sender_name'] = user.name
                message['sender_id'] = user.id
                message['car_id'] = car_id
                message['dateString'] = dt.strftime(bookingImage.register_date,"%Y년 %m월 %d일 %H:%M")
                dataList.append(message)
    else:
        data['message'] = 'fail'
    data['urlList'] = dataList
    return jsonify(data)


@carbooking_api_app.route('/api/add_carprice/<string:car_id>',methods=["POST"])
@car_owner_match
def add_car_price(car_id="",**kwargs):
    data = request.get_json()
    data['car_id'] = car_id
    form = CarPriceScheduleForm(data = data)
    vacation_list = CarPriceSchedule\
                        .query\
                        .filter(CarPriceSchedule.car_id == car_id)\
                        .filter(CarPriceSchedule.end_time > dt.now()).all()
    result={}
    if form.validate(vacation_list):
        start_time,end_time = convert_events_time(data)
        carPriceSchedule = CarPriceSchedule(
            car_id=car_id,
            start_time=start_time,
            end_time=end_time,
            price=form.price.data,
        )
        db.session.add(carPriceSchedule)
        db.session.commit()
        result['id'] = carPriceSchedule.id
        result['message'] = "success"
    else:
        result = convert_wtf_error(result,form)
    return jsonify(result)


@carbooking_api_app.route('/api/get_carprice_schedule/<string:car_id>',methods=["GET"])
@car_owner_match
def get_carprice_schedule(car_id="",**kwargs):
    return BookingDao.convert_schedule(CarPriceSchedule,car_id)


@carbooking_api_app.route('/api/update_carprice_schedule/<string:car_id>',methods=["POST"])
@car_owner_match
def update_carprice_schedule(car_id="",**kwargs):
    data = request.get_json()
    return BookingDao.update_carprice_schedule(car_id,data,CarPriceUpdateForm,CarPriceSchedule)

@carbooking_api_app.route('/api/add_car_vacation/<string:car_id>',methods=["POST"])
@car_owner_match
def add_car_vacation(car_id="",**kwargs):
    data = request.get_json()
    data['car_id'] = car_id
    form = VacationScheduleForm(data = data)
    vacation_list = CarVacation\
                        .query\
                        .filter(CarVacation.car_id == car_id)\
                        .filter(CarVacation.end_time > dt.now()).all()
    result={}
    if form.validate(vacation_list):
        start_time,end_time = convert_events_time(data)
        carVacation = CarVacation(
            car_id=car_id,
            start_time=start_time,
            end_time=end_time,
        )
        db.session.add(carVacation)
        db.session.commit()
        result['id'] = carVacation.id
        result['message'] = "success"
    else:
        result = convert_wtf_error(result,form)
    return jsonify(result)

@carbooking_api_app.route('/api/get_car_vacation/<string:car_id>',methods=["GET"])
@car_owner_match
def get_car_vacation(car_id="",**kwargs):
    return BookingDao.convert_schedule(CarVacation,car_id)


@carbooking_api_app.route('/api/update_car_vacation/<string:car_id>',methods=["POST"])
@car_owner_match
def update_car_vacation(car_id="",**kwargs):
    data = request.get_json()
    return BookingDao.update_carprice_schedule(car_id,data,CarVacationUpdateForm,CarVacation)
