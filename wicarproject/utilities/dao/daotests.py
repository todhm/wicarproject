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
from carbooking.models import *
from utilities.dao.cardao import CarDao
from utilities.dao.userdao import UserDao
from utilities.dao.bookingdao import BookingDao
from utilities.imaging import save_image
from utilities.testutil import TestUtil
from utilities.timeutil import get_next_week_by_day
from utilities.common import get_price
from utilities.hashutil import encrypt_hash,decrypt_hash
from utilities.flask_tracking.documents import Tracking
from random import randint
from mongoengine.queryset.visitor import Q
from freezegun import freeze_time
from datetime import datetime as dt
from datetime import timedelta
import urllib
import re
import uuid

TEST_UPLOADED_FOLDER='/static/images/test_images'

class DaoTest(TestUtil):
    def setUp(self):
        super().setUp()
        self.testPrice =40000
        owner = self.register_user_with_phone(email='todhm@naver.com',name="테스트")
        self.user=owner
        self.car =self.add_car_without_img(user_id=owner.id,price=self.testPrice)
        self.day_diff=2
        self.weekly_diff = 11
        self.monthly_diff=32
        self.start_time = dt.now()
        self.end_time = dt.now() + timedelta(days=self.day_diff)

    def test_get_car_price(self):
        total_price = CarDao.get_car_price(self.car.id,start_time =self.start_time,end_time=self.end_time)
        price = CarDao.get_median_car_price(self.car.id,start_time =self.start_time,end_time=self.end_time)
        self.assertTrue(self.testPrice*self.day_diff==total_price)
        self.assertTrue(self.testPrice==price)

    def test_get_car_price_with_price_event(self):
        new_price=100000
        BookingDao.add_car_price_schedule(
            car_id=self.car.id,
            start_time=self.start_time,
            end_time=self.end_time,
            price=new_price
            )
        total_price = CarDao.get_car_price(self.car.id,start_time =self.start_time,end_time=self.end_time)
        price = CarDao.get_median_car_price(self.car.id,start_time =self.start_time,end_time=self.end_time)

        self.assertTrue(price==new_price)
        self.assertTrue(total_price==new_price * self.day_diff)

    def test_get_car_price_with_weekly_price(self):
        new_end_time = self.start_time + timedelta(days=self.weekly_diff)
        CarDao.add_longterm_sale(car_id=self.car.id,weekly_discount=10)
        price = CarDao.get_median_car_price(self.car.id,start_time =self.start_time,end_time=new_end_time)
        total_price = CarDao.get_car_price(self.car.id,start_time =self.start_time,end_time=new_end_time)
        self.assertTrue(price==int(0.9*self.testPrice))
        self.assertTrue(total_price==int(0.9*self.testPrice)*self.weekly_diff)

    def test_get_car_price_with_monthly_price(self):
        new_end_time = self.start_time + timedelta(days=self.monthly_diff)
        CarDao.add_longterm_sale(car_id=self.car.id,monthly_discount=30)
        price = CarDao.get_median_car_price(self.car.id,start_time =self.start_time,end_time=new_end_time)
        total_price = CarDao.get_car_price(self.car.id,start_time =self.start_time,end_time=new_end_time)
        self.assertTrue(price==int(0.7*self.testPrice))
        self.assertTrue(total_price==int(0.7*self.testPrice)*self.monthly_diff)


    def test_mixed_price_events(self):
        new_day_diff = 5
        new_end_time = self.start_time + timedelta(days=new_day_diff)
        new_price=100000
        BookingDao.add_car_price_schedule(
            car_id=self.car.id,
            start_time=self.start_time,
            end_time=self.end_time,
            price=new_price
            )
        price = CarDao.get_median_car_price(self.car.id,start_time =self.start_time,end_time=new_end_time)
        total_price = CarDao.get_car_price(self.car.id,start_time =self.start_time,end_time=new_end_time)
        totalPrice = (self.day_diff * self.testPrice) + ((new_day_diff-self.day_diff) * new_price)
        medium_price = int(totalPrice / new_day_diff)
        self.assertTrue(price==medium_price)
        self.assertTrue(total_price==totalPrice)




    def test_mixed_price_event_and_weekly(self):
        new_end_time = self.start_time + timedelta(days=self.weekly_diff)
        new_price=100000
        BookingDao.add_car_price_schedule(
            car_id=self.car.id,
            start_time=self.start_time,
            end_time=new_end_time,
            price=new_price
            )
        CarDao.add_longterm_sale(car_id=self.car.id,weekly_discount=10)
        price = CarDao.get_median_car_price(self.car.id,start_time =self.start_time,end_time=new_end_time)
        total_price = CarDao.get_car_price(self.car.id,start_time =self.start_time,end_time=new_end_time)
        self.assertTrue(price==int(0.9*new_price))
        self.assertTrue(total_price==int(0.9*new_price)*self.weekly_diff)

    def test_mixed_price_event_and_monthly(self):
        new_end_time = self.start_time + timedelta(days=self.monthly_diff)
        new_price=100000
        BookingDao.add_car_price_schedule(
            car_id=self.car.id,
            start_time=self.start_time,
            end_time=new_end_time,
            price=new_price
            )
        CarDao.add_longterm_sale(car_id=self.car.id,monthly_discount=10)
        price = CarDao.get_median_car_price(self.car.id,start_time =self.start_time,end_time=new_end_time)
        total_price = CarDao.get_car_price(self.car.id,start_time =self.start_time,end_time=new_end_time)
        self.assertTrue(price==int(0.9*new_price))
        self.assertTrue(total_price==int(0.9*new_price)*self.monthly_diff)

    def test_add_user_liscence(self):
        user = self.user
        liscence_info=self.return_full_liscence_info()
        with self.app.test_request_context('/'):
            user =UserDao.add_liscence_user(
                user_id=user.id,
                liscence_1=liscence_info.get('liscence_1'),
                liscence_2=liscence_info['liscence_2'],
                liscence_3=liscence_info['liscence_3'],
                liscence_4=liscence_info['liscence_4'],
                birth=liscence_info['birth'],
                serialNumber=liscence_info['serialNumber']
        )

        self.assertTrue(user.liscence_1==liscence_info['liscence_1'])
        self.assertTrue(decrypt_hash(user.liscence_2) == liscence_info['liscence_2'])
        self.assertTrue(decrypt_hash(user.liscence_3) == liscence_info['liscence_3'])
        self.assertTrue(decrypt_hash(user.liscence_4) == liscence_info['liscence_4'])
        self.assertTrue(decrypt_hash(user.birth) == liscence_info['birth'])
        self.assertTrue(decrypt_hash(user.serial) == liscence_info['serialNumber'])

    def test_bookingdao_gbfp_finished_booking(self):
        owner_earning_list = []
        owner_email_list = []
        renter_email_list = []
        owner_price ={}

        for x in range(10):
            owner_email = 'todhm' + str(x+10) + "@nate.com"
            renter_email = "gmlaud" + str(x+10) + "@gmail.com"
            car,user = self.return_user_and_car(owneremail=owner_email, renteremail = renter_email,remainUser=False)
            user_id = user.id
            self.add_card_info(user_id)
            owner = car.user
            account_num = '111222333444'+str(x)
            bank_name="테스트은행"
            self.add_bank(
                user_id=owner.id,
                bank_code_std='001',
                bank_name=bank_name,
                account_num=account_num,
            )
            owner_price[owner.id] = {}
            owner_price[owner.id]['total_earning'] =0
            owner_price[owner.id]['earning_list'] = []
            owner_price[owner.id]['account_num'] = account_num
            owner_price[owner.id]['bank_name'] = bank_name
            self.client.get('/logout')
            for i in range(10):
                booking = self.add_random_booking(
                    car = car,
                    user=user,
                    status=3,
                    start_time=dt.now() + timedelta(days=i),
                    end_time=dt.now() + timedelta(days=i+1),
                    total_price=1000000,insurance_price=1000,
                    owner_earning=randint(10000,50000)
                )
                owner_price[owner.id]['total_earning'] += booking.owner_earning
                owner_price[owner.id]['earning_list'].append(booking.owner_earning)


        start_time = dt.now()
        with freeze_time(dt.now()) as frozen_datetime:
            frozen_datetime.tick(delta=timedelta(days=12))
            end_time = dt.now()
        result = BookingDao.get_booking_for_pay(start_time,end_time)
        for owner_id in result:
            self.assertTrue(result[owner_id]['account_num']==owner_price[owner_id]['account_num'])
            self.assertTrue(result[owner_id]['bank_name']==owner_price[owner_id]['bank_name'])
            self.assertTrue(result[owner_id]['total_earning']==owner_price[owner_id]['total_earning'])
            for x in range(10):
                self.assertTrue(result[owner_id]['booking_list'][x]['owner_earning']==owner_price[owner_id]['earning_list'][x])

    def test_sent_money_list(self):
        owner_list =[]

        for x in range(10):
            owner_email = 'todhm' + str(x+10) + "@nate.com"
            renter_email = "gmlaud" + str(x+10) + "@gmail.com"
            car,user = self.return_user_and_car(owneremail=owner_email, renteremail = renter_email,remainUser=False)
            user_id = user.id
            self.add_card_info(user_id)
            owner = car.user
            account_num = '111222333444'+str(x)
            bank_name="테스트은행"
            self.add_bank(
                user_id=owner.id,
                bank_code_std='001',
                bank_name=bank_name,
                account_num=account_num,
            )
            owner_list.append({})
            owner_list[x]['total_earning'] =0
            owner_list[x]['booking_list'] = []
            owner_list[x]['account_num'] = account_num
            owner_list[x]['ownerId'] = owner.id
            owner_list[x]['owner_phone'] = owner.phone
            owner_list[x]['bank_name'] = bank_name
            for i in range(10):
                booking = self.add_random_booking(
                    car = car,
                    user=user,
                    status=3,
                    start_time=dt.now() + timedelta(days=i),
                    end_time=dt.now() + timedelta(days=i+1),
                    total_price=1000000,insurance_price=1000,
                    owner_earning=randint(10000,50000)
                )
                booking_info = {}
                booking_info['owner_earning'] = booking.owner_earning
                booking_info['id'] = booking.id
                owner_list[x]['total_earning'] += booking.owner_earning
                owner_list[x]['booking_list'].append(booking_info)


        result = BookingDao.send_owner_list_money(owner_list)
        self.assertTrue(result)
        for owner_data in owner_list:
            logList = Tracking.objects.filter(
                Q(__raw__ = {'custom_data.action': 'send_owner_money',
                            'custom_data.user_id' : owner_data['ownerId']})
                ).order_by('-date_created')
            self.assertEqual(len(logList),1)
            self.assertTrue(logList[0].custom_data['total_amount']==owner_data['total_earning'])
            for booking_data in owner_data['booking_list']:
                ownerSend = OwnerSend.query.filter(OwnerSend.booking_id==booking_data['id']).first()
                self.assertTrue(ownerSend.tran_amt==booking_data['owner_earning'])

    def test_update_image(self):
        car = self.return_car_obj()
        car_id = str(car.id)
        test_image_url = "."+TEST_UPLOADED_FOLDER + "/background.jpg"
        old_img_id = self.add_car_image(car_id,test_image_url)
        beforeImage = CarImage.query.first()
        before_image_src = beforeImage.imgsrc
        with freeze_time(dt.now()) as frozen_datetime:
            frozen_datetime.tick(delta=timedelta(seconds=1))
            with open(test_image_url, 'r+b') as f:
                new_img_id = save_image(f,car_id)
        CarDao.update_image(car_id,beforeImage.image_index,new_img_id)
        newImage = CarImage.query.first()
        new_img_src = newImage.imgsrc
        self.assertTrue(old_img_id != new_img_id)
        self.assertTrue(before_image_src != new_img_src)


    #
    # def test_update_filename(self):
    #     car = self.return_car_obj()
    #     car_id = str(car.id)
    #     test_image_url = "."+TEST_UPLOADED_FOLDER + "/background.jpg"
    #     test_image_url2 = "."+TEST_UPLOADED_FOLDER + "/background4.jpg"
    #     self.add_car_image(car_id,test_image_url)
    #     self.add_car_image(car_id,test_image_url2)
    #     result = CarDao.update_carimage_filename()
    #     carImageList = CarImage.query.all()
    #     self.assertTrue(result)
    #     for carImage in carImageList:
    #         with open('.'+carImage.imgsrc, 'r+b') as f3:
    #             self.assertTrue(f3 is not None)
    #         os.remove('.'+carImage.imgsrc)


    #
    #
    # def test_update_booking_filename(self):
    #     car,user = self.return_user_and_car()
    #     card = self.add_card_info(user.id)
    #     booking = self.add_random_booking(car,user)
    #     booking = self.confirm_booking(booking)
    #     test_image_url = "."+TEST_UPLOADED_FOLDER + "/background.jpg"
    #     test_image_url2 = "."+TEST_UPLOADED_FOLDER + "/background4.jpg"
    #     self.add_booking_img(booking,test_image_url)
    #     self.add_booking_img(booking,test_image_url2)
    #     result = BookingDao.update_bookingimage_filename()
    #     self.assertTrue(result)
    #     bookingImageList = BookingImage.query.all()
    #     for bookingImage in bookingImageList:
    #         with open('.'+bookingImage.imgsrc, 'r+b') as f3:
    #             self.assertTrue(f3 is not None)
    #         os.remove('.'+bookingImage.imgsrc)
