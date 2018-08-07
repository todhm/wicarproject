import os
import unittest
import sqlalchemy
from flask import current_app as app
from flask_sqlalchemy import SQLAlchemy
from application import create_admin_app, db
from caruser.models import User
from carbooking.models import UserCard, OwnerSend
from caruser.tasks import get_best_cars
from caruser.mongomodels import BestCar
from carupload.models import Car
from carbooking.tasks import change_past
from flask_testing import TestCase
from utilities.dao.userdao import UserDao
from utilities.testutil import TestUtil
from utilities.timeutil import get_current_day, get_end_day
from utilities.hashutil import decrypt_hash
from utilities.flask_tracking.documents import Tracking
from utilities.common import delete_card, register_card
from mongoengine.queryset.visitor import Q
from carbooking.tasks import change_past
from freezegun import freeze_time
from datetime import datetime as dt
from datetime import timedelta
from settings import TEST_DB_URI, TEST_MONGO_URI
import json

TEST_UPLOADED_FOLDER = '/static/images/test_images'


class AdminPageTest(TestUtil):
    def create_app(self):
        app = create_admin_app(
            SQLALCHEMY_DATABASE_URI=TEST_DB_URI,
            TESTING=True,
            testing=True,
            WTF_CSRF_ENABLED=False,
            UPLOADED_FOLDER=TEST_UPLOADED_FOLDER,
            MONGODB_SETTINGS={'host': TEST_MONGO_URI},
            SQLALCHEMY_MAX_OVERFLOW=200,
            UPLOADED_IMAGES_URL='/static/images/test_images',
            BOOKING_IMAGE_FOLDER='/static/images/test_images'
            )
        return app

    def setUp(self):
        super().setUp()
        self.password = "test12345858"

    def test_login_user(self):
        user = self.create_admin_user(password=self.password)
        self.user = user
        response = self.api_post("/auth_login",
            data=dict(
                email=user.email,
                password=self.password
            ))
        self.assertTrue(response['message'] == "success")


    def test_get_payment_list(self):
        user = self.create_admin_user(password=self.password)
        response = self.api_post("/auth_login",
            data=dict(
                email=user.email,
                password=self.password
            ))
        token = response['auth_token']
        car = self.add_car(user_id=user.id,active=1)
        bank = self.add_bank(user_id=user.id)
        start_time = dt.now()
        end_time = dt.now() + timedelta(days=1)
        start_time_str = dt.strftime(start_time,"%Y-%m-%d")
        end_time_str = dt.strftime(end_time,"%Y-%m-%d")
        booking = self.add_random_booking(car=car,user=user,status=3,start_time=start_time,end_time=end_time)
        response = self.api_post("/get_unpaid_data",
            data=dict(
                startDate=start_time_str,
                endDate=end_time_str,
            ),
            token=token)
        self.assertTrue(response['message']=="success")
        self.assertTrue(response['data'][user.id]['bank_name']==bank.bank_name)


    def test_pay_complete(self):
        user=self.create_admin_user(password=self.password)
        response = self.api_post("/auth_login",
            data=dict(
                email=user.email,
                password=self.password
            ))
        token = response['auth_token']
        car = self.add_car(user_id=user.id, active=1)
        bank = self.add_bank(user_id=user.id)
        start_time = dt.now()
        end_time = dt.now() + timedelta(days=1)
        start_time_str = dt.strftime(start_time, "%Y-%m-%d")
        end_time_str = dt.strftime(end_time, "%Y-%m-%d")
        booking = self.add_random_booking(
            car=car,
            user=user,
            status=3,
            start_time=start_time,
            end_time=end_time
        )
        data = []
        data.append({})
        data[0]['ownerId'] = user.id
        data[0]['total_earning'] = booking.owner_earning
        data[0]['booking_list'] = []
        data[0]['account_num'] = bank.account_num
        data[0]['bank_name'] = bank.bank_name
        data[0]['owner_phone'] = user.phone
        data[0]['booking_list'].append({})
        data[0]['booking_list'][0]['owner_earning'] = booking.owner_earning
        data[0]['booking_list'][0]['id'] = booking.id
        response = self.api_post(
            "/pay_complete",
            data=dict(
                checkedList=data,
            ),
            token=token
        )
        self.assertTrue(response['message'] == "success")
