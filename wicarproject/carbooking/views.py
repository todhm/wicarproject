from flask import Blueprint, render_template, session, make_response, request, flash, jsonify, redirect, url_for, send_from_directory, abort,current_app
from werkzeug.datastructures import MultiDict
from datetime import datetime as dt
from flask_wtf import FlaskForm,Form
from application import db, mdb
from caruser.forms import SearchForm
from carupload.models import CarImage, Car
from carbooking.forms import *
from carbooking.models import *
from utilities.geoutil import get_geo_address
from utilities.smsutil import send_sms,send_lms, send_payment_error
from utilities.timeutil import find_duplicate_time, daterange
from utilities.common import *
from utilities.errorutil import return_booking_error
from utilities.dao.cardao import CarDao
from utilities.dao.userdao import UserDao
from utilities.dao.bookingdao import BookingDao
from utilities.decorators import *
from utilities.hashutil import encrypt_hash,decrypt_hash
from utilities.flask_tracking.documents import Tracking
from mongoengine.queryset.visitor import Q
from datetime import datetime as dt
from datetime import timedelta
import json

carbooking_app = Blueprint('carbooking_app', __name__)

@carbooking_app.route('/car_search', methods=["GET", "POST"])
def car_search():
    form = SearchForm()
    start_date=""
    end_date=""
    if form.validate_on_submit():
        session['search_data'] = request.form
        return redirect(url_for('carbooking_app.car_search'))
    elif session.get('search_data'):
        form_data = session['search_data']
        start_date = session['search_data']['startDate']
        end_date = session['search_data']['endDate']
        form =SearchForm(**form_data)
    return render_template("carbooking/carsearch.html",
        form=form, start_date = start_date, end_date=end_date
        )

@carbooking_app.route('/car_info/<string:car_id>')
def car_info(car_id):
    return render_template("carbooking/carinfo.html")


@carbooking_app.route('/confirm_booking/<string:car_id>')
@registered_phone_required
def check_booking(car_id):
    return render_template("carbooking/carinfo.html")


@carbooking_app.route('/car_owner_setting')
@login_required
def car_owner_setting():
    return render_template("carbooking/dashboard.html")


@carbooking_app.route('/notifications')
@login_required
def get_notifications():
    #대기중인예약
    user_id = session['user_id']
    carList = Car.query.filter(Car.user_id==user_id).filter(Car.active==True).all()
    car_ids = [car.id for car in carList]
    bookingList = CarBooking.query.filter(CarBooking.car_id.in_(car_ids) ).filter(CarBooking.status==0).all()
    bookingList = BookingDao.iterate_notification_info(bookingList,True)
    userBookingList = CarBooking.query.filter(CarBooking.status==0).filter(CarBooking.renter_id==user_id).all()
    userBookingList = BookingDao.iterate_notification_info(userBookingList,False)
    bookingList.extend(userBookingList)

    #Log불러오기
    logList = Tracking.objects.filter(
        Q(__raw__ = {'custom_data.user_id' : user_id}) |
        Q(__raw__ = {'custom_data.owner_id' : user_id}) |
        Q(__raw__ = {'custom_data.renter_id' : user_id})|
        Q(__raw__ = {'custom_data.sender_id' : user_id})|
        Q(__raw__ = {'custom_data.receiver_id' : user_id})
        ).filter(
            Q(__raw__ = {'custom_data.action' : 'auto_cancel_booking'}) |
            Q(__raw__ = {'custom_data.action' : 'finish_booking'}) |
            Q(__raw__ = {'custom_data.action' : 'booking_confirm'})|
            Q(__raw__ = {'custom_data.action' : 'cancel_booking'})|
            Q(__raw__ = {'custom_data.action' : 'booking_disallow'})|
            Q(__raw__ = {'custom_data.action' : 'message'})
        )\
        .order_by('-date_created')
    return render_template("carbooking/notifications.html",bookingList = bookingList,logList = logList,user_id = user_id)



@carbooking_app.route('/reservation/<string:booking_id>',methods=['GET','POST'])
@login_required
@verify_booking_matched
def reservation_page(booking_id="",review_error="",message_error="",**kwargs):
    booking = kwargs['booking']
    review_error=request.args.get('review_error')
    message_error=request.args.get('message_error')
    is_car_owner = kwargs['is_car_owner']
    carimage = booking.car.carimage.filter(CarImage.image_index ==0).filter(CarImage.active==True).first()
    booking.imgsrc = carimage.imgsrc if carimage else None
    now_time = dt.now()
    time_difference = min(booking.register_date + timedelta(hours=12),booking.start_time) - now_time
    remaining_hours = (time_difference.days *24) + (time_difference.seconds / 3600)
    booking.remaining_time = round(remaining_hours)
    booking.mapurl = "http://maps.google.com/maps?q=" + booking.car.address
    original_status = booking.status
    owner = booking.car.user
    owner_phone = owner.phone
    owner_name = owner.name
    renter_name = booking.renter.name
    renter_phone = booking.renter.phone
    renter_img = booking.renter.imgsrc
    owner_img = booking.car.user.imgsrc
    error= None
    messageForm = MessageForm()
    reviewForm = ReviewForm()
    messageList = Message.query.filter(Message.booking_id ==booking_id).order_by(Message.register_date).all()
    if booking.status>0:
        bookingPhotoList = BookingImage.query.filter(BookingImage.active==True).filter(BookingImage.booking_id==booking_id).order_by(BookingImage.image_index).all()
    else:
        bookingPhotoList=[]
    if is_car_owner:
        booking_owner_24 = (booking.start_time - dt.now()).days <1
        confirmForm = ConfirmForm()
        endForm = OwnerCancelForm()
        booking.userimg = renter_img

        if confirmForm.validate_on_submit():
            userCard = UserCard.query.filter(UserCard.user_id==booking.renter_id).first()
            error = handle_confirm_booking(booking,userCard,owner,renter_name, error, renter_img,owner_name, owner_img,renter_phone,owner_phone)

        elif endForm.validate_on_submit():
            if original_status == 0:
                booking.status = -1
                if not current_app.config['TESTING']:
                    body = 'wicar 예약 취소. {}님이 예약을 거절하여 고객님의 예약이 취소되었습니다.'.format(owner_name)
                    send_sms(renter_phone,body)

                request._tracking_data = {
                    'user_id':owner.id,
                    'booking_id':booking.id,
                    'owner_id': owner.id,
                    'owner_name': owner_name,
                    'owner_img': owner_img,
                    'renter_id':booking.renter_id,
                    'renter_name':renter_name,
                    'renter_img': renter_img,
                    'total_price':booking.total_price,
                    'owner_earning':booking.owner_earning,
                    'status':booking.status,
                     'action':'booking_disallow'
                     }
                db.session.commit()

            elif original_status == 2 and booking_owner_24:
                error = handle_owner_cancel(
                    price=booking.total_price,
                    booking=booking,
                    error=error,
                    owner=owner,
                    owner_name=owner_name,
                    owner_phone=owner_phone,
                    renter_phone=renter_phone,
                    owner_img=owner_img,
                    renter_name=renter_name,
                    renter_img=renter_img,
                    now_time=now_time,
                    status=-8)

            elif original_status == 2 and not booking_owner_24:
                error = handle_owner_cancel(
                    price=booking.total_price,
                    booking=booking,
                    error=error,
                    owner=owner,
                    owner_name=owner_name,
                    owner_phone=owner_phone,
                    renter_phone=renter_phone,
                    owner_img=owner_img,
                    renter_name=renter_name,
                    renter_img=renter_img,
                    now_time=now_time,
                    status=-7)
        renter_review = RenterReview.query.filter(RenterReview.booking_id == booking_id).first()
        return render_template("carbooking/reservation.html",
            booking=booking,confirmForm=confirmForm,endForm=endForm,
            reviewForm=reviewForm,error=error,review_error=review_error,renter_review=renter_review,
            booking_owner_24 = booking_owner_24, messageForm = messageForm,messageList=messageList,message_error=message_error,
            bookingPhotoList=bookingPhotoList)

    else:
        userCancelForm = UserCancelForm()
        booking.userimg =owner_img
        cancel_level = get_cancellation_level(booking.register_date, booking.start_time)
        owner_review = OwnerReview.query.filter(OwnerReview.booking_id == booking_id).first()


        if userCancelForm.validate_on_submit():

            booking.status = cancel_level

            if original_status == 2:
                if cancel_level == -3:
                    error = handle_cancel_request(booking.total_price,booking,error,owner,owner_name,owner_phone,renter_phone,owner_img,renter_name,renter_img,now_time)
                elif cancel_level == -4:
                    error = handle_cancel_request(booking.owner_earning,booking,error,owner,owner_name,owner_phone,renter_phone,owner_img,renter_name,renter_img,now_time)
                elif cancel_level == -5:
                    cancel_price = int(0.9 * booking.owner_earning)
                    error = handle_cancel_request(cancel_price,booking,error,owner,owner_name,owner_phone,renter_phone,owner_img,renter_name,renter_img,now_time)
                elif cancel_level == -6:
                    error = handle_cancel_request(0,booking,error,owner,owner_name,owner_phone,renter_phone,owner_img,renter_name,renter_img,now_time)

            else:
                request._tracking_data = {
                    'user_id':booking.renter_id,
                    'booking_id':booking.id,
                    'owner_id':owner.id,
                    'owner_name':owner_name,
                    'owner_img':owner_img,
                    'renter_id':booking.renter_id,
                    'renter_img':renter_img,
                    'renter_name':renter_name,
                    'cancel_price':0,
                    'action':'cancel_booking',
                    'status':booking.status
                     }
                db.session.commit()
                if not  current_app.config['TESTING']:
                    body = "{} 고객님이 예약을 취소하였습니다.".format(renter_name)
                    send_sms(owner_phone,body)

        return render_template(
            "carbooking/reservation_renter.html",
            booking=booking,
            owner_review=owner_review,
            userCancelForm = userCancelForm,
            cancel_level = cancel_level,
            error=error,
            review_error=review_error,
            messageForm = messageForm,
            messageList = messageList,
            reviewForm=reviewForm,
            message_error=message_error,
            bookingPhotoList=bookingPhotoList
            )

@carbooking_app.route('/add_owner_review/<string:booking_id>',methods=['POST'])
@login_required
@verify_booking_matched
def add_owner_review(booking_id="",**kwargs):
    booking = kwargs['booking']
    owner_id = booking.car.user_id
    reviewForm = ReviewForm()
    owner_review = OwnerReview.query.filter(OwnerReview.booking_id == booking_id).first()
    review_validate =  reviewForm.validate()
    if review_validate and not owner_review:
        owner_review = OwnerReview(
            booking_id=booking_id,
            owner_id=owner_id,
            review_point=reviewForm.review_point.data,
            review=reviewForm.review.data
            )
        db.session.add(owner_review)
        db.session.commit()
        return redirect(url_for('carbooking_app.reservation_page',booking_id=booking_id))
    elif not review_validate:
        review_error = list(reviewForm.errors.items())[0][1][0]
        return redirect(url_for('carbooking_app.reservation_page',booking_id=booking_id,review_error=review_error))


@carbooking_app.route('/add_renter_review/<string:booking_id>',methods=['POST'])
@login_required
@verify_booking_matched
def add_renter_review(booking_id="",**kwargs):
    booking = kwargs['booking']
    renter_id = booking.renter_id
    reviewForm = ReviewForm()
    renter_review = RenterReview.query.filter(RenterReview.booking_id == booking_id).first()
    review_validate =  reviewForm.validate()
    if review_validate and not renter_review:
        renter_review = RenterReview(
            booking_id=booking_id,
            renter_id=renter_id,
            review_point=reviewForm.review_point.data,
            review=reviewForm.review.data
            )
        db.session.add(renter_review)
        db.session.commit()
        return redirect(url_for('carbooking_app.reservation_page',booking_id=booking_id))
    elif not review_validate:
        review_error = list(reviewForm.errors.items())[0][1][0]
        return redirect(url_for('carbooking_app.reservation_page',booking_id=booking_id,review_error=review_error))

@carbooking_app.route('/send_message/<string:booking_id>',methods=['POST'])
@login_required
@verify_booking_matched
def send_message(booking_id="",**kwargs):
    booking = kwargs['booking']
    messageForm=MessageForm()
    is_car_owner = kwargs['is_car_owner']
    now_time = dt.now()
    original_status = booking.status
    owner = booking.car.user
    owner_phone = owner.phone
    owner_name = owner.name
    renter_name = booking.renter.name
    renter_phone = booking.renter.phone
    renter_img = booking.renter.imgsrc
    owner_img = booking.car.user.imgsrc
    if is_car_owner:
        message_error = handle_message(messageForm=messageForm,booking=booking,
        sender_id=owner.id,receiver_id=booking.renter_id,receiver_phone=renter_phone,
        sender_name=owner_name, sender_img=owner_img,receiver_name=renter_name, now_time=now_time)

    else:
        #메세지를 보낸경우.
        message_error = handle_message(messageForm=messageForm,booking=booking,
            sender_id=booking.renter_id,receiver_id=owner.id, receiver_phone=owner_phone,
            sender_name=renter_name, sender_img=renter_img,receiver_name=owner_name,
             now_time=now_time)

    return redirect(url_for('carbooking_app.reservation_page',booking_id=booking_id,message_error=message_error))


@carbooking_app.route('/owner_review',methods=['GET'])
@login_required
def get_my_owner_review():
    ownerReviewList = OwnerReview\
        .query\
        .filter(OwnerReview.owner_id==session['user_id'])\
        .order_by(OwnerReview.register_date.desc()).all()
    return render_template('carbooking/owner_review.html',ownerReviewList=ownerReviewList)


@carbooking_app.route('/booking_photo/<string:booking_id>',methods=['GET',"POST"])
@login_required
@verify_booking_matched
def share_booking_photo(booking_id="",**kwargs):
    return render_template('carbooking/booking_photo.html')

@carbooking_app.route('/booking_history',methods=['GET'])
@login_required
def booking_history():
    user_id = session['user_id']
    carList = Car.query.filter(Car.user_id==user_id).filter(Car.active==True).all()
    car_ids = [car.id for car in carList]
    bookingOwnerList = CarBooking.query.filter(CarBooking.car_id.in_(car_ids) ).filter(CarBooking.status>=3).all()
    if bookingOwnerList:
        for booking in bookingOwnerList:
            carimage = booking.car.carimage.filter(CarImage.image_index ==0).filter(CarImage.active==True).first()
            booking.imgsrc = carimage.imgsrc if carimage else None
    bookingRenterList = CarBooking.query.filter(CarBooking.renter_id==user_id).filter(CarBooking.status>=3).all()
    if bookingRenterList:
        for booking in bookingRenterList:
            carimage = booking.car.carimage.filter(CarImage.image_index ==0).filter(CarImage.active==True).first()
            booking.imgsrc = carimage.imgsrc if carimage else None
    return render_template('carbooking/booking_history.html',bookingOwnerList=bookingOwnerList, bookingRenterList=bookingRenterList)
