import os
import unittest
import sqlalchemy
from flask import Flask,session,url_for,redirect
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import desc
from application import create_app ,db
import unittest
from unittest.mock import patch
import json
from caruser.models import User
from caruser.forms import SearchForm
from carupload.models import CarOption,Car,CarImage
from carbooking.tasks import *
from carbooking.models import UserTime, VacationData,UserCard, Payment,CarBooking,Message, OwnerSend, OwnerReview, RenterReview,BookingImage
from utilities.dao.userdao import UserDao
from utilities.dao.bookingdao import BookingDao
from utilities.testutil import TestUtil
from utilities.timeutil import get_next_week_by_day
from utilities.common import get_price
from utilities.hashutil import encrypt_hash,decrypt_hash
from utilities.flask_tracking.documents import Tracking
from mongoengine.queryset.visitor import Q
from freezegun import freeze_time
from datetime import datetime as dt
from datetime import timedelta
import urllib
import re
import uuid


class CarBookingTest(TestUtil):


    def setUp(self):
        super().setUp()

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
                               1000
                               )
        return booking


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

    def get_booked_owner(self,owneremail='todhm@naver.com',
    renteremail='gmlaud14@nate.com',start_time=None,end_time=None):
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

    def get_address_dict(self,address):
        address_list = self.search_address(address)
        address_dict = address_list[0]
        return address_dict

    def verify_search_session(self,session_data,address_dict):
        self.assertTrue(session_data['address']== address_dict['address'])
        self.assertTrue(int(float(session_data['pointX'])*1000) == int(float(address_dict['pointX'])*1000))
        self.assertTrue(int(float(session_data['pointY'])*1000) == int(float(address_dict['pointY'])*1000))
        self.assertTrue(session_data['startDate'] == address_dict['startDate'])
        self.assertTrue(session_data['endDate'] == address_dict['endDate'])
        self.assertTrue(session_data['startTime'] == address_dict['startTime'])
        self.assertTrue(session_data['endTime'] == address_dict['endTime'])

    def verify_search_page(self,rv,address_dict):
        self.assertTrue(address_dict['address'] in rv.data.decode())

    def test_carowner_goto_reservation_page(self):
        booking,owner,renter = self.get_booked_owner()
        rv = self.client.get("/reservation/" +booking.id)
        self.assertTrue( str(booking.owner_earning) in rv.data.decode())
        self.assertTrue( booking.car.address in rv.data.decode())
        self.assertTrue( booking.car.detail_address in rv.data.decode())
        self.assertTrue( booking.renter.name in rv.data.decode())
        self.assertTrue('요청 거절하기'in rv.data.decode())

    def test_carrenter_goto_reservation_page(self):
        booking,user = self.get_booked_renter()
        rv = self.client.get("/reservation/" +booking.id)
        self.assertTrue( str(booking.total_price) in rv.data.decode())
        self.assertTrue( booking.car.address in rv.data.decode())
        self.assertTrue( booking.car.detail_address in rv.data.decode())
        self.assertTrue( booking.car.user.name in rv.data.decode())
        self.assertTrue('요청 취소하기'in rv.data.decode())

    def test_carowner_allow_reservation(self):
        booking, owner, renter = self.get_booked_owner()
        self.add_card_info(renter.id)
        rv = self.client.post(
            '/reservation/'+booking.id,
            data = dict(
                confirm = 'confirm'
                )
            )
        payment = Payment.query.filter(Payment.booking_id == booking.id).first()
        booking = BookingDao.get_booking_obj_by_user(renter.id)
        self.assertTrue(rv.status_code==200)
        self.assertTrue(booking.status ==2)
        self.assertTrue(payment.price == booking.total_price)
        tracking = Tracking.objects.filter(__raw__ ={'custom_data.user_id':owner.id}).first()
        self.assertTrue(tracking.custom_data['action']=='booking_confirm')
        self.assertTrue(tracking.custom_data['renter_name']==booking.renter.name)
        self.assertTrue(tracking.custom_data['owner_name']==booking.car.user.name)

    def test_carowner_disallow_reservation(self):
        booking, owner, renter = self.get_booked_owner()
        self.add_card_info(renter.id)
        rv = self.client.post(
            '/reservation/'+booking.id,
            data = dict(
                disallow = 'disallow'
                )
            )
        booking = BookingDao.get_booking_obj_by_user(renter.id)
        self.assertTrue(rv.status_code==200)
        self.assertTrue(booking.status == -1 )
        tracking = Tracking.objects.filter(__raw__ ={'custom_data.user_id':owner.id}).first()
        self.assertTrue(tracking.custom_data['action']=='booking_disallow')
        self.assertTrue(tracking.custom_data['renter_name']==booking.renter.name)
        self.assertTrue(tracking.custom_data['owner_name']==booking.car.user.name)


    def test_carrenter_cancel_right_after(self):
        owneremail = 'todhm@naver.com'
        renteremail = 'gmlaud14@nate.com'
        booking, owner, renter = self.get_booked_owner(owneremail,renteremail)
        self.add_card_info(renter.id)
        rv = self.client.post(
            '/reservation/'+booking.id,
            data = dict(
                confirm='confirml'
                )
            )
        self.client.get('/logout')
        self.login_user(renteremail)
        rv = self.client.post(
            '/reservation/'+booking.id,
            data = dict(
                cancel='cancel'
                )
            )
        booking = BookingDao.get_booking_obj_by_user(renter.id)
        payment_list = Payment.query.filter(Payment.booking_id == booking.id).order_by(Payment.register_date).all()
        self.assertTrue(rv.status_code==200)
        self.assertTrue(booking.status == -3)
        self.assertTrue(payment_list[0].is_cancel == False )
        self.assertTrue(payment_list[1].is_cancel == True)
        self.assertTrue(payment_list[0].price == booking.total_price)
        self.assertTrue(payment_list[1].price == booking.total_price*(-1))
        tracking = Tracking.objects.filter(__raw__ ={'custom_data.user_id':renter.id}).first()
        self.assertTrue(tracking.custom_data['action']=='cancel_booking')
        self.assertTrue(tracking.custom_data['cancel_price']== booking.total_price * (-1))
        self.assertTrue(tracking.custom_data['renter_name']==booking.renter.name)
        self.assertTrue(tracking.custom_data['owner_name']==booking.car.user.name)

    def test_carrenter_cancel_less_than24(self):
        owneremail = 'todhm@naver.com'
        renteremail = 'gmlaud14@nate.com'
        booking, owner, renter = self.get_booked_owner(owneremail,renteremail)
        self.add_card_info(renter.id)
        rv = self.client.post(
            '/reservation/'+booking.id,
            data = dict(
                confirm='confirml'
                )
            )
        self.client.get('/logout')
        self.login_user(renteremail)
        with freeze_time(dt.now()) as frozen_datetime:
            frozen_datetime.tick(delta=timedelta(hours=10))
            rv = self.client.post(
                '/reservation/'+booking.id,
                data = dict(
                    cancel='cancel'
                    )
                )
            booking = BookingDao.get_booking_obj_by_user(renter.id)
            self.assertTrue(rv.status_code==200)
            self.assertTrue(booking.status == -6)
            tracking = Tracking.objects.filter(__raw__ ={'custom_data.user_id':renter.id}).first()
            self.assertTrue(tracking.custom_data['action']=='cancel_booking')
            self.assertTrue(tracking.custom_data['cancel_price']== 0)
            self.assertTrue(tracking.custom_data['renter_name']==booking.renter.name)
            self.assertTrue(tracking.custom_data['owner_name']==booking.car.user.name)

    def test_carrenter_cancel_1_to_7(self):
        owneremail = 'todhm@naver.com'
        renteremail = 'gmlaud14@nate.com'
        start_time = dt.now() + timedelta(days=4)
        end_time = dt.now() + timedelta(days=8)
        booking, owner, renter = self.get_booked_owner(owneremail,renteremail,start_time,end_time)
        self.add_card_info(renter.id)
        rv = self.client.post(
            '/reservation/'+booking.id,
            data = dict(
                confirm='confirm'
                )
            )
        self.client.get('/logout')
        self.login_user(renteremail)
        with freeze_time(dt.now()) as frozen_datetime:
            frozen_datetime.tick(delta=timedelta(hours=10))
            rv = self.client.post(
                '/reservation/'+booking.id,
                data = dict(
                    cancel='cancel'
                    )
                )
            booking = BookingDao.get_booking_obj_by_user(renter.id)
            payment_list = Payment.query.filter(Payment.booking_id == booking.id).order_by(Payment.register_date).all()
            self.assertTrue(rv.status_code==200)
            self.assertTrue(booking.status == -5)
            self.assertTrue(payment_list[0].is_cancel == False )
            self.assertTrue(payment_list[1].is_cancel == True)
            self.assertTrue(payment_list[0].price == booking.total_price)
            self.assertTrue(payment_list[1].price == int(booking.owner_earning*(-0.9)))
            tracking = Tracking.objects.filter(__raw__ ={'custom_data.user_id':renter.id}).first()
            self.assertTrue(tracking.custom_data['action']=='cancel_booking')
            self.assertTrue(tracking.custom_data['cancel_price']== int(booking.owner_earning*(-0.9)))
            self.assertTrue(tracking.custom_data['renter_name']==booking.renter.name)
            self.assertTrue(tracking.custom_data['owner_name']==booking.car.user.name)

    def test_carrenter_cancel_over_7(self):
        owneremail = 'todhm@naver.com'
        renteremail = 'gmlaud14@nate.com'
        start_time = dt.now() + timedelta(days=8)
        end_time = dt.now() + timedelta(days=12)
        booking, owner, renter = self.get_booked_owner(owneremail,renteremail,start_time,end_time)
        self.add_card_info(renter.id)
        rv = self.client.post(
            '/reservation/'+booking.id,
            data = dict(
                confirm='confirm'
                )
            )
        self.client.get('/logout')
        self.login_user(renteremail)
        with freeze_time(dt.now()) as frozen_datetime:
            frozen_datetime.tick(delta=timedelta(hours=10))
            rv = self.client.post(
                '/reservation/'+booking.id,
                data = dict(
                    cancel='cancel'
                    )
                )
            booking = BookingDao.get_booking_obj_by_user(renter.id)
            payment_list = Payment.query.filter(Payment.booking_id == booking.id).order_by(Payment.register_date).all()
            self.assertTrue(rv.status_code==200)
            self.assertTrue(booking.status == -4)
            self.assertTrue(payment_list[0].is_cancel == False )
            self.assertTrue(payment_list[1].is_cancel == True)
            self.assertTrue(payment_list[0].price == booking.total_price)
            self.assertTrue(payment_list[1].price == booking.owner_earning*(-1))
            tracking = Tracking.objects.filter(__raw__ ={'custom_data.user_id':renter.id}).first()
            self.assertTrue(tracking.custom_data['action']=='cancel_booking')
            self.assertTrue(tracking.custom_data['cancel_price']== booking.owner_earning*(-1))
            self.assertTrue(tracking.custom_data['renter_name']==booking.renter.name)
            self.assertTrue(tracking.custom_data['owner_name']==booking.car.user.name)

    def test_pending_booking_notification(self):
        owneremail = 'todhm@naver.com'
        renteremail = 'gmlaud14@nate.com'
        booking, owner, renter = self.get_booked_owner(owneremail,renteremail)
        rv = self.client.get('/notifications')
        self.assertTrue('{}님이 {}을 빌리고싶어하십니다.'.format(
            booking.renter.name,
            booking.car.class_name) in rv.data.decode())
        self.client.get('/logout')
        self.login_user(email=renteremail)
        rv = self.client.get('/notifications')
        self.assertTrue('{}님의 {}을 요청하였습니다.'.format(
            booking.car.user.name,
            booking.car.class_name) in rv.data.decode())


    def test_renter_cancel_notification(self):
        owneremail = 'todhm@naver.com'
        renteremail = 'gmlaud14@nate.com'
        booking, owner, renter = self.get_booked_owner(owneremail,renteremail)
        self.client.get('/logout')
        self.login_user(email=renteremail)
        rv = self.client.post(
            '/reservation/'+booking.id,
            data = dict(
                cancel='cancel'
                )
            )
        # 본인이 예약을 취소한경우 예약자의 이름이 나타나지 않음.
        rv = self.client.get('/notifications')
        self.assertTrue('예약을 취소하였습니다.' in rv.data.decode())
        self.client.get('/logout')

        # 타인이 예약을 취소한 경우 예약자의 이름이 나타남.
        self.login_user(email=owneremail)
        rv = self.client.get('/notifications')
        self.assertTrue('{}님이 예약을 취소하였습니다.'.format(renter.name) in rv.data.decode())


    def test_owner_confirm_notification(self):
        owneremail = 'todhm@naver.com'
        renteremail = 'gmlaud14@nate.com'
        booking, owner, renter = self.get_booked_owner(owneremail,renteremail)
        rv = self.client.post(
            '/reservation/'+booking.id,
            data = dict(
                confirm='confirm'
                )
            )
        # 본인이 예약을 확정한 경우  예약자의 이름이 나타나지 않음.
        rv = self.client.get('/notifications')
        self.assertTrue('예약을 수락하였습니다.' in rv.data.decode())
        self.client.get('/logout')

        # 타인이 예약을 확정한 경우 예약자의 이름이 나타남.
        self.login_user(email=renteremail)
        rv = self.client.get('/notifications')
        self.assertTrue('{}님이 예약을 수락하였습니다.'.format(owner.name) in rv.data.decode())


    def test_owner_cancel_notification(self):
        owneremail = 'todhm@naver.com'
        renteremail = 'gmlaud14@nate.com'
        booking, owner, renter = self.get_booked_owner(owneremail,renteremail)
        rv = self.client.post(
            '/reservation/'+booking.id,
            data = dict(
                confirm='confirm'
                )
            )
        rv = self.client.post(
            '/reservation/'+booking.id,
            data = dict(
                disallow='disallow'
                )
            )
        # 본인이 예약을 확정한 경우  예약자의 이름이 나타나지 않음.
        rv = self.client.get('/notifications')
        self.assertTrue('예약을 취소하였습니다.' in rv.data.decode())
        self.client.get('/logout')

        # 타인이 예약을 확정한 경우 예약자의 이름이 나타남.
        self.login_user(email=renteremail)
        rv = self.client.get('/notifications')
        self.assertTrue('{}님이 예약을 취소하였습니다.'.format(owner.name) in rv.data.decode())

    def test_owner_disallow(self):
        owneremail = 'todhm@naver.com'
        renteremail = 'gmlaud14@nate.com'
        booking, owner, renter = self.get_booked_owner(owneremail,renteremail)
        rv = self.client.post(
            '/reservation/'+booking.id,
            data = dict(
                disallow='disallow'
                )
            )

        rv = self.client.get('/notifications')
        self.assertTrue('예약을 거절하였습니다.' in rv.data.decode())
        self.client.get('/logout')

        # 타인이 예약을 확정한 경우 예약자의 이름이 나타남.
        self.login_user(email=renteremail)
        rv = self.client.get('/notifications')
        self.assertTrue('{}님이 예약을 거절하였습니다.'.format(owner.name) in rv.data.decode())

    def test_owner_send_message(self):
        owneremail = 'todhm@naver.com'
        renteremail = 'gmlaud14@nate.com'
        booking, owner, renter = self.get_booked_owner(owneremail,renteremail)
        message = '나는 천재다.'
        rv = self.client.post(
            '/send_message/'+booking.id,
            data = dict(
                message=message
                ),
            follow_redirects=True
            )
        with self.client.session_transaction() as session:
            self.assertTrue(rv.status_code==200)
            self.assertTrue(type(session[renter.phone])== str )
        messageObject = Message.query.filter(Message.booking_id==booking.id).first()
        self.assertTrue(messageObject.message == message)
        rv = self.client.get('/reservation/'+booking.id)
        self.assertTrue( message in rv.data.decode())
        rv = self.client.get('/notifications')
        self.assertTrue('{}님에게 메세지를 보냈습니다.'.format(renter.name) in rv.data.decode())
        self.client.get('/logout')
        self.login_user(renteremail)
        rv = self.client.get('/notifications')
        self.assertTrue('{}님이 메세지를 보냈습니다.'.format(owner.name) in rv.data.decode())

    def test_renter_send_message(self):
        owneremail = 'todhm@naver.com'
        renteremail = 'gmlaud14@nate.com'
        booking, owner, renter = self.get_booked_owner(owneremail,renteremail)
        self.client.get('/logout')
        self.login_user(renteremail)
        message = '나는 천재다.'
        rv = self.client.post(
            '/send_message/'+booking.id,
            data = dict(
                message=message
                ),
            follow_redirects=True
            )
        with self.client.session_transaction() as session:
            print(rv.status_code)
            self.assertTrue(rv.status_code==200)
            self.assertTrue(type(session[owner.phone])== str )
        messageObject = Message.query.filter(Message.booking_id==booking.id).first()
        self.assertTrue(messageObject.message == message)
        rv = self.client.get('/reservation/'+booking.id)
        self.assertTrue(rv.status_code==200)
        self.assertTrue( message in rv.data.decode())
        rv = self.client.get('/notifications')
        self.assertTrue('{}님에게 메세지를 보냈습니다.'.format(owner.name) in rv.data.decode())


    def test_multiple_notifications(self):
        owneremail = 'todhm@naver.com'
        renteremail = 'gmlaud14@nate.com'
        booking, owner, renter = self.get_booked_owner(owneremail,renteremail)
        self.client.get('/logout')
        self.login_user(renteremail)
        message = '나는 천재다.'
        rv = self.client.post(
            '/send_message/'+booking.id,
            data = dict(
                message=message
                ),
            follow_redirects=True
            )
        rv = self.client.post(
            '/reservation/'+booking.id,
            data = dict(
                cancel='cancel'
                )
            )
        # 본인이 예약을 취소한경우 예약자의 이름이 나타나지 않음.
        rv = self.client.get('/notifications')
        self.assertTrue('예약을 취소하였습니다.' in rv.data.decode())
        self.assertTrue('{}님에게 메세지를 보냈습니다.'.format(owner.name) in rv.data.decode())

    def test_multiple_message(self):
        owneremail = 'todhm@naver.com'
        renteremail = 'gmlaud14@nate.com'
        booking, owner, renter = self.get_booked_owner(owneremail,renteremail)
        message = '나는 천재다.'
        message2 = '나는 바보다.'
        rv = self.client.post(
            '/send_message/'+booking.id,
            data = dict(
                message=message
                ),
            follow_redirects=True
            )
        rv = self.client.post(
            '/send_message/'+booking.id,
            data = dict(
                message=message
                ),
            follow_redirects=True
            )
        logList = Tracking.objects.filter(
            Q(__raw__ = {'custom_data.user_id' : owner.id})
            ).order_by('-date_created')
        self.assertTrue(len(logList)==1)
        with freeze_time(dt.now()) as frozen_datetime:
            frozen_datetime.tick(delta=timedelta(hours=10))
            rv = self.client.post(
                '/send_message/'+booking.id,
                data = dict(
                    message=message
                    ),
                follow_redirects=True
                )
            logList = Tracking.objects.filter(
                Q(__raw__ = {'custom_data.user_id' : owner.id})
                ).order_by('-date_created')
            self.assertTrue(len(logList)==2)

    #예약시간관련 예약 취소.
    def test_cancel_overtime(self):
        with freeze_time(dt.now()) as frozen_datetime:
            #예약시간으로부터 12시간이 지나지 않았을경우.
            booking, owner, renter = self.get_booked_owner(
                start_time=self.original_start_time,
                end_time=self.original_start_time
                )
            cancel_overtime()
            booking = CarBooking.query.filter_by(renter_id = renter.id).first()
            self.assertTrue(booking.status ==0)

            #예약 시간으로부터 12시간이 지났을경우 예약 취소.
            booking = CarBooking.query.filter_by(renter_id = renter.id).first()
            frozen_datetime.tick(delta=timedelta(hours=12))
            cancel_overtime()
            self.assertTrue(booking.status ==-2)
            logList = Tracking.objects.filter(
                Q(__raw__ = {'custom_data.action' : 'auto_cancel_booking'})
                ).order_by('-date_created')
            self.assertTrue(len(logList)==1)
            self.assertTrue(logList[0].custom_data['action']=='auto_cancel_booking')
            self.assertTrue(logList[0].custom_data['user_id']=='wicar')



    #시작시간 관련 예약 취소.
    def test_cancel_regarding_booking_st(self):
        with freeze_time(dt.now()) as frozen_datetime:
            #시작시간이 지난경우의 예약!!
            booking, owner, renter = self.get_booked_owner(
                start_time=dt.now(),
                end_time=dt.now() + timedelta(hours=3)
                )
            cancel_overtime()
            booking = CarBooking.query.filter(CarBooking.id==booking.id).first()
            self.assertTrue(booking.status == -2)
            logList = Tracking.objects.filter(
                Q(__raw__ = {'custom_data.user_id' : 'wicar'})
                ).order_by('-date_created')
            self.assertTrue(len(logList)==1)
            self.assertTrue(logList[0].custom_data['action']=='auto_cancel_booking')


    def test_update_booking_status(self):
        with freeze_time(dt.now()) as frozen_datetime:
            booking, owner, renter = self.get_booked_owner(
                start_time=dt.now(),
                end_time=dt.now() + timedelta(hours=3)
                )

            rv = self.client.post(
                '/reservation/'+booking.id,
                data = dict(
                    confirm='confirm'
                    )
                )
            bank = self.add_bank(owner.id)
            #예약시간이 종료되지 않았을떄의 예약 종료 확인.
            finish_past_booking()
            changed_booking = CarBooking.query.filter(CarBooking.id==booking.id).first()
            self.assertTrue(changed_booking.status==2)

            #예약시간이 지났을때의 예약 종료 확인
            frozen_datetime.tick(delta=timedelta(hours=10))
            finish_past_booking()
            changed_booking = CarBooking.query.filter(CarBooking.id==booking.id).first()
            self.assertTrue(changed_booking.status==3)
            logList = Tracking.objects.filter(
                Q(__raw__ = {'custom_data.user_id' : 'wicar',
                            'custom_data.action':'finish_booking'})
                ).order_by('-date_created')
            self.assertTrue(len(logList)==1)
            self.assertTrue(logList[0].custom_data['action']=='finish_booking')

    def test_update_multiple_booking(self):
        with freeze_time(dt.now()) as frozen_datetime:
            owner, renter, bank = self.add_confirmed_booking(
                start_time=dt.now(),
                end_time=dt.now() + timedelta(hours=3)
                )
            owner, renter, bank = self.add_confirmed_booking(
                start_time=dt.now(),
                end_time=dt.now() + timedelta(hours=3)
                )

            frozen_datetime.tick(delta=timedelta(hours=10))
            finish_past_booking()
            bookingList = CarBooking.query.all()
            for booking in bookingList:
                self.assertTrue(booking.status==3)
            logList = Tracking.objects.filter(
                Q(__raw__ = {'custom_data.user_id' : 'wicar',
                            'custom_data.action':'finish_booking'})
                ).order_by('-date_created')
            self.assertTrue(len(logList)==2)
            for log in logList:
                self.assertTrue(log.custom_data['action']=='finish_booking')


    def test_update_mixed_user(self):
        with freeze_time(dt.now()) as frozen_datetime:
            owner, renter, bank = self.add_confirmed_booking(
                owneremail='todhm@nate.com',
                start_time=dt.now(),
                end_time=dt.now() + timedelta(hours=3)
                )
            self.client.get('/logout')
            owner, renter, bank = self.add_confirmed_booking(
                owneremail='todhm@naver.com',
                start_time=dt.now(),
                end_time=dt.now() + timedelta(hours=3)
                )
            frozen_datetime.tick(delta=timedelta(hours=10))
            finish_past_booking()
            bookingList = CarBooking.query.all()
            for booking in bookingList:
                self.assertTrue(booking.status==3)

            logList = Tracking.objects.filter(
                Q(__raw__ = {'custom_data.user_id' : 'wicar',
                            'custom_data.action':'finish_booking'})
                ).order_by('-date_created')
            self.assertTrue(len(logList)==2)
            for log in logList:
                self.assertTrue(log.custom_data['action']=='finish_booking')


    def test_update_mixed_time(self):
        with freeze_time(dt.now()) as frozen_datetime:
            owner, renter, bank = self.add_confirmed_booking(
                start_time=dt.now(),
                end_time=dt.now() + timedelta(hours=3)
                )
            owner, renter, bank = self.add_confirmed_booking(
                start_time=dt.now(),
                end_time=dt.now() + timedelta(hours=3)
                )
            owner, renter, bank = self.add_confirmed_booking(
                start_time=dt.now(),
                end_time=dt.now() + timedelta(hours=11)
                )
            frozen_datetime.tick(delta=timedelta(hours=10))
            finish_past_booking()
            bookingList = CarBooking.query.all()
            payedBooking = CarBooking.query.filter(CarBooking.status ==3).all()
            self.assertEqual(len(bookingList),3)
            self.assertEqual(len(payedBooking),2)
            logList = Tracking.objects.filter(
                Q(__raw__ = {'custom_data.user_id' : 'wicar',
                            'custom_data.action':'finish_booking'})
                ).order_by('-date_created')
            self.assertTrue(len(logList)==2)
            for log in logList:
                self.assertTrue(log.custom_data['action']=='finish_booking')


    def test_update_mixed_account(self):
        with freeze_time(dt.now()) as frozen_datetime:
            owner, renter, bank = self.add_confirmed_booking(
                owneremail='todhm@nate.com',
                start_time=dt.now(),
                end_time=dt.now() + timedelta(hours=3)
                )
            self.client.get('/logout')
            owner, renter, bank = self.add_confirmed_booking(
                owneremail='todhm@naver.com',
                start_time=dt.now(),
                end_time=dt.now() + timedelta(hours=3),
                bank_code_std='089',
                bank_name='신한은행',
                account_num='110339922410',
                account_holder_info='9201271',
                account_holder_name='강희명'
                )

            frozen_datetime.tick(delta=timedelta(hours=10))
            finish_past_booking()
            bookingList = CarBooking.query.all()
            payedBooking = CarBooking.query.filter(CarBooking.status ==3).all()
            self.assertEqual(len(payedBooking),2)
            logList = Tracking.objects.filter(
                Q(__raw__ = {'custom_data.user_id' : 'wicar',
                            'custom_data.action':'finish_booking'})
                ).order_by('-date_created')
            self.assertTrue(len(logList)==2)
            for log in logList:
                self.assertTrue(log.custom_data['action']=='finish_booking')


    def test_update_mixed_account(self):
        with freeze_time(dt.now()) as frozen_datetime:
            owner, renter, bank = self.add_confirmed_booking(
                owneremail='todhm@nate.com',
                start_time=dt.now(),
                end_time=dt.now() + timedelta(hours=3)
                )
            self.client.get('/logout')
            owner, renter, bank = self.add_confirmed_booking(
                owneremail='todhm@naver.com',
                start_time=dt.now(),
                end_time=dt.now() + timedelta(hours=3),
                bank_code_std='089',
                bank_name='신한은행',
                account_num='110339922410',
                account_holder_info='9201271',
                account_holder_name='강희명'
                )

            frozen_datetime.tick(delta=timedelta(hours=10))
            finish_past_booking()
            bookingList = CarBooking.query.all()
            payedBooking = CarBooking.query.filter(CarBooking.status ==3).all()
            self.assertEqual(len(payedBooking),2)
            logList = Tracking.objects.filter(
                Q(__raw__ = {'custom_data.user_id' : 'wicar',
                            'custom_data.action':'finish_booking'})
                ).order_by('-date_created')
            self.assertTrue(len(logList)==2)
            for log in logList:
                self.assertTrue(log.custom_data['action']=='finish_booking')


    def test_owner_review_template(self):
        owneremail ='todhm@naver.com'
        renteremail='todhm@nate.com'
        booking, owner, renter = self.get_booked_owner(
            owneremail=owneremail,
            renteremail=renteremail
            )
        booking.status = 3
        db.session.commit()
        self.client.get('/logout')
        self.login_user(renteremail)
        rv = self.client.get('/reservation/' + booking.id)
        self.assertTrue('리뷰남기기' in rv.data.decode())

    def test_owner_add_review(self):
        owneremail ='todhm@naver.com'
        renteremail='todhm@nate.com'
        reviewMessage="안녕하세요"
        booking, owner, renter = self.get_booked_owner(
            owneremail=owneremail,
            renteremail=renteremail
            )
        booking.status = 3
        db.session.commit()
        self.client.get('/logout')
        self.login_user(renteremail)
        rv = self.client.post(
            '/add_owner_review/' + booking.id,
            data=dict(
                review="안녕하세요",
                review_point=5
            ))
        review = OwnerReview.query.filter(OwnerReview.booking_id==booking.id).first()
        self.assertEqual(review.review,reviewMessage)
        self.assertEqual(review.review_point,5)

    def test_float_point_review(self):
        owneremail ='todhm@naver.com'
        renteremail='todhm@nate.com'
        reviewMessage="안녕하세요"
        booking, owner, renter = self.get_booked_owner(
            owneremail=owneremail,
            renteremail=renteremail
            )
        booking.status = 3
        db.session.commit()
        self.client.get('/logout')
        self.login_user(renteremail)
        rv = self.client.post(
            '/add_owner_review/' + booking.id,
            data=dict(
                review="안녕하세요",
                review_point=3.5
            ))
        review = OwnerReview.query.filter(OwnerReview.booking_id==booking.id).first()
        self.assertEqual(review.review,reviewMessage)
        self.assertEqual(review.review_point,3.5)

    def test_ownerreview_rendering(self):
        owneremail ='todhm@naver.com'
        renteremail='todhm@nate.com'
        reviewMessage="안녕하세요"
        booking, owner, renter = self.get_booked_owner(
            owneremail=owneremail,
            renteremail=renteremail
            )
        booking.status = 3
        db.session.commit()
        self.client.get('/logout')
        self.login_user(renteremail)
        rv = self.client.post(
            '/add_owner_review/' + booking.id,
            data=dict(
                review=reviewMessage,
                review_point=5
            ),follow_redirects = True)
        self.assertTrue(reviewMessage in rv.data.decode())
        self.assertTrue('리뷰남기기' not in rv.data.decode())

    def test_owner_unperfectreview(self):
        owneremail ='todhm@naver.com'
        renteremail='todhm@nate.com'
        reviewMessage="안녕하세요"
        booking, owner, renter = self.get_booked_owner(
            owneremail=owneremail,
            renteremail=renteremail
            )
        booking.status = 3
        db.session.commit()
        self.client.get('/logout')
        self.login_user(renteremail)
        rv = self.client.post(
            '/add_owner_review/' + booking.id,
            data=dict(
                review=reviewMessage
            ),follow_redirects = True)
        self.assertTrue('리뷰 점수를 입력해주세요.' in rv.data.decode())

    def test_renter_review_template(self):
        owneremail ='todhm@naver.com'
        renteremail='todhm@nate.com'
        booking, owner, renter = self.get_booked_owner(
            owneremail=owneremail,
            renteremail=renteremail
            )
        booking.status = 3
        db.session.commit()
        rv = self.client.get('/reservation/' + booking.id)
        self.assertTrue('리뷰남기기' in rv.data.decode())

    def test_renter_add_review(self):
        owneremail ='todhm@naver.com'
        renteremail='todhm@nate.com'
        reviewMessage="안녕하세요"
        booking, owner, renter = self.get_booked_owner(
            owneremail=owneremail,
            renteremail=renteremail
            )
        booking.status = 3
        db.session.commit()
        rv = self.client.post(
            '/add_renter_review/' + booking.id,
            data=dict(
                review="안녕하세요",
                review_point=5
            ))
        review = RenterReview.query.filter(RenterReview.booking_id==booking.id).first()
        self.assertEqual(review.review,reviewMessage)
        self.assertEqual(review.review_point,5)


    def test_renterreview_rendering(self):
        owneremail ='todhm@naver.com'
        renteremail='todhm@nate.com'
        reviewMessage="안녕하세요"
        booking, owner, renter = self.get_booked_owner(
            owneremail=owneremail,
            renteremail=renteremail
            )
        booking.status = 3
        db.session.commit()
        rv = self.client.post(
            '/add_renter_review/' + booking.id,
            data=dict(
                review=reviewMessage,
                review_point=5
            ),follow_redirects = True)
        self.assertTrue(reviewMessage in rv.data.decode())
        self.assertTrue('리뷰남기기' not in rv.data.decode())

    def test_renter_unperfectreview(self):
        owneremail ='todhm@naver.com'
        renteremail='todhm@nate.com'
        reviewMessage="안녕하세요"
        booking, owner, renter = self.get_booked_owner(
            owneremail=owneremail,
            renteremail=renteremail
            )
        booking.status = 3
        db.session.commit()

        rv = self.client.post(
            '/add_renter_review/' + booking.id,
            data=dict(
                review=reviewMessage
            ),follow_redirects = True)
        self.assertTrue('리뷰 점수를 입력해주세요' in rv.data.decode())


    def test_render_booking_photo(self):
        owneremail ='todhm@naver.com'
        renteremail='todhm@nate.com'
        reviewMessage="안녕하세요"
        booking, owner, renter = self.get_booked_owner(
            owneremail=owneremail,
            renteremail=renteremail
            )
        booking.status = 2
        db.session.commit()
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

        rv = self.client.get('/reservation/'+booking.id)
        self.assertTrue( carbooking_image.imgsrc in rv.data.decode())
        self.remove_image(carbooking_image.image,booking.id,'BOOKING_IMAGE_FOLDER')


    def test_car_search(self):
        address_dict = self.get_address_dict("경기도 안양시 동안구 평촌대로40번길 100")
        today = dt.now() + timedelta(days=1)
        oneweek = dt.now() + timedelta(days=7)
        start_date_str = dt.strftime(today,"%m/%d/%Y")
        end_date_str = dt.strftime(oneweek,"%m/%d/%Y")
        address_dict['startTime']="10:00"
        address_dict['endTime']="12:00"
        address_dict['startDate'] = start_date_str
        address_dict['endDate'] = end_date_str
        rv = self.client.post('/car_search',data = address_dict,follow_redirects=True)
        with self.client.session_transaction() as session:
            session_data = session['search_data']
            self.verify_search_session(session_data,address_dict)
            self.verify_search_page(rv,address_dict)
        address_dict = self.get_address_dict("경기도 안양시 동안구 평촌대로40번길 100")
        address_dict['startTime']="10:00"
        address_dict['endTime']="10:00"
        address_dict['startDate'] = start_date_str
        address_dict['endDate'] = end_date_str
        rv = self.client.post('/',data = address_dict,follow_redirects=True)
        with self.client.session_transaction() as session:
            session_data = session['search_data']
            self.verify_search_session(session_data,address_dict)
            self.verify_search_page(rv,address_dict)




    def test_car_search_with_improper_address(self):
        address_dict = self.get_address_dict("경기도 안양시 동안구 평촌대로40번길 100")
        today = dt.now()
        oneweek = dt.now() + timedelta(days=7)
        start_date_str = dt.strftime(today,"%m/%d/%Y")
        end_date_str = dt.strftime(oneweek,"%m/%d/%Y")
        address_dict['startTime']="10:00"
        address_dict['endTime']="10:00"
        address_dict['startDate'] = start_date_str
        address_dict['endDate'] = end_date_str
        address_dict.pop('address')
        rv = self.client.post('/car_search',data = address_dict,follow_redirects=True)
        self.assertTrue("주소를 입력해주세요." in rv.data.decode())
        rv = self.client.post('/',data = address_dict,follow_redirects=True)
        self.assertTrue("주소를 입력해주세요." in rv.data.decode())

    def test_car_search_with_improper_datetime(self):
        address_dict = self.get_address_dict("경기도 안양시 동안구 평촌대로40번길 100")
        today =  dt.now() + timedelta(days=7)
        oneweek = dt.now()
        start_date_str = dt.strftime(today,"%m/%d/%Y")
        end_date_str = dt.strftime(oneweek,"%m/%d/%Y")
        address_dict['startTime']="10:00"
        address_dict['endTime']="10:00"
        address_dict['startDate'] = start_date_str
        address_dict['endDate'] = end_date_str
        rv = self.client.post('/car_search',data = address_dict,follow_redirects=True)
        self.assertTrue("시간오류" in rv.data.decode())
        rv = self.client.post('/',data = address_dict,follow_redirects=True)
        self.assertTrue("시간오류" in rv.data.decode())
