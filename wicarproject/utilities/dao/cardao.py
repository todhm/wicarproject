from application import db
from carupload.models import Car,CarImage,CarOption
from carbooking.models import CarPriceSchedule
from datetime import datetime as dt
from utilities.timeutil import *
from utilities.imaging import save_image
from utilities.dao.bookingdao import BookingDao
from flask import current_app as app
from sqlalchemy import func
import json
import os


class CarDao(object):

    @classmethod
    def get_car_obj(self,user_id):
        car  = Car.query.filter(Car.user_id==user_id).order_by(Car.register_date.desc()).first()
        return car

    @classmethod
    def get_car_by_carid(self,car_id):
        car  = Car.query.filter(Car.id==car_id).first()
        return car

    @classmethod
    def update_carimage_filename(self):
        carImageList = CarImage.query.all()
        for carImage in carImageList:
            carImage.filename = carImage.originalImgSrc
            db.session.add(carImage)
        db.session.commit()
        return True



    @classmethod
    def update_image(self,car_id,image_index,image_id):
        carimage = db.session.query(CarImage)\
                    .filter_by(car_id=car_id)\
                    .filter_by(image_index=image_index)\
                    .filter_by(active=True)\
                    .first()
        carimage.image = image_id
        carimage.filename = "{}.{}.jpg".format(car_id,image_id)
        db.session.commit()
        return carimage

    @classmethod
    def get_active_car_obj(self,user_id):
        car  = Car.query.filter(Car.user_id==user_id).filter(Car.active==False).order_by(Car.register_date.desc()).first()
        return car

    @classmethod
    def update_all_non_indexed_image(self):
        carList = Car.query.all()
        for car in carList:
            imageList = car.carimage.order_by(CarImage.image).filter(CarImage.active==True).all()
            for idx, image in enumerate(imageList):
                image.image_index = idx
        db.session.commit()



    @classmethod
    def get_all_car(self):
        result = db.session.query(Car)\
                           .filter(Car.active==True)\
                           .filter(Car.cartype !='camping')\
                           .limit(100)
        result_lst = []
        for car in result:
            carImage = car.carimage\
                        .filter(CarImage.active==True)\
                        .filter(CarImage.image_index==0)\
                        .first()
            if car.caroption and carImage:
                car_obj = json.loads(car.caroption.json)
                car_obj['id'] = car.id
                car_obj['img']= carImage.imgsrc
                car_obj['address'] = car.address
                car_obj['year'] = car.year
                car_obj['car_type'] = car.cartype
                car_obj['distance'] = car.distance
                car_obj['brand'] = car.brand
                car_obj['class_name'] = car.class_name
                car_obj['model'] = car.model
                car_obj['transmission'] = car.transmission
                car_obj['distance_from_dest'] =False
                result_lst.append(car_obj)
        return result_lst


    @classmethod
    def get_searched_car(self,search_data,startDate=None,endDate=None,startTime=None,endTime=None):
        startDate = dt.strftime(dt.now()+ timedelta(days=1),"%m/%d/%Y") if startDate is None else startDate
        endDate = dt.strftime(dt.now() + timedelta(days=8),"%m/%d/%Y") if endDate is None else endDate
        startTime = "10:00" if startTime is None else startTime
        endTime = "10:00" if endTime is None else endTime
        startDateTime = dt.strptime(startDate + " " + startTime,"%m/%d/%Y %H:%M")
        endDateTime = dt.strptime(endDate + " " + endTime,"%m/%d/%Y %H:%M")

        loc_search = func.ll_to_earth(search_data['pointY'],search_data['pointX'])
        loc_car = func.ll_to_earth(Car.lat,Car.lng)
        distance_func = func.earth_distance(loc_search,loc_car)
        result = db.session.query(Car,distance_func)\
                           .order_by(distance_func)\
                           .filter(Car.active==True)\
                           .filter(Car.cartype !='camping')\
                           .limit(100)

        result_lst = []
        for car,distance in result:
            available_result = BookingDao.check_booking_availability(car,startDateTime,endDateTime)
            if available_result['message'] != "success":
                continue
            carImage = car.carimage\
                        .filter(CarImage.image_index==0)\
                        .filter(CarImage.active==True)\
                        .first()
            if car.caroption and carImage:
                car_obj = json.loads(car.caroption.json)
                car_obj['id'] = car.id
                car_obj['img']= carImage.imgsrc
                car_obj['address'] = car.address
                car_obj['year'] = car.year
                car_obj['distance'] = car.distance
                car_obj['car_type'] = car.cartype
                car_obj['brand'] = car.brand
                car_obj['class_name'] = car.class_name
                car_obj['price'] = self.get_median_car_price_without_discount(car_id=car.id,start_time=startDateTime,end_time=endDateTime)
                car_obj['model'] = car.model
                car_obj['transmission'] = car.transmission
                car_obj['distance_from_dest'] ="{0:.1f}".format(distance/1000)
                result_lst.append(car_obj)
        return result_lst


    @classmethod
    def add_car(
        self,user_id,address,detail_address,lat,lng,distance,brand,cartype,
        class_name,model,year,register_date=None,transmission="auto",
        active=0
        ):
        car = Car(
            user_id=user_id,
            address=address,
            detail_address=detail_address,
            lat=lat,
            lng=lng,
            distance=distance,
            year=year,
            brand=brand,
            cartype=cartype,
            class_name=class_name,
            model=model,
            active=active,
            transmission=transmission,
            register_date=register_date
            )
        db.session.add(car)
        db.session.commit()
        return car


    @classmethod
    def add_car_image(self,car_id,image_id,image_index,active=1):
        carImage = CarImage(
            car_id=car_id,
            image=image_id,
            image_index=image_index,
            active=active
        )
        db.session.add(carImage)
        db.session.commit()



    #start_time,end_time,car_id => give median car price
    @classmethod
    def get_car_price_without_discount(self,car_id,start_time,end_time):
        #특정 가격시간대가 존재하는경우.
        carPriceScheduleList =CarPriceSchedule\
                                .query\
                                .filter(CarPriceSchedule.car_id==car_id)\
                                .filter(CarPriceSchedule.end_time>=start_time)\
                                .filter(CarPriceSchedule.start_time<=end_time)\
                                .all()
        carOption = CarOption.query.filter(CarOption.id==car_id).first()
        total_price =0
        total_days=get_total_rental_days(start_time,end_time)
        for date in rental_range(start_time,total_days):
            event_start_time = date.replace(hour=0,minute=0,second=1)
            event_end_time = date.replace(hour=23,minute=59,second=0)
            duplicate_result = False
            for carPriceSchedule in carPriceScheduleList:
                duplicate = find_duplicate_time(event_start_time,event_end_time,carPriceSchedule.start_time,carPriceSchedule.end_time)
                if duplicate and not duplicate_result:
                    total_price += carPriceSchedule.price
                    duplicate_result = True
            if not duplicate_result:
                total_price += carOption.price
        return total_price

    #start_time,end_time,car_id => give median car price
    @classmethod
    def get_median_car_price_without_discount(self,car_id,start_time,end_time):
        #특정 가격시간대가 존재하는경우.
        total_price = self.get_car_price_without_discount(car_id,start_time,end_time)
        total_days=get_total_rental_days(start_time,end_time)
        return int(total_price/total_days)

    #start_time,end_time,car_id => give median car price
    @classmethod
    def get_median_car_price(self,car_id,start_time,end_time):
        total_price = self.get_car_price(car_id,start_time,end_time)
        total_days=get_total_rental_days(start_time,end_time)
        return int(total_price/total_days)


    #start_time,end_time,car_id => give median car price
    @classmethod
    def get_car_price(self,car_id,start_time,end_time):
        total_price = self.get_car_price_without_discount(car_id,start_time,end_time)
        total_days=get_total_rental_days(start_time,end_time)
        carOption = CarOption.query.filter(CarOption.id==car_id).first()
        if total_days >= 7 and total_days<30:
            if carOption.weekly_discount:
                total_price = total_price * ((100-carOption.weekly_discount) / 100.0)
                total_price = int(total_price)
        elif total_days >=30:
            if carOption.monthly_discount:
                total_price = total_price * ((100-carOption.monthly_discount) / 100.0)
                total_price = int(total_price)
        return total_price


    #start_time,end_time,car_id => give median car price
    @classmethod
    def get_car_price_info(self,result,car_id,start_time,end_time):
        total_days=get_total_rental_days(start_time,end_time)
        total_price = self.get_car_price_without_discount(car_id,start_time,end_time)
        result['dailyPrice'] =  int(total_price/total_days)
        result['totalDays'] = total_days
        result['tripPriceWithoutDiscount'] =  total_price
        carOption = CarOption.query.filter(CarOption.id==car_id).first()
        if total_days >= 7 and total_days<30:
            if carOption.weekly_discount:
                result['weeklyDiscount'] = carOption.weeklyDiscount
                total_price = total_price * ((100-carOption.weekly_discount) / 100.0)
                total_price = int(total_price)
        elif total_days >=30:
            if carOption.monthly_discount:
                result['monthlyDiscount'] = carOption.monthlyDiscount
                total_price = total_price * ((100-carOption.monthly_discount) / 100.0)
                total_price = int(total_price)
        result['totalTripPrice'] = total_price
        result['wicarFee'] = int(total_price * 0.05)
        return result

    @classmethod
    def add_longterm_sale(self,car_id,weekly_discount=0,monthly_discount=0):
        carOption = CarOption.query.filter(CarOption.id==car_id).first()
        carOption.weekly_discount=weekly_discount
        carOption.monthly_discount=monthly_discount
        db.session.commit()
        return carOption

    @classmethod
    def add_car_option(self,car_id,data):
        carOption = CarOption()
        carOption.id = car_id
        carOption.advance_notice = data.get('advance_notice')
        carOption.price = data.get('price')
        carOption.plate_num = data.get('plate_num')
        carOption.description = data.get('description')
        carOption.roof_box = data.get('roof_box')
        carOption.hid = data.get('hid')
        carOption.led = data.get('led')
        carOption.auto_trunk = data.get('auto_trunk')
        carOption.leather_seater = data.get('leather_seater')
        carOption.room_mirror = data.get('room_mirror')
        carOption.seat_6_4 = data.get('seat_6_4')
        carOption.seat_heater_1st = data.get('seat_heater_1st')
        carOption.seat_heater_2nd = data.get('seat_heater_2nd')
        carOption.seat_cooler = data.get('seat_cooler')
        carOption.high_pass = data.get('high_pass')
        carOption.button_starter = data.get('button_starter')
        carOption.handle_heater = data.get('handle_heater')
        carOption.premium_audio = data.get('premium_audio')
        carOption.hud = data.get('hud')
        carOption.smart_cruz_control = data.get('smart_cruz_control')
        carOption.tpms = data.get('tpms')
        carOption.curtton_airbag = data.get('curtton_airbag')
        carOption.esp = data.get('esp')
        carOption.isofix = data.get('isofix')
        carOption.slope_sleepery = data.get('slope_sleepery')
        carOption.front_collusion = data.get('front_collusion')
        carOption.lane_alarm = data.get('lane_alarm')
        carOption.high_bim = data.get('high_bim')
        carOption.aux_bluetooth = data.get('aux_bluetooth')
        carOption.usb = data.get('usb')
        carOption.auto_head_light = data.get('auto_head_light')
        carOption.android_conn = data.get('android_conn')
        carOption.apple_conn = data.get('apple_conn')
        carOption.electric_brake = data.get('electric_brake')
        carOption.navigation = data.get('navigation')
        carOption.backword_cam = data.get('backword_cam')
        carOption.surround_view_cam = data.get('surround_view_cam')
        carOption.bolt_220 = data.get('bolt_220')
        carOption.smartphone_charge = data.get('smartphone_charge')
        db.session.add(carOption)
        db.session.commit()
