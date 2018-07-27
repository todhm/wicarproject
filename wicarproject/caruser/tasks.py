from datetime import datetime as dt
from datetime import timedelta
from application import celery,db
from carbooking.models import CarBooking, OwnerSend, OwnerReview
from carupload.models import Car, CarImage
from caruser.models import UserBank
from caruser.mongomodels import BestCar
from utilities.smsutil import send_sms, send_lms
from utilities.dao.userdao import UserDao
from utilities.flask_tracking.documents import Tracking
from utilities.common import get_bank_token,get_count
from utilities.imaging import check_img_exists
from sqlalchemy import cast, func, desc,and_
from flask import request, current_app as app
import json
import requests



@celery.task(bind=True)
def get_best_cars_celery(self):
    get_best_cars()

def get_best_cars():

    carList = db.session.query(
        Car,
        func.avg(OwnerReview.review_point).label('review_point')
        )\
        .outerjoin(CarBooking)\
        .outerjoin(OwnerReview)\
        .filter(Car.active==True)\
        .group_by(Car.id)\
        .order_by(desc(func.avg(OwnerReview.review_point)))\
        .limit(20)\
        .all()

    car_data = []
    for car,average_point in carList:
        data = {}
        carimg = car.carimage.filter(CarImage.active==True).filter(CarImage.image_index==0).first()
        if not carimg:
            continue
        else:
            imgsrc = carimg.imgsrc
            image_exists = check_img_exists(carimg.filename)
            if not image_exists:
                continue
            data['id'] = car.id
            data['is_sale'] = False
            data['brand'] = car.brand
            data['class_name'] = car.class_name
            data['price'] = car.caroption.price
            data['review_point'] = average_point if average_point else 0
            booking_count = get_count(CarBooking,and_(
                CarBooking.car_id == car.id,
                CarBooking.status>=3
                ))
            data['bookingCount'] = booking_count
            data['img'] = carimg.imgsrc
            car_data.append(data)
    car_data = sorted(car_data, key = lambda x: (x['review_point']*(-1), x['bookingCount']*(-1)))
    bestCar = BestCar(car_list = car_data)
    bestCar.save()
