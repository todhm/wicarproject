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
from carupload.models import CarOption,Car,CarImage
from carbooking.tasks import cancel_overtime_booking, cancel_overtime, change_past_booking, change_past
from carbooking.models import UserTime, VacationData,UserCard, Payment,CarBooking,Message, OwnerSend, OwnerReview, RenterReview
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

class UserInfoTest(TestUtil):

    def test_renter_review_get(self):
        today = dt.now()
        booking,user,car = self.get_booked_car(owneremail='todhm@naver.com',renteremail='todhm@nate.com')
        renter_review = self.add_renter_review(booking,user,review_point=3)
        rv = self.client.get('/api/get_user_renterreview/' + user.id)
        result_obj = json.loads(rv.data.decode())
        first_review = result_obj['renter_review_list'][0]
        self.assertEqual(result_obj['renter_rate'] ,3)
        self.assertEqual(first_review['point'], renter_review.review_point)
        self.assertEqual(first_review['message'], renter_review.review)
        self.assertEqual(first_review['reviewer_user_id'], booking.car.user.id)
        self.assertEqual(first_review['register_year'], today.year)
        self.assertEqual(first_review['register_month'], today.month)
        self.assertEqual(first_review['register_day'], today.day)
        self.assertEqual(first_review['reviewer_name'], booking.car.user.name)


    def test_owner_review_get(self):
        today = dt.now()
        booking,owner,car = self.get_booked_ownercar(owneremail='todhm@naver.com',renteremail='todhm@nate.com')
        owner_review = self.add_owner_review(booking,owner,review_point=3)
        rv = self.client.get('/api/get_user_ownerreview/' + owner.id)
        result_obj = json.loads(rv.data.decode())
        first_review = result_obj['owner_review_list'][0]
        self.assertEqual(result_obj['owner_rate'] ,3)
        self.assertEqual(first_review['point'], owner_review.review_point)
        self.assertEqual(first_review['message'], owner_review.review)
        self.assertEqual(first_review['reviewer_user_id'], booking.renter.id)
        self.assertEqual(first_review['register_year'], today.year)
        self.assertEqual(first_review['register_month'], today.month)
        self.assertEqual(first_review['register_day'], today.day)
        self.assertEqual(first_review['reviewer_name'], booking.renter.name)


    def test_get_userinfo(self):
        booking,owner,car = self.get_booked_ownercar(owneremail='todhm@naver.com',renteremail='todhm@nate.com')
        rv = self.client.get('/api/get_user_info/' + owner.id)
        result_obj = json.loads(rv.data.decode())
        self.assertEqual(result_obj['user_name'],owner.name)
        self.assertEqual(result_obj['register_year'],owner.register_date.year)
        self.assertEqual(result_obj['register_month'],owner.register_date.month)
        self.assertEqual(result_obj['register_day'],owner.register_date.day)
        self.assertEqual(result_obj['user_id'],owner.id)

    def test_get_carinfo(self):
        booking,owner,car = self.get_booked_ownercar(owneremail='todhm@naver.com',renteremail='todhm@nate.com')
        booking.status = 3
        db.session.commit()
        rv = self.client.get('/api/get_user_carinfo/' + owner.id)
        result_obj = json.loads(rv.data.decode())
        first_car = result_obj['car_list'][0]
        self.assertEqual(first_car['brand'],car.brand)
        self.assertEqual(first_car['class_name'],car.class_name)
        self.assertEqual(first_car['price'],car.caroption.price)
