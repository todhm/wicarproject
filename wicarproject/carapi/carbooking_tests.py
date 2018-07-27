import os
import unittest
import sqlalchemy
from flask import Flask,session,url_for,redirect
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import desc
from application import create_app ,db
import unittest
import json
from caruser.models import User
from carupload.models import CarOption,Car,CarImage
from carbooking.models import *
from utilities.dao.userdao import UserDao
from utilities.dao.bookingdao import BookingDao
from utilities.dao.cardao import CarDao
from utilities.testutil import TestUtil
from utilities.timeutil import get_next_week_by_day
from utilities.common import get_price,register_card,delete_card
from utilities.hashutil import encrypt_hash,decrypt_hash
from utilities.flask_tracking.documents import Tracking
from utilities.imaging import check_img_exists,save_image
from mongoengine.queryset.visitor import Q
from freezegun import freeze_time
from datetime import datetime as dt
from datetime import timedelta
from settings import TEST_DB_URI
import urllib
import re
import uuid



class CarBookingApiTest(TestUtil):
    def setUp(self):
        super().setUp()
        start_time = dt.now() + timedelta(days=1)
        self.start_time = start_time.replace(hour=10,minute=0,second=0)
        end_time = dt.now() + timedelta(days=3)
        self.end_time = end_time.replace(hour=10,minute=0,second=0)
        self.start_date = dt.strftime(self.start_time,"%m/%d/%Y")
        self.end_date = dt.strftime(self.end_time,"%m/%d/%Y")
        self.startTime =  dt.strftime(self.start_time,"%H:%M")
        self.endTime =  dt.strftime(self.end_time,"%H:%M")
        self.address=  '평촌대로40번길 100'

        self.original_start_time = dt.now() + timedelta(days=1)
        self.original_end_time = dt.now() + timedelta(days=4)
        self.vacation_start_time =  dt.strftime(self.original_start_time,"%Y-%m-%d %H:%M")
        self.vacation_end_time = dt.strftime(self.original_end_time,"%Y-%m-%d %H:%M")

        #Interval이 겹치지 않게 start_time 과 end_time의 2배 만큼의 시간을 더함.
        time_diff = self.original_end_time - self.original_start_time
        self.new_start_time = self.original_start_time + (2*time_diff)
        self.new_end_time = self.original_end_time + (2*time_diff)
        self.time_diff = time_diff
        self.new_start_timestr =  dt.strftime(self.new_start_time,"%Y-%m-%d %H:%M")
        self.new_end_timestr = dt.strftime(self.new_end_time,"%Y-%m-%d %H:%M")

        TEST_UPLOADED_FOLDER='/static/images/test_images'
        self.test_image="."+TEST_UPLOADED_FOLDER + "/background.jpg"
        self.test_invalid_img = '.' + TEST_UPLOADED_FOLDER + "/invalidpdf.pdf"
    def add_random_booking(self,car,user,start_time = None,end_time=None):
        start_time = start_time if start_time is not None else self.original_start_time
        end_time = end_time if end_time is not None else self.original_end_time
        booking = BookingDao.add_booking(
                               car.id,
                               user.id,
                               10000,
                               1000,
                               5000,
                               start_time,
                               end_time,
                               0,
                               10000
                               )
        return booking
    def check_carbooking_img(self,data,carbooking_image,car,user):
        self.assertTrue(data['url']==carbooking_image.imgsrc)
        self.assertTrue(data['sender_id']==carbooking_image.sender_id)
        self.assertTrue(data['description']==carbooking_image.description)
        self.assertTrue(data['car_id']==car.id)
        self.assertTrue(data['sender_name']==user.name)
        self.assertTrue(data['dateString']==dt.strftime(carbooking_image.register_date,"%Y년 %m월 %d일 %H:%M"))
        self.assertTrue(data['image_index']==carbooking_image.image_index)

    def verify_valid_booking_check(self,car,start_timestr,end_timestr):
        rv = self.client.post(
                "/api/verify_booking",
                data = json.dumps(dict(
                    start_time = start_timestr,
                    end_time = end_timestr,
                    car_id = car.id
                )),
                content_type='application/json'
                )
        data = json.loads(rv.get_data().decode('utf-8'))
        self.assertTrue(data['message']=="success")


    def verify_unvalid_booking_check(self,car,start_timestr,end_timestr):
        rv = self.client.post(
                "/api/verify_booking",
                data = json.dumps(dict(
                    start_time = start_timestr,
                    end_time = end_timestr,
                    car_id = car.id
                )),
                content_type='application/json'
                )
        data = json.loads(rv.get_data().decode('utf-8'))
        self.assertTrue(data['message']=="fail")

    def get_booked_owner(self,owneremail='todhm@naver.com',renteremail='gmlaud14@nate.com',start_time=None,end_time=None):
        booking,renter = self.get_booked_renter(owneremail,renteremail,start_time=start_time,end_time=end_time)
        self.client.get('/logout')
        self.login_user(email=owneremail)
        owner = UserDao.get_user_obj(owneremail)
        return booking, owner, renter

    def get_booked_renter(self,owneremail='todhm@naver.com',renteremail='gmlaud14@nate.com',start_time=None,end_time=None):
        car,user = self.return_user_and_car(owneremail=owneremail, renteremail = renteremail)
        user_id = user.id
        self.add_card_info(user_id)
        booking = self.add_random_booking(car,user,start_time=start_time,end_time=end_time)
        return booking,user

    def add_fake_img(self,car):
        carimage = CarImage(
            car_id=car.id,
            image = 1111111,
            image_index = 0,
            active = 1
        )
        db.session.add(carimage)
        db.session.commit()
        return carimage

    def test_one_car_search(self):
        self.activate_car_with_address(self.address)
        self.search_car(self.address)
        rv = self.client.get("/api/get_car_list")
        car_list = json.loads(rv.get_data().decode('utf-8'))
        car_obj = car_list[0]
        self.assertTrue(self.address in car_obj['address'])
        self.assertTrue(int(car_obj['distance_from_dest'].split('.')[0])<1000)

    #시간이 겹치지 않는차는 가져온다.
    def test_search_car_nonduplicate(self):
        address='평촌대로40번길 100'
        search_start_time = dt.now() + timedelta(days=10)
        search_start_time = search_start_time.replace(minute=0)
        search_end_time = dt.now() + timedelta(days=13)
        search_start_time = search_end_time.replace(minute=0)
        start_time = dt.now() + timedelta(days=3)
        end_time = dt.now() + timedelta(days=6)
        start_date = dt.strftime(search_start_time,"%m/%d/%Y")
        end_date = dt.strftime(search_end_time,"%m/%d/%Y")
        startTime =  dt.strftime(search_start_time,"%H:%M")
        endTime =  dt.strftime(search_end_time,"%H:%M")
        booking1,user1,car = self.get_booked_car(
            start_time=start_time,end_time=end_time
            )
        self.add_fake_img(car)
        self.search_car(
            address,startDate=start_date,endDate=end_date,startTime=startTime,
            endTime=endTime
            )

        rv = self.client.get("/api/get_car_list")
        car_list = json.loads(rv.get_data().decode('utf-8'))
        self.assertTrue(len(car_list)==1)
        self.assertTrue(address in car_list[0]['address'])


    #시간이 겹치는 차는 가져오지 않는다.
    def test_search_car_duplicatetime(self):
        address='평촌대로40번길 100'
        booking1,user1,car = self.get_booked_car(start_time=self.start_time,end_time=self.end_time)
        self.search_car(address,startDate=self.start_date,endDate=self.end_date,startTime=self.startTime,endTime=self.endTime)
        rv = self.client.get("/api/get_car_list")
        car_list = json.loads(rv.get_data().decode('utf-8'))
        self.assertTrue(len(car_list)==0)

    #시간이 겹치는 차는 가져오지 않는다.
    def test_carsearch_with_car_vacation(self):
        booking1,user1,car = self.get_booked_car(start_time=self.start_time,end_time=self.end_time)
        BookingDao.add_car_vacation(car_id=car.id,start_time=self.start_time,end_time=self.end_time)
        self.search_car(self.address,startDate=self.start_date,endDate=self.end_date,startTime=self.startTime,endTime=self.endTime)
        rv = self.client.get("/api/get_car_list")
        car_list = json.loads(rv.get_data().decode('utf-8'))
        self.assertTrue(len(car_list)==0)

    #특정가격이 변경된경우!
    def test_carsearch_with_change_price(self):
        car = self.activate_car_without_img()
        self.add_fake_img(car)
        BookingDao.add_car_price_schedule(car_id=car.id,price=44000,start_time=self.start_time,end_time=self.end_time)
        self.search_car(self.address,startDate=self.start_date,endDate=self.end_date,startTime=self.startTime,endTime=self.endTime)
        rv = self.client.get("/api/get_car_list")
        car_list = json.loads(rv.get_data().decode('utf-8'))
        print(car_list[0]['price'])
        self.assertTrue(car_list[0]['price']==44000)

    def test_car_without_img(self):
        self.activate_car_without_img()
        rv = self.client.get("/api/get_car_list")
        car_list = json.loads(rv.get_data().decode('utf-8'))
        self.assertTrue(len(car_list)==0)


    def test_three_address_in_order(self):
        address_list = ['상암동','평촌대로40번길 100','해운대']
        for address in address_list:
            self.activate_car_with_address(address)
        self.search_car('평촌대로40번길 100')
        rv = self.client.get("/api/get_car_list")
        car_list = json.loads(rv.get_data().decode('utf-8'))
        self.assertTrue(len(car_list) == len(address_list))
        self.assertTrue( address_list[1] in car_list[0]['address'])
        self.assertTrue( address_list[0] in car_list[1]['address'])
        self.assertTrue( address_list[2] in car_list[2]['address'])



    def test_get_car_info(self):
        car = self.activate_car_without_img()
        rv = self.client.get("/api/get_car_for_booking/"+str(car.id))
        return_obj = json.loads(rv.get_data().decode('utf-8'))
        self.assertTrue(isinstance(return_obj['year'],int))
        self.assertTrue(isinstance(return_obj['username'],str))
        self.assertTrue(isinstance(return_obj['caroption']['description'],str))
        self.assertTrue(isinstance(return_obj['brand'],str))
        self.assertTrue(isinstance(return_obj['class_name'],str))
        self.assertTrue(isinstance(return_obj['model'],str))
        self.assertTrue(isinstance(return_obj['year'],int))
        self.assertTrue(isinstance(return_obj['reviewRate'],float))
        self.assertTrue(return_obj['totalBookingCount'] ==0)

    def test_get_car_info_after_search(self):
        car = self.activate_car_without_img()
        self.add_fake_img(car)
        self.search_car(self.address,startDate=self.start_date,endDate=self.end_date,startTime=self.startTime,endTime=self.endTime)
        rv = self.client.get("/api/get_car_for_booking/"+str(car.id))
        return_obj = json.loads(rv.get_data().decode('utf-8'))
        self.assertTrue(return_obj['bookingStartTime'] ==self.start_date + " "+self.startTime)
        self.assertTrue(return_obj['bookingEndTime'] ==self.end_date + " "+self.endTime)

    def test_get_car_info_withreview(self):
         booking,user,car = self.get_booked_car()
         booking.status=3
         db.session.commit()
         review = OwnerReview(
             owner_id= car.user.id,
             booking_id=booking.id,
             review_point=4,
             review="암낫그레잇"
         )
         db.session.add(review)
         db.session.commit()
         ownerReviewList = OwnerReview\
             .query\
             .filter(OwnerReview.owner_id==car.user.id)\
             .order_by(OwnerReview.register_date.desc()).all()
         rv = self.client.get('/api/get_car_for_booking/' + str(car.id))
         return_obj = json.loads(rv.get_data().decode('utf-8'))
         self.assertEqual(return_obj['totalBookingCount'] , 1)
         self.assertTrue(len(return_obj['reviewList']) == 1)
         self.assertTrue(return_obj['reviewRate'] == 4)



    def test_get_car_info_with_multiplereview(self):
        start_time = dt.now()
        end_time = dt.now() + timedelta(hours=3)
        booking1,user,car = self.get_booked_car()
        booking2 = self.add_random_booking(car,user,start_time=start_time,end_time=end_time)
        booking3 = self.add_random_booking(car,user,start_time=start_time,end_time=end_time)
        booking4 = self.add_random_booking(car,user,start_time=start_time,end_time=end_time)
        booking1.status=3
        booking2.status=3
        booking3.status=3
        booking4.status=3
        db.session.commit()
        review1 = OwnerReview(
            owner_id= car.user.id,
            booking_id= booking1.id,
            review_point=5,
            review="암낫그레잇"
        )
        review2 = OwnerReview(
            owner_id= car.user.id,
            booking_id=booking2.id,
            review_point=3,
            review="암낫그레잇"
        )
        review3 = OwnerReview(
            owner_id= car.user.id,
            booking_id=booking3.id,
            review_point=2.5,
            review="암낫그레잇"
        )
        review4 = OwnerReview(
            owner_id= car.user.id,
            booking_id=booking4.id,
            review_point=3.5,
            review="암낫그레잇"
        )
        db.session.add(review1)
        db.session.add(review2)
        db.session.add(review3)
        db.session.add(review4)
        db.session.commit()
        rv = self.client.get('/api/get_car_for_booking/' + str(car.id))
        return_obj = json.loads(rv.get_data().decode('utf-8'))
        self.assertEqual(return_obj['totalBookingCount'], 4)
        self.assertEqual(len(return_obj['reviewList']), 4)
        self.assertEqual(return_obj['reviewRate'], 3.5)






    def test_get_unregister_info(self):
        car = self.activate_car_without_img()
        rv = self.client.get("/api/get_car_for_booking/"+str(2))
        self.assertTrue(rv.status_code ==403)

    #add available time without log in
    def test_add_available_time(self):
        rv = self.client.post('/api/add_time_availability')
        self.assertTrue(rv.status_code==403)

    #add avaialble time with all available
    def test_rentAlways_available_time(self):
        user = self.register_user_with_phone(email='todhm@nate.com')
        test_request = dict(rentAlways=True)
        rv = self.client.post(
            '/api/add_time_availability',
            data = json.dumps(test_request),
            content_type='application/json'
        )
        self.assertTrue(rv.status_code==200)
        user_time_table = UserTime.query.filter(UserTime.user_id==user.id).all()
        self.assertTrue(len(user_time_table)==0)



    #add available time with all available
    def test_all_day_available_time(self):
        user = self.register_user_with_phone(email='todhm@nate.com')
        rv = self.client.post('/api/add_time_availability',
            data = json.dumps(dict(
                rentAlways=False,
                availability=[ {"dailyAlways":2} for i in range(7)]
            )),
            content_type='application/json'
            )
        self.assertTrue(rv.status_code==200)
        user_time_table = UserTime.query.filter(UserTime.user_id==user.id).all()
        for user in user_time_table:
            self.assertTrue(user.availability==2)



    #change to rentAlways status after register user time table with false rentAlways value.
    def test_change_to_rent_always_after_not(self):
        user = self.register_user_with_phone(email='todhm@nate.com')
        rv = self.client.post('/api/add_time_availability',
            data = json.dumps(dict(
                rentAlways=False,
                availability=[ {"dailyAlways":"2"} for i in range(7)]
            )),
            content_type='application/json'
            )
        self.assertTrue(rv.status_code==200)
        user_time_table = UserTime.query.filter(UserTime.user_id==user.id).all()
        for user_t in user_time_table:
            self.assertTrue(user_t.availability==2)
        rv = self.client.post('/api/add_time_availability',
            data = json.dumps(dict(
                rentAlways=True
            )),
            content_type='application/json'
            )
        user_time_table = UserTime.query.filter(UserTime.user_id==user.id).all()
        self.assertTrue(len(user_time_table)==0)

    #test data with never available.
    def test_never_available_data(self):
        user = self.register_user_with_phone(email='todhm@nate.com')
        rv = self.client.post('/api/add_time_availability',
            data = json.dumps(dict(
            rentAlways=False,
            availability=[ {"dailyAlways":"0"} for i in range(7)]
        )),
        content_type='application/json')
        self.assertTrue(rv.status_code==200)
        user_time_table = UserTime.query.filter(UserTime.user_id==user.id).all()
        self.assertTrue(len(user_time_table)==7)
        for user in user_time_table:
            self.assertTrue(user.availability==0)

    #test data with mixed value.
    def test_mixed_available_data(self):
        user = self.register_user_with_phone(email='todhm@nate.com')
        availability = self.get_random_valid_availability()
        rv = self.client.post('/api/add_time_availability',
            data = json.dumps(dict(
            rentAlways=False,
            availability=availability
            )),
            content_type='application/json'
        )
        self.check_random_valid_availability(rv,user)

    #test data where start time bigger than end time
    def test_start_time_greater(self):
        user = self.register_user_with_phone(email='todhm@nate.com')
        availability=[ {"dailyAlways":"0"} for i in range(7)]
        availability[1] = {'dailyAlways':"1","start":"30","end":"0"}
        rv = self.client.post('/api/add_time_availability',
            data = json.dumps(dict(
            rentAlways=False,
            availability=availability
        )),
        content_type='application/json')
        self.assertTrue(rv.status_code==403)
        user_time_table = UserTime.query.filter(UserTime.user_id==user.id).order_by(UserTime.dow).all()
        self.assertTrue(len(user_time_table)==0)


    def test_update_query_result(self):
        user = self.register_user_with_phone(email='todhm@nate.com')
        availability=[ {"dailyAlways":"0"} for i in range(7)]
        rv = self.client.post('/api/add_time_availability',
            data = json.dumps(dict(
            rentAlways=False,
            availability=availability
        )),
        content_type='application/json')

        availability = self.get_random_valid_availability()
        rv = self.client.post('/api/add_time_availability',
            data = json.dumps(dict(
            rentAlways=False,
            availability=availability
            )),
            content_type='application/json'
        )
        self.check_random_valid_availability(rv,user)

    def test_get_availability(self):
        user = self.register_user_with_phone(email='todhm@nate.com')
        availability = self.get_all_day_custom_availability()
        rv = self.client.post('/api/add_time_availability',
            data = json.dumps(dict(
            rentAlways=False,
            availability=availability
            )),
            content_type='application/json'
        )
        rv = self.client.get('/api/get_time_availability')
        data = json.loads(rv.get_data().decode('utf-8'))
        for i in range(7):
            self.assertTrue(data['availability'][i]['start'] == availability[i]['start'])
            self.assertTrue(data['availability'][i]['end'] == availability[i]['end'])
            self.assertTrue(data['availability'][i]['dailyAlways'] == availability[i]['dailyAlways'])


    def test_add_valid_vacation(self):
        user = self.register_user_with_phone(email='todhm@nate.com')
        rv = self.client.post('/api/add_vacation_time',
            data = json.dumps(dict(
                start_time = self.vacation_start_time,
                end_time = self.vacation_end_time

            )),
            content_type='application/json')
        self.assertTrue(rv.status_code==200)
        vacation = VacationData.query.filter(VacationData.user_id ==user.id).first()
        self.assertEquals(self.vacation_start_time,vacation.start_time_fmt)
        self.assertEquals(self.vacation_end_time,vacation.end_time_fmt)


        rv = self.client.post('/api/add_vacation_time',
            data = json.dumps(dict(
                start_time = dt.strftime(self.new_start_time,"%Y-%m-%d %H:%M"),
                end_time = dt.strftime(self.new_end_time,"%Y-%m-%d %H:%M")

            )),
            content_type='application/json')
        vacation = VacationData.query.filter(VacationData.user_id ==user.id).order_by(desc(VacationData.start_time)).first()
        self.assertEquals( dt.strftime(self.new_start_time,"%Y-%m-%d %H:%M"),vacation.start_time_fmt)
        self.assertEquals(dt.strftime(self.new_end_time,"%Y-%m-%d %H:%M"),vacation.end_time_fmt)


    def test_add_duplicate_vacation(self):
        user = self.register_user_with_phone(email='todhm@nate.com')
        rv = self.client.post('/api/add_vacation_time',
            data = json.dumps(dict(
                start_time = self.vacation_start_time,
                end_time = self.vacation_end_time

            )),
            content_type='application/json')
        rv = self.client.post('/api/add_vacation_time',
            data = json.dumps(dict(
                start_time = self.vacation_start_time,
                end_time = self.vacation_end_time

            )),
            content_type='application/json')
        self.assertTrue(rv.status_code==200)
        result = json.loads(rv.get_data().decode('utf-8'))
        self.assertTrue(result['message']=="fail")

    def test_delete_vacation(self):
        user = self.register_user_with_phone(email='todhm@nate.com')
        rv = self.client.post('/api/add_vacation_time',
            data = json.dumps(dict(
                start_time = self.vacation_start_time,
                end_time = self.vacation_end_time
            )),
            content_type='application/json')
        vacation = VacationData.query.filter(VacationData.user_id ==user.id).first()
        self.client.post('/api/delete_vacation_time',
        data = json.dumps(dict(
            vacation_id = vacation.id
        )),
        content_type='application/json'
        )
        vacation = VacationData.query.filter(VacationData.user_id ==user.id).first()
        data = json.loads(rv.get_data().decode('utf-8'))
        self.assertTrue(vacation is None)
        self.assertTrue(data['message']=="success")



    #사전알림 시간때문에 예약을 진행할수 없는경우.
    def test_check_unvalid_due_to_advance_notice(self):
        car = self.activate_car_without_img(advance_notice=10,email="todhm@naver.com")
        self.client.get('/logout')
        user = self.register_user_with_phone(email='gmlaud14@nate.com')
        self.add_random_booking(car=car, user=user)
        new_start_timestr = dt.strftime(dt.now(),"%Y-%m-%d %H:%M")
        new_end_timestr = dt.strftime(dt.now()+timedelta(days=2),"%Y-%m-%d %H:%M")
        self.verify_unvalid_booking_check(car,new_start_timestr, new_end_timestr)


    # VacationTable때문에 예약을 진행할 수 없는경우.
    def test_check_unvalid_due_to_vacation(self):
        car = self.activate_car_without_img()
        BookingDao.add_vacation_time(
            car.user_id,
            self.vacation_start_time,
            self.vacation_end_time
            )
        self.client.get('/logout')
        user = self.register_user_with_phone(email='gmlaud14@nate.com')
        self.verify_unvalid_booking_check(
            car,
            self.vacation_start_time,
            self.vacation_end_time
            )

    #VacationTable이 있어도 휴가가 겹치지 않아서 예약을 진행할 수 있는경우.
    def test_check_valid_due_to_vacation(self):
        car = self.activate_car_without_img()
        BookingDao.add_vacation_time(car.user_id,self.vacation_start_time,self.vacation_end_time)
        self.client.get('/logout')
        user = self.register_user_with_phone(email='gmlaud14@nate.com')
        self.verify_valid_booking_check(car,self.new_start_timestr,self.new_end_timestr)


    #UserTime Table이 모든날이 상시가능이라  에약을 진행할 수 있는 경우.
    def test_check_valid_due_to_usertime(self):
        car = self.activate_car_without_img()
        availability=[ {"dailyAlways":"2","start":"0","end":"90"} for i in range(7)]
        BookingDao.add_availability(car.user_id, availability)
        self.client.get('/logout')
        user = self.register_user_with_phone(email='gmlaud14@nate.com')
        self.verify_valid_booking_check(car,self.vacation_start_time,self.vacation_end_time)

    #UserrTime Table의 모든날이 상시불가능이라 예약을 진행할 수 없는경우.
    def test_check_invalid_due_to_usertime(self):
        car = self.activate_car_without_img()
        availability=[ {"dailyAlways":"0","start":"0","end":"90"} for i in range(7)]
        BookingDao.add_availability(car.user_id, availability)
        self.verify_unvalid_booking_check(car,self.vacation_start_time,self.vacation_end_time)


    #UserTimeTable의 시간이 car owner가 불가능한 요일에 설정된경우.
    def test_check_unvalid_due_to_usertime_daily_custom(self):
        car = self.activate_car_without_img()
        availability=[ {"dailyAlways":"2","start":"0","end":"90"} for i in range(7)]
        #목금토일의 시간을 설정.
        for i in range(3,7):
            availability[i] = {"dailyAlways":"1","start":"0","end":"90"}
        BookingDao.add_availability(car.user_id, availability)
        thursday = get_next_week_by_day(3).replace(hour=0,minute=0,second=0)
        sunday=get_next_week_by_day(6).replace(hour=17,minute=0,second=0)
        start_time_str = dt.strftime(thursday,"%Y-%m-%d %H:%M")
        end_time_str = dt.strftime(sunday,"%Y-%m-%d %H:%M")
        self.verify_unvalid_booking_check(car,start_time_str, end_time_str)


    #UserTimeTable의 시간이 car owner가 가능한 요일에 설정된경우.
    def test_check_valid_due_to_usertime_daily_custom(self):
        car = self.activate_car_without_img()
        availability=[ {"dailyAlways":"2","start":"0","end":"90"} for i in range(7)]
        #목금토일의 시간을 설정.
        for i in range(3,7):
            availability[i] = {"dailyAlways":"1","start":"0","end":"1080"}
        BookingDao.add_availability(car.user_id, availability)
        thursday = get_next_week_by_day(3).replace(hour=0,minute=0,second=0)
        sunday=get_next_week_by_day(6).replace(hour=3,minute=0,second=0)
        start_time_str = dt.strftime(thursday,"%Y-%m-%d %H:%M")
        end_time_str = dt.strftime(sunday,"%Y-%m-%d %H:%M")
        self.client.get('/logout')
        user = self.register_user_with_phone(email='gmlaud14@nate.com')
        self.verify_valid_booking_check(car,start_time_str, end_time_str)



    #자신의 차의 예약을 확인하려는 경우.
    def test_own_car_booking(self):
        car = self.activate_car_without_img()
        self.verify_unvalid_booking_check(car,self.vacation_start_time,self.vacation_end_time)


    #기존예약이 없는경우!
    def test_check_booking_with_none_booking_before(self):
        car,user=self.return_user_and_car()
        rv = self.client.post("/api/verify_booking",
                data = json.dumps(dict(
                    start_time = self.vacation_start_time,
                    end_time = self.vacation_end_time,
                    car_id = car.id,
                )),
                content_type='application/json'
                )
        data = json.loads(rv.get_data().decode('utf-8'))
        self.assertTrue(data['message']=="success")

    # 기존예약이 있지만 시간이 겹치는 경우.
    def test_check_booking_with_duplicate_time(self):
        car,user=self.return_user_and_car()
        self.add_random_booking(car,user)
        rv = self.client.post(
                "/api/verify_booking",
                data = json.dumps(dict(
                    start_time = self.vacation_start_time,
                    end_time = self.vacation_end_time,
                    car_id=car.id
                )),
                content_type='application/json'
                )
        data = json.loads(rv.get_data().decode('utf-8'))
        self.assertTrue(data['message']=="fail")


    #기존예약이 있지만 시간이 겹치지 않는경우 .
    def test_check_booking_with_non_duplicate_time(self):
        car,user=self.return_user_and_car()
        self.add_random_booking(car, user)
        rv = self.client.post(
                "/api/verify_booking",
                data = json.dumps(dict(
                    start_time = self.new_start_timestr,
                    end_time = self.new_end_timestr,
                    car_id = car.id,
                )),
                content_type='application/json'
                )
        data = json.loads(rv.get_data().decode('utf-8'))
        self.assertTrue(data['message']=="success")


    # 카드등록.
    def test_register_card(self):
        user = self.register_user_with_phone(email='gmlaud14@nate.com')
        rv = self.client.post(
            "/api/register_card",
            data = json.dumps(self.get_card_info(user.id)),
            content_type='application/json'
        )
        response = json.loads(rv.data.decode())
        self.assertTrue(response['message']=="success")
        userCard = UserCard.query.filter(UserCard.user_id == user.id).first()
        self.assertTrue(userCard.name == self.get_card_info(user.id)['name'])

    # 카드등록.
    def test_register_nice_card(self):
        user = self.register_user_with_phone(email='gmlaud14@nate.com')
        rv = self.client.post(
            "/api/register_nice_card",
            data = json.dumps(self.get_nice_card_info(user.id)),
            content_type='application/json'
        )
        response = json.loads(rv.data.decode())
        self.assertTrue(response['message']=="success")
        userCard = UserCard.query.filter(UserCard.user_id == user.id).first()
        self.assertTrue(userCard.name == self.get_card_info(user.id)['name'])
        tracking = Tracking.objects.filter(__raw__ ={'custom_data.user_id':user.id}).order_by('-date_created').first()
        self.assertTrue(tracking.custom_data['action']=='add_card')
        delete_card(userCard.customer_uid)


    # 카드등록.
    def test_invalid_nice_card(self):
        user = self.register_user_with_phone(email='gmlaud14@nate.com')
        card_data = self.get_nice_card_info(user.id)
        card_data['card_1'] ='1111-2222-3333-4444'
        rv = self.client.post(
            "/api/register_nice_card",
            data = json.dumps(card_data),
            content_type='application/json'
        )
        response = json.loads(rv.data.decode())
        self.assertTrue(response['message']=="fail")
        self.assertTrue(type(response['error_message']==str))

    # 기존카드 존재시 카드삭제후 재등록.
    def test_update_nice_card(self):
        user = self.register_user_with_phone(email='gmlaud14@nate.com')
        card_data = self.get_nice_card_info(user.id)
        rv1 = self.client.post(
            "/api/register_nice_card",
            data = json.dumps(card_data),
            content_type='application/json'
        )
        card_name="jordan"
        new_card_data=dict(
            name=card_name,
            birth="920127",
            card_1="9411-6126-2533-3873",
            expire_year="2024",
            expire_month="05",
            cvc="944",
            password="59",
            auth_token=encrypt_hash(str(user.id))
        )
        rv2 = self.client.post(
            "/api/register_nice_card",
            data = json.dumps(new_card_data),
            content_type='application/json'
        )
        response = json.loads(rv2.data.decode())
        self.assertTrue(response['message']=="success")
        userCard = UserCard.query.filter(UserCard.user_id == user.id).first()
        self.assertTrue(userCard.name == card_name)
        delete_card(userCard.customer_uid)
        tracking = Tracking.objects.filter(__raw__ ={'custom_data.user_id':user.id}).order_by('-date_created').first()
        self.assertTrue(tracking.custom_data['action']=='modify_card')

    def test_add_multiple_card(self):
        pass

    #기존 카드정보 존재.
    def test_get_card_info(self):
        user = self.register_user_with_phone()
        card_data = self.get_card_info(user.id)
        self.add_card_info(user.id)
        rv = self.client.get('/api/get_card_info')
        response = json.loads(rv.data.decode())
        self.assertTrue(
            response['message'] == 'success'
            )
        self.assertTrue(
            response['data']['name'] == self.get_card_info(user.id)['name']
            )


    # valid requiest예약 테스트
    def test_request_bookings(self):
        car,user = self.return_user_and_car()
        user_id = user.id
        self.add_card_info(user_id)
        rv = self.client.post(
            "/api/add_booking",
            data = json.dumps(dict(
                start_time = self.vacation_start_time,
                end_time = self.vacation_end_time,
                auth_token = encrypt_hash(str(user_id)),
                car_id = car.id
            )),
            content_type='application/json'
        )
        self.assertTrue(rv.status_code ==200)
        booking = BookingDao.get_booking_obj_by_car(car.id)
        trip_price = CarDao.get_car_price(car.id,self.original_start_time,self.original_end_time)
        total_distance = get_price(car.distance,self.original_start_time,self.original_end_time)
        rent_fee = int(trip_price * 0.05)
        total_price = trip_price + rent_fee
        self.assertTrue(booking.owner_earning==trip_price)
        self.assertTrue(booking.total_price==trip_price + rent_fee)
        self.assertTrue(booking.insurance_price==0)
        self.assertTrue(booking.status==0)
        self.assertTrue(dt.strftime(booking.start_time,"%Y-%m-%d %H:%M")==self.vacation_start_time)
        self.assertTrue(dt.strftime(booking.end_time,"%Y-%m-%d %H:%M")==self.vacation_end_time)
        self.assertTrue(booking.car_id==car.id)
        self.assertTrue(booking.renter_id==user.id)
        self.assertTrue(booking.total_distance == total_distance)

    def test_invalid_request_bookings(self):
        car,user = self.return_user_and_car()
        user_id = user.id
        self.add_card_info(user_id)
        self.add_random_booking(car,user)
        rv = self.client.post(
            "/api/add_booking",
            data = json.dumps(dict(
                start_time = self.vacation_start_time,
                end_time = self.vacation_end_time,
                auth_token = encrypt_hash(str(user_id)),
                car_id = car.id
            )),
            content_type='application/json'
        )
        self.assertTrue(rv.status_code==200)
        result = json.loads(rv.data.decode())
        self.assertTrue(result['message']=="fail")


    def test_unauthorized_booking(self):
        car,user = self.return_user_and_car()
        user_id = user.id
        self.add_card_info(user_id)
        self.add_random_booking(car,user)
        rv = self.client.post(
            "/api/add_booking",
            data = json.dumps(dict(
                start_time = self.vacation_start_time,
                end_time = self.vacation_end_time,
                auth_token = "abc",
                insurance = "insurancePremium",
                car_id = car.id
            )),
            content_type='application/json'
        )
        self.assertTrue(rv.status_code==403)


    def test_add_booking_img(self):
        car,user = self.return_user_and_car()
        card = self.add_card_info(user.id)
        booking = self.add_random_booking(car,user)
        booking = self.confirm_booking(booking)
        with freeze_time(dt.now()) as frozen_datetime:
            with open(self.test_image, 'r+b') as f:
                rv1= self.client.post(
                    '/api/add_booking_img/' + booking.id,
                     buffered=True,
                   content_type='multipart/form-data',
                   data={
                   'image':f,
                   'booking_id':booking.id,
                   'description':"hello",
                   })
                data = json.loads(rv1.data.decode())
                carbooking_image = BookingImage.query.filter(BookingImage.booking_id==booking.id).filter(BookingImage.active==True).first()
                image_exists = check_img_exists(carbooking_image.filename)
                self.assertTrue(image_exists)
                self.assertTrue(carbooking_image.image_index==0)
                self.check_carbooking_img(data,carbooking_image,car,user)
        self.remove_image(carbooking_image.image,booking.id,'BOOKING_IMAGE_FOLDER')


    def test_add_invalid_booking_img(self):
        car,user = self.return_user_and_car()
        card = self.add_card_info(user.id)
        booking = self.add_random_booking(car,user)
        booking = self.confirm_booking(booking)
        with freeze_time(dt.now()) as frozen_datetime:
            with open(self.test_invalid_img, 'r+b') as f:
                rv1= self.client.post(
                    '/api/add_booking_img/' + booking.id,
                     buffered=True,
                   content_type='multipart/form-data',
                   data={
                   'image':f,
                   'booking_id':booking.id,
                   'description':"hello",
                   })
        data = json.loads(rv1.data.decode())
        self.assertTrue(data['message']=="fail")
        carbooking_image = BookingImage.query.filter(BookingImage.booking_id==booking.id).filter(BookingImage.active==True).first()
        self.assertTrue(carbooking_image is None)
        tracking = Tracking.objects.filter(__raw__ ={'custom_data.action':'image_add_fail'}).order_by('-date_created').first()
        self.assertTrue(tracking.custom_data['action']=='image_add_fail')


    def test_add_booking_nondescription_img(self):
        car,user = self.return_user_and_car()
        card = self.add_card_info(user.id)
        booking = self.add_random_booking(car,user)
        booking = self.confirm_booking(booking)
        with freeze_time(dt.now()) as frozen_datetime:
            with open(self.test_image, 'r+b') as f:
                rv1= self.client.post(
                    '/api/add_booking_img/' + booking.id,
                     buffered=True,
                   content_type='multipart/form-data',
                   data={
                   'image':f,
                   'booking_id':booking.id
                   })
                data = json.loads(rv1.data.decode())
                carbooking_image = BookingImage.query.filter(BookingImage.booking_id==booking.id).filter(BookingImage.active==True).first()
                self.assertTrue(data['description']==carbooking_image.description)
        self.remove_image(carbooking_image.image,booking.id,'BOOKING_IMAGE_FOLDER')


    def test_add_not_matched_booking_img(self):
        car,user = self.return_user_and_car(owneremail='todhm@naver.com', renteremail='gmlaud14@nate.com')
        user_id = user.id
        booking = self.add_random_booking(car,user)
        self.client.get('/logout')
        self.register_user_with_phone(email='todhm@nate.com')
        with open(self.test_image, 'r+b') as f:
            rv1= self.client.post('/api/add_booking_img/'+booking.id, buffered=True,
                               content_type='multipart/form-data',
                               data={'image':f})
        self.assertTrue(rv1.status_code ==403)



    @freeze_time("Jan 14th, 2020", tick=True)
    def test_add_multiple_img_of_booking(self):
        car,user = self.return_user_and_car()
        user_id = user.id
        booking = self.add_random_booking(car,user)
        booking = self.confirm_booking(booking)
        added_booking_lst = []
        added_image_lst = []
        with freeze_time(dt.now()) as frozen_datetime:
            for i in range(10):
                with open(self.test_image, 'r+b') as f:
                    frozen_datetime.tick(delta=timedelta(hours=1))
                    rv= self.client.post('/api/add_booking_img/'+booking.id, buffered=True,
                                       content_type='multipart/form-data',
                                       data={'image':f,'description':str(uuid.uuid4())})
                    data = json.loads(rv.data.decode())
                    carbooking_image = BookingImage.query.filter(BookingImage.booking_id==booking.id).order_by(BookingImage.image_index.desc()).filter(BookingImage.active==True).first()
                    self.check_carbooking_img(data,carbooking_image,car,user)
                    self.assertTrue(i==carbooking_image.image_index)
                    added_booking_lst.append(booking.id)
                    added_image_lst.append(carbooking_image.image)
        self.remove_added_img(added_image_lst,added_booking_lst)


    def test_get_booking_img(self):
        car,user = self.return_user_and_car()
        card = self.add_card_info(user.id)
        booking = self.add_random_booking(car,user)
        booking = self.confirm_booking(booking)
        with open(self.test_image, 'r+b') as f:
            rv1= self.client.post(
                '/api/add_booking_img/'+booking.id,
                 buffered=True,
               content_type='multipart/form-data',
               data={
               'image':f,
               'booking_id':booking.id,
               'description':str(uuid.uuid4())
               })
            data = json.loads(rv1.data.decode())
            carbooking_image = BookingImage.query.filter(BookingImage.booking_id==booking.id).filter(BookingImage.active==True).first()
        rv = self.client.get('/api/get_booking_img/' + booking.id)
        rv_data = json.loads(rv.data.decode())
        data = rv_data['urlList'][0]
        self.check_carbooking_img(data,carbooking_image,car,user)
        self.remove_image(carbooking_image.image,booking.id,'BOOKING_IMAGE_FOLDER')


    def test_get_not_matched_booking_img(self):
        car,user = self.return_user_and_car(owneremail='todhm@naver.com', renteremail='gmlaud14@nate.com')
        user_id = user.id
        booking = self.add_random_booking(car,user)
        with open(self.test_image, 'r+b') as f:
            rv1= self.client.post('/api/add_booking_img', buffered=True,
                               content_type='multipart/form-data',
                               data={'image':f,'booking_id':booking.id})
        self.client.get('/logout')
        self.register_user_with_phone(email='todhm@nate.com')
        rv = self.client.get('/api/get_booking_img/' + booking.id)
        self.assertTrue(rv.status_code ==403)



    @freeze_time("Jan 14th, 2020", tick=True)
    def test_get_multiple_img_of_booking(self):
        car,user = self.return_user_and_car()
        user_id = user.id
        booking = self.add_random_booking(car,user)
        booking = self.confirm_booking(booking)
        added_booking_lst = []
        added_image_lst = []
        with freeze_time(dt.now()) as frozen_datetime:
            for i in range(10):
                with open(self.test_image, 'r+b') as f:
                    frozen_datetime.tick(delta=timedelta(hours=1))
                    rv= self.client.post('/api/add_booking_img/'+booking.id, buffered=True,
                                       content_type='multipart/form-data',
                                       data={'image':f,'booking_id':booking.id})
                    carbooking_image = BookingImage.query.filter(BookingImage.booking_id==booking.id).order_by(BookingImage.image_index.desc()).filter(BookingImage.active==True).first()
                    added_booking_lst.append(booking.id)
                    added_image_lst.append(carbooking_image.image)
        booking_image_list = BookingImage.query.filter(BookingImage.booking_id==booking.id).filter(BookingImage.active==True).order_by(BookingImage.image_index).all()
        rv = self.client.get('/api/get_booking_img/' + booking.id)
        message = json.loads(rv.data.decode())
        data_list = message['urlList']
        for idx, carbooking_image in enumerate(booking_image_list):
            data = data_list[idx]
            self.check_carbooking_img(data,carbooking_image,car,user)
        self.remove_added_img(added_image_lst,added_booking_lst)



    def test_add_carpirce_by_date(self):
        car  = self.activate_car_without_img()
        now_time = dt.now()
        end_time = dt.now() + timedelta(days=3)
        start_time_str = dt.strftime(now_time,"%Y-%m-%d")
        end_time_str = dt.strftime(end_time,"%Y-%m-%d")
        rv = self.client.post('/api/add_carprice/'+car.id,
            data = json.dumps(dict(
                price=10000,
                start_time=start_time_str,
                end_time =end_time_str,
                )
            ),
            content_type='application/json')
        response = json.loads(rv.data.decode())
        carPriceSchedule = CarPriceSchedule.query.filter(CarPriceSchedule.car_id==car.id).first()
        self.assertTrue(response['message']=="success")
        self.assertTrue(carPriceSchedule.price==10000)
        self.assertTrue(dt.strftime(carPriceSchedule.start_time,"%Y-%m-%d")==start_time_str)
        self.assertTrue(dt.strftime(carPriceSchedule.end_time,"%Y-%m-%d")==end_time_str)


    def test_add_duplicate_carprice(self):
        car = self.activate_car_without_img()
        now_time = dt.now()
        new_now_time = dt.now() + timedelta(days=2)
        new_start_timestr = dt.strftime(new_now_time,"%Y-%m-%d")
        end_time = dt.now() + timedelta(days=3)
        start_time_str = dt.strftime(now_time,"%Y-%m-%d")
        end_time_str = dt.strftime(end_time,"%Y-%m-%d")
        rv = self.client.post('/api/add_carprice/'+car.id,
            data = json.dumps(dict(
                price=10000,
                start_time=start_time_str,
                end_time =end_time_str,
                )
            ),
            content_type='application/json')
        rv  = self.client.post('/api/add_carprice/'+car.id,
            data = json.dumps(dict(
                price=10000,
                start_time=new_start_timestr,
                end_time =end_time_str,
                )
            ),
            content_type='application/json')
        carPriceScheduleList = CarPriceSchedule.query.filter(CarPriceSchedule.car_id==car.id).all()
        carPriceSchedule = carPriceScheduleList[0]
        response = json.loads(rv.data.decode())
        self.assertTrue(response['message']=="fail")
        self.assertTrue(response['errorMessage']=="중복된 시간입니다")
        self.assertTrue(len(carPriceScheduleList)==1)
        self.assertTrue(carPriceSchedule.price==10000)
        self.assertTrue(dt.strftime(carPriceSchedule.start_time,"%Y-%m-%d")==start_time_str)
        self.assertTrue(dt.strftime(carPriceSchedule.end_time,"%Y-%m-%d")==end_time_str)

    def test_add_invalid_car_priceinput(self):
        car = self.activate_car_without_img()
        now_time = dt.now()
        end_time = dt.now() + timedelta(days=3)
        price = 10000
        start_time_str = dt.strftime(now_time,"%Y-%m-%d")
        end_time_str = dt.strftime(end_time,"%Y-%m-%d")
        invalid_start_time =  dt.strftime(now_time,"%Y-%m")
        invalid_end_time = dt.strftime(end_time,"%Y-%d")
        invalid_price = "abcdef"
        rv = self.client.post('/api/add_carprice/'+car.id,
            data = json.dumps(dict(
                price=invalid_price,
                start_time=start_time_str,
                end_time =end_time_str,
                )
            ),
            content_type='application/json')
        response = json.loads(rv.data.decode())
        self.assertTrue(response['message']=="fail")
        rv = self.client.post('/api/add_carprice/'+car.id,
            data = json.dumps(dict(
                price=price,
                start_time=invalid_start_time,
                end_time =end_time_str,
                )
            ),
            content_type='application/json')
        response = json.loads(rv.data.decode())
        self.assertTrue(response['message']=="fail")
        rv = self.client.post('/api/add_carprice/'+car.id,
            data = json.dumps(dict(
                price=price,
                start_time=start_time_str,
                end_time =invalid_end_time,
                )
            ),
            content_type='application/json')
        response = json.loads(rv.data.decode())
        self.assertTrue(response['message']=="fail")

    def test_get_carprice_schedule(self):
        car  = self.activate_car_without_img()
        self.add_carprice_schedule(
            car_id=car.id,
            price=10000
        )
        rv = self.client.get('/api/get_carprice_schedule/' + car.id)
        response= json.loads(rv.data.decode())
        carSchedulePrice = CarPriceSchedule.query.first()
        self.assertTrue(len(response['priceEvents'])==1)
        self.assertTrue(response['priceEvents'][0]['price']==carSchedulePrice.price)
        self.assertTrue(response['priceEvents'][0]['startDate']==dt.strftime(carSchedulePrice.start_time,'%Y-%m-%d %H:%M'))
        self.assertTrue(response['priceEvents'][0]['endDate']==dt.strftime(carSchedulePrice.end_time,'%Y-%m-%d %H:%M'))
        self.assertTrue(response['priceEvents'][0]['id']==carSchedulePrice.id)

    def test_update_carprice_schedule(self):
        car  = self.activate_car_without_img()
        price = 10000
        new_price=20000
        schedule = self.add_carprice_schedule(
            car_id=car.id,
            price=price
        )
        start_time = dt.now() + timedelta(days=1)
        end_time = dt.now() + timedelta(days =20)
        start_time_str = dt.strftime(start_time,"%Y-%m-%d")
        end_time_str = dt.strftime(end_time,"%Y-%m-%d")
        rv = self.client.post('/api/update_carprice_schedule/'+car.id,
            data = json.dumps(dict(
                price=new_price,
                start_time=start_time_str,
                end_time =end_time_str,
                id=schedule.id,
                )
            ),
            content_type='application/json')
        response = json.loads(rv.data.decode())
        carPriceSchedule = CarPriceSchedule.query.filter(CarPriceSchedule.car_id==car.id).first()
        self.assertTrue(response['message']=="success")
        self.assertTrue(carPriceSchedule.price==new_price)
        self.assertTrue(dt.strftime(carPriceSchedule.start_time,"%Y-%m-%d")==start_time_str)
        self.assertTrue(dt.strftime(carPriceSchedule.end_time,"%Y-%m-%d")==end_time_str)

    def test_update_duplicate_schedule(self):
        car  = self.activate_car_without_img()
        price = 10000
        new_price=20000
        schedule1 = self.add_carprice_schedule(
            car_id=car.id,
            price=price
        )
        start_time = dt.now() + timedelta(days=1)
        end_time = dt.now() + timedelta(days =20)
        schedule2 = self.add_carprice_schedule(
            car_id=car.id,
            price=price,
            start_time=start_time,
            end_time=end_time
        )
        start_time_str = dt.strftime(start_time,"%Y-%m-%d")
        end_time_str = dt.strftime(end_time,"%Y-%m-%d")
        rv = self.client.post('/api/update_carprice_schedule/'+car.id,
            data = json.dumps(dict(
                price=new_price,
                start_time=start_time_str,
                end_time =end_time_str,
                id=schedule1.id,
                )
            ),
            content_type='application/json')
        response = json.loads(rv.data.decode())
        carPriceSchedule = CarPriceSchedule.query.filter(CarPriceSchedule.car_id==car.id).first()
        self.assertTrue(response['message']=="fail")

    def test_add_car_vacation(self):
        car  = self.activate_car_without_img()
        start_time = dt.now() + timedelta(days=1)
        end_time = dt.now() + timedelta(days =20)
        start_time_str = dt.strftime(start_time,"%Y-%m-%d")
        end_time_str = dt.strftime(end_time,"%Y-%m-%d")
        rv = self.client.post('/api/add_car_vacation/'+car.id,
            data = json.dumps(dict(
                start_time=start_time_str,
                end_time =end_time_str,
                )
            ),
            content_type='application/json')
        response = json.loads(rv.data.decode())
        carVacation = CarVacation.query.filter(CarVacation.car_id==car.id).first()
        self.assertTrue(response['message']=="success")
        self.assertTrue(dt.strftime(carVacation.start_time,"%Y-%m-%d")==start_time_str)
        self.assertTrue(dt.strftime(carVacation.end_time,"%Y-%m-%d")==end_time_str)


    def test_update_carvacation_schedule(self):
        car  = self.activate_car_without_img()
        schedule = self.add_car_vacation(
            car_id=car.id
        )
        start_time = dt.now() + timedelta(days=1)
        end_time = dt.now() + timedelta(days =20)
        start_time_str = dt.strftime(start_time,"%Y-%m-%d")
        end_time_str = dt.strftime(end_time,"%Y-%m-%d")
        rv = self.client.post('/api/update_car_vacation/'+car.id,
            data = json.dumps(dict(
                start_time=start_time_str,
                end_time =end_time_str,
                id=schedule.id,
                )
            ),
            content_type='application/json')
        response = json.loads(rv.data.decode())
        carVacation = CarVacation.query.filter(CarVacation.car_id==car.id).first()
        self.assertTrue(response['message']=="success")
        self.assertTrue(dt.strftime(carVacation.start_time,"%Y-%m-%d")==start_time_str)
        self.assertTrue(dt.strftime(carVacation.end_time,"%Y-%m-%d")==end_time_str)
