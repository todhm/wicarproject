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
from carupload.models import CarOption,Car,CarImage
from carbooking.models import *
from utilities.testutil import TestUtil
from mongoengine.queryset.visitor import Q
from freezegun import freeze_time
from datetime import datetime as dt
from datetime import timedelta
import urllib
import re
import uuid


class UtilTest(TestUtil):
    def setUp(self):
        super().setUp()
        self.name="강희명"
        self.email="todhm@naver.com"
        self.password="test12345858"


    def test_error_util(self):
        self.assertTrue(response.get('email'))
