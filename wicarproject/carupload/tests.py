import os
import unittest
import sqlalchemy
from flask import Flask,session,url_for,redirect
from flask_sqlalchemy import SQLAlchemy
from application import create_app ,db
import unittest
import json
from caruser.models import User
from carupload.models import CarOption,Car,CarImage
from flask_testing import TestCase
from utilities.dao.userdao import UserDao
from utilities.dao.cardao import CarDao
from utilities.testutil import TestUtil
from freezegun import freeze_time
from datetime import datetime as dt
from datetime import timedelta
from settings import TEST_DB_URI,MONGO_URI
import urllib



TEST_UPLOADED_FOLDER='/static/images/test_images'

class CarUploadViewTest(TestUtil):



    def test_deactivate_car(self):
        car = self.activate_car_without_img()
        rv = self.client.get("/deactivate_car/"+str(car.id),follow_redirects=True)
        self.assertTrue("미등록" in rv.data.decode())
        returned_car = Car.query.filter(Car.active==False).first()
        self.assertTrue(returned_car.id == car.id)
