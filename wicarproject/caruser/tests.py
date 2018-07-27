import os
import unittest
import sqlalchemy
from flask import Flask,session,url_for,redirect,current_app as app
from flask_sqlalchemy import SQLAlchemy
from application import create_app ,db
import unittest
import json
from caruser.models import User, UserBank
from carbooking.models import UserCard,OwnerSend
from caruser.tasks import get_best_cars
from caruser.mongomodels import BestCar
from carupload.models import Car
from carbooking.tasks import change_past
from flask_testing import TestCase
from utilities.dao.userdao import UserDao
from utilities.testutil import TestUtil
from utilities.timeutil import get_current_day,get_end_day
from utilities.hashutil import decrypt_hash
from utilities.flask_tracking.documents import Tracking
from utilities.common import delete_card,register_card
from mongoengine.queryset.visitor import Q
from carbooking.tasks import change_past
from freezegun import freeze_time
from datetime import datetime as dt
from datetime import timedelta
from settings import TEST_DB_URI
import urllib
import re


class UserTest(TestUtil):
    def setUp(self):
        super().setUp()
        self.test_car_list = test_car_list = [
            {"brand":"현대","class_name":"제네시스","price":10000,'review_point':5,"booking_count":4},
            {"brand":"기아","class_name":"오피러스","price":10000,'review_point':3,"booking_count":10},
            {"brand":"삼성","class_name":"sm7","price":10000, 'review_point':2,"booking_count":1},
        ]


    def verify_card_info(self,userCard,card_info):
        self.assertTrue(userCard.name == card_info['name'])
        self.assertTrue(userCard.customer_uid == card_info['customer_uid'])


    def test_proper_user(self):
        rv = self.register_user('김희동','todhm@nate.com','123456io','123456io')
        self.assertEqual(len(User.query.all()), 1)
        with self.client.session_transaction() as session:
            self.assertEqual(session["email"], 'todhm@nate.com')
            self.assertEqual(type(session['user_id']),str)


    def test_duplicate_user(self):
        rv1 = self.register_user()
        rv2 = self.register_user()
        self.assertEqual(len(User.query.all()), 1)

    def test_strange_username(self):
        rv1 = self.register_user(username="b'sdfa'df'")
        self.assertEqual(len(User.query.all()), 1)

    def test_spanish(self):
        rv = self.register_user(username="España")
        self.assertEqual(len(User.query.all()), 1)

    def test_logout(self):
        rv = self.register_user('김희동','todhm@nate.com','123456io','123456io')
        self.assertEqual(len(User.query.all()), 1)
        rv2 = self.client.get('/logout')
        with self.client.session_transaction() as session:
            self.assertTrue(session.get('email') is None )



    #
    # def test_user_with_phonecode(self):
    #     rv = self.register_user()
    #     rv2 = self.send_code()
    #     with self.client.session_transaction() as session:
    #         self.assertEqual(session.get("phonenumber"),"01071675299")
    #
    # def test_user_with_correct_verify_code(self):
    #     rv = self.register_user()
    #     rv2 = self.send_code()
    #     with self.client.session_transaction() as session:
    #         self.assertTrue(session.get("verification_code") is not None)
    #         self.assertEqual(session.get("phonenumber"),"01071675299")
    #         rv3 = self.verify_code(code = session.get("verification_code"))
    #         self.assertTrue( "Wi-CAR에서 당신에게 딱맞는 차를 찾아가세요" in rv3.data.decode('utf-8'))
    #         registered_phone = self.userdao.get_user_phone(session.get("email"))
    #         self.assertEqual(registered_phone,"01071675299")
    #
    # def test_user_with_incorrect_verify_code(self):
    #     rv = self.register_user()
    #     rv2 = self.send_code()
    #     rv3 = self.verify_code(code = "123445")
    #     with self.client.session_transaction() as session:
    #         self.assertTrue("인증번호 입력하기" in rv3.data.decode('utf-8'))
    #         registered_phone = self.userdao.get_user_phone(session.get("email"))
    #         self.assertEqual(registered_phone,None)

    def test_index_search(self):
        search_obj = self.get_search_obj()
        rv = self.client.post('/',data=search_obj,follow_redirects=True)
        self.assertEqual(rv.status_code,200)
        self.assertTrue(search_obj['address'] in rv.data.decode('utf-8'))
        with self.client.session_transaction() as session:
            self.assertTrue('search_data' in session)


    def test_session_remained(self):
        search_obj = self.get_search_obj()
        rv = self.client.post('/',data=search_obj,follow_redirects=True)
        with self.client.session_transaction() as session:
            self.assertTrue(
                isinstance(session.get('search_data').get('address'),str)
                )
            self.assertTrue(
                isinstance(float(session.get('search_data').get('pointX')),float)
            )
    # 카드가 등록되있으면 등록된 카드가 등록되어있지 않으면 등록되지 않는 카드정보가 나타남.
    def test_account_info_page_with_card(self):
        user = self.register_user_with_phone(email='todhm@naver.com')
        rv = self.client.get('/account_info')
        self.assertTrue('카드등록'  in rv.data.decode())
        self.assertTrue('계좌등록'  in rv.data.decode())
        userCard = self.add_card_info(user.id)
        bank = self.add_bank(user.id)
        rv = self.client.get('/account_info')
        self.assertTrue(userCard.name in rv.data.decode())


    def test_card_add_account_page(self):
        user = self.register_user_with_phone(email='todhm@naver.com')
        rv = self.client.post(
            "/account_info",
            data = self.get_nice_seperate_info(user.id),
            follow_redirects=True,
        )
        response = rv.data.decode()
        userCard = UserCard.query.filter(UserCard.user_id == user.id).first()
        self.assertTrue(userCard.name in response)
        self.assertTrue(userCard.name == self.get_nice_card_info(user.id)['name'])
        tracking = Tracking.objects.filter(__raw__ ={'custom_data.user_id':user.id}).order_by('-date_created').first()
        self.assertTrue(tracking.custom_data['action']=='add_card')
        delete_card(userCard.customer_uid)



    def test_card_add_invalid_account_page(self):
        user = self.register_user_with_phone(email='todhm@naver.com')
        card_info = self.get_nice_seperate_info(user.id)
        card_info['card_1']=1902
        rv = self.client.post(
            "/account_info",
            data = card_info,
            follow_redirects=True,
        )
        response = rv.data.decode()
        userCard = UserCard.query.filter(UserCard.user_id == user.id).first()
        self.assertTrue(userCard is None)



    def test_card_modify_account_page(self):
        user = self.register_user_with_phone(email='todhm@naver.com')
        rv = self.client.post(
            "/account_info",
            data = self.get_nice_seperate_info(user.id),
            follow_redirects=True,
        )
        userCard = UserCard.query.filter(UserCard.user_id == user.id).first()
        card_name="jordan"
        rv = self.client.post(
            "/account_info",
            data = dict(
                name=card_name,
                birth="920127",
                card_1="9411612625333873",
                expire_year="2024",
                expire_month="05",
                cvc="944",
                password="59"
            ),
            follow_redirects=True,
        )
        response = rv.data.decode()
        userCard = UserCard.query.filter(UserCard.user_id == user.id).first()
        print(userCard.name)
        self.assertTrue(userCard.name ==card_name)
        self.assertTrue(card_name in response)
        tracking = Tracking.objects.filter(__raw__ ={'custom_data.user_id':user.id}).order_by('-date_created').first()
        self.assertTrue(tracking.custom_data['action']=='modify_card')
        delete_card(userCard.customer_uid)



    def test_card_invalid_modify_account_page(self):
        user = self.register_user_with_phone(email='todhm@naver.com')
        rv = self.client.post(
            "/account_info",
            data = self.get_nice_seperate_info(user.id),
            follow_redirects=True,
        )
        card_name="jordan"
        rv = self.client.post(
            "/account_info",
            data = dict(
                name=card_name,
                card_1="1122612625333873",
                expire_year="2024",
                expire_month="05",
                cvc="944",
                password="59"
            ),
            follow_redirects=True,
        )
        response = rv.data.decode()
        userCard = UserCard.query.filter(UserCard.user_id == user.id).first()
        self.assertTrue(userCard.name ==self.get_nice_seperate_info(user.id)['name'])
        self.assertTrue(self.get_nice_seperate_info(user.id)['name'] in response)
        tracking = Tracking.objects.filter(__raw__ ={'custom_data.user_id':user.id}).order_by('-date_created').first()
        self.assertTrue(tracking.custom_data['action']=='add_card')
        delete_card(userCard.customer_uid)



    # 계좌정보를 제대로 등록시켰을떄와 아닐경우 테스트.
    def test_bank_add(self):
        # 제대로된 계좌가 아닌경우.
        user = self.register_user_with_phone(email='todhm@naver.com')
        bank_info = self.get_bank_info()
        origin_birth = bank_info['account_holder_info']
        original_account = bank_info['account_num']
        bank_info['account_holder_info'] = origin_birth[1:]
        rv = self.client.post('/register_bank',data = bank_info,follow_redirects=True)
        self.assertTrue('생년월일 7자리나 사업자등록번호가 필요합니다.' in rv.data.decode())
        bank_info['account_holder_info'] = origin_birth
        bank_info['account_num'] = original_account[1:]

        #제대로된 계좌가 맞는 경우.
        bank_info['account_num'] = original_account
        rv = self.client.post('/register_bank',data=bank_info,follow_redirects=True)
        bank = UserBank.query.filter_by(user_id = user.id).first()
        self.assertTrue(bank.to_json['bank_num'] in rv.data.decode())
        self.assertTrue(bank.account_holder_info==bank_info['account_holder_info'])
        self.assertTrue(bank.account_num==bank_info['account_num'])
        self.assertTrue(bank.account_holder_name==bank_info['account_holder_name'])
        self.assertTrue(bank.bank_code_std==bank_info['bank_code_std'])

        logList = Tracking.objects.filter(
            Q(__raw__ = {'custom_data.action': 'add_bank'})
            ).order_by('-date_created')
        self.assertEqual(len(logList),1)

        #계좌를 수정하는 경우.
        bank_info['bank_code_std'] = '088'
        bank_info['account_num']='110339922410'
        bank_info['account_holder_info'] = '9201271'
        bank_info['account_holder_name'] = '강희명'
        rv = self.client.post('/register_bank', data=bank_info,follow_redirects=True)
        bank = UserBank.query.filter_by(user_id = user.id).first()
        self.assertTrue(bank.account_num==bank_info['account_num'])
        self.assertTrue(bank.account_holder_name==bank_info['account_holder_name'])
        self.assertTrue(bank.bank_code_std==bank_info['bank_code_std'])

        logList = Tracking.objects.filter(
            Q(__raw__ = {'custom_data.action': 'modify_bank'})
            ).order_by('-date_created')
        self.assertEqual(len(logList),1)


    #제대로 이미지가 등록되어있으면 등록 순서대로 자동차가 나타남.
    def test_get_best_cars(self):
        user1 = self.register_user_with_phone()
        test_image_url = "."+app.config['UPLOADED_FOLDER'] + "/background.jpg"
        image_list = []
        added_car_list = []
        for test_car in self.test_car_list:
            car,image_id = self.add_car_with_img(
                user1.id,test_image_url, brand=test_car['brand'],
                class_name=test_car['class_name'], price=test_car['price']
            )
            added_car_list.append(car.id)
            image_list.append(image_id)

        get_best_cars()
        bestCar = BestCar.objects.order_by('-register_date')[0]
        car_list = bestCar['car_list']
        rv = self.client.get('/')
        page = rv.data.decode()
        self.assertTrue(len(self.test_car_list)==len(car_list))
        for idx,car in enumerate(car_list):
            self.assertTrue(car['brand'] in [ testcar['brand'] for testcar in self.test_car_list])
            self.assertTrue(car['class_name'] in [ testcar['class_name'] for testcar in self.test_car_list])
            self.assertTrue(car['price'] in [ testcar['price'] for testcar in self.test_car_list])
            self.assertTrue(car['bookingCount']==0)

        self.remove_added_img(image_list, added_car_list)



    #리뷰가 있으면 평균 평점이 높은 순서대로 데이터가 저장됨.
    def test_bestcar_order_by_review(self):
        owner = self.register_user_with_phone(email='todhm@nate.com')
        self.client.get('/logout')
        renter = self.register_user_with_phone(email='todhm@naver.com')
        test_image_url = "."+app.config['UPLOADED_FOLDER'] + "/background.jpg"
        image_list = []
        added_car_list = []
        booking_list = []
        for test_car in self.test_car_list:
            car,image_id = self.add_car_with_img(
                owner.id,test_image_url, brand=test_car['brand'],
                class_name=test_car['class_name'], price=test_car['price']
            )
            booking = self.add_random_booking(car,renter)
            booking.status = 2
            db.session.commit()
            self.add_owner_review(booking,owner,review_point=test_car['review_point'])
            added_car_list.append(car.id)
            image_list.append(image_id)

        get_best_cars()
        bestCar = BestCar.objects.order_by('-register_date')[0]
        car_list = bestCar['car_list']
        rv = self.client.get('/')
        page = rv.data.decode()

        self.assertTrue(len(self.test_car_list)==len(car_list))
        for idx,car in enumerate(car_list):
            self.assertTrue(car['brand'] ==self.test_car_list[idx]['brand'])
            self.assertTrue(car['class_name']==self.test_car_list[idx]['class_name'])
            self.assertTrue(car['price']==self.test_car_list[idx]['price'])
            self.assertTrue(car['bookingCount']==1)
            self.assertTrue(car['review_point']==self.test_car_list[idx]['review_point'])

        self.remove_added_img(image_list, added_car_list)



    #booking Count가 많은 순서로 데이터를 가져옴!
    def test_bestcar_order_by_reviewCount(self):
        owner = self.register_user_with_phone(email='todhm@nate.com')
        self.client.get('/logout')
        renter = self.register_user_with_phone(email='todhm@naver.com')
        test_image_url = "."+app.config['UPLOADED_FOLDER'] + "/background.jpg"
        image_list = []
        added_car_list = []
        booking_list = []
        for test_car in self.test_car_list:
            car,image_id = self.add_car_with_img(
                owner.id,test_image_url, brand=test_car['brand'],
                class_name=test_car['class_name'], price=test_car['price']
            )
            for i in range(test_car['booking_count']):
                booking = self.add_random_booking(car,renter)
                booking.status = 2
                db.session.commit()
                self.add_owner_review(booking,owner,review_point=3)
            added_car_list.append(car.id)
            image_list.append(image_id)

        get_best_cars()
        bestCar = BestCar.objects.order_by('-register_date')[0]
        car_list = bestCar['car_list']
        rv = self.client.get('/')
        page = rv.data.decode()
        self.assertTrue(len(self.test_car_list)==len(car_list))
        sorted_test_car = sorted(self.test_car_list,key=lambda x:-x['booking_count'])
        for idx,car in enumerate(car_list):
            self.assertTrue(car['brand'] ==sorted_test_car[idx]['brand'])
            self.assertTrue(car['class_name']==sorted_test_car[idx]['class_name'])
            self.assertTrue(car['price']==sorted_test_car[idx]['price'])
            self.assertTrue(car['bookingCount']==sorted_test_car[idx]['booking_count'])
            self.assertTrue(car['review_point']==3)
        self.remove_added_img(image_list, added_car_list)


    def test_earning_page(self):
        owner_name="르브론제임스"
        renter_name='하메스 로드리게스'
        renter = self.register_user_with_phone(email="todhm@nate.com", name=renter_name)
        self.client.get('/logout')
        owner = self.register_user_with_phone(email='todhm@naver.com',name=owner_name)
        car = self.add_car_without_img(user_id=owner.id, price=10000)
        bank = self.add_bank(owner.id)
        start_time = dt.now()
        end_time = dt.now() + timedelta(hours=12)
        booking = self.add_random_booking(car=car,user=renter,start_time=start_time,end_time=end_time)
        booking.status=2
        db.session.commit()
        with freeze_time(dt.now()) as frozen_datetime:
            frozen_datetime.tick(delta=timedelta(hours=14))
            change_past()

        rv = self.client.get('/earning')
        self.assertTrue( car.brand in rv.data.decode())
        self.assertTrue( car.class_name in rv.data.decode())
        self.assertTrue( str(booking.owner_earning) in rv.data.decode())


    def test_add_bank_in_earning_page(self):
        user = self.register_user_with_phone(email="todhm@nate.com",name='테스트')
        bank_info = self.get_bank_info()
        origin_birth = bank_info['account_holder_info']
        original_account = bank_info['account_num']
        bank_info['account_holder_info'] = origin_birth[1:]
        rv = self.client.post('/register_bank',data = bank_info,follow_redirects=True, headers={'Referer': '/earning'})
        self.assertTrue('생년월일 7자리나 사업자등록번호가 필요합니다.' in rv.data.decode())

        #제대로된 계좌가 맞는 경우.
        bank_info['account_holder_info'] = origin_birth
        rv = self.client.post('/register_bank',data=bank_info,follow_redirects=True, headers={'Referer': '/earning'})
        bank = UserBank.query.filter_by(user_id = user.id).first()
        self.assertTrue(bank.account_holder_info==bank_info['account_holder_info'])
        self.assertTrue(bank.account_num==bank_info['account_num'])
        self.assertTrue(bank.account_holder_name==bank_info['account_holder_name'])
        self.assertTrue(bank.bank_code_std==bank_info['bank_code_std'])

        logList = Tracking.objects.filter(
            Q(__raw__ = {'custom_data.action': 'add_bank'})
            ).order_by('-date_created')
        self.assertEqual(len(logList),1)

        #계좌를 수정하는 경우.
        bank_info['bank_code_std'] = '088'
        bank_info['account_num']='110339922410'
        bank_info['account_holder_info'] = '9201271'
        bank_info['account_holder_name'] = '강희명'
        rv = self.client.post('/register_bank', data=bank_info,follow_redirects=True, headers={'Referer': '/earning'})
        bank = UserBank.query.filter_by(user_id = user.id).first()
        self.assertTrue(bank.account_num==bank_info['account_num'])
        self.assertTrue(bank.account_holder_name==bank_info['account_holder_name'])
        self.assertTrue(bank.bank_code_std==bank_info['bank_code_std'])

        logList = Tracking.objects.filter(
            Q(__raw__ = {'custom_data.action': 'modify_bank'})
            ).order_by('-date_created')
        self.assertEqual(len(logList),1)

    def test_recipt_page(self):
        owner_name="르브론제임스"
        renter_name='하메스 로드리게스'
        renter = self.register_user_with_phone(email="todhm@nate.com", name=renter_name)
        self.client.get('/logout')
        owner = self.register_user_with_phone(email='todhm@naver.com',name=owner_name)
        car = self.add_car_without_img(user_id=owner.id)
        bank = self.add_bank(owner.id,bank_code_std='088', bank_name='신한은행',
                account_num='110339922410',account_holder_info='9201271',
                account_holder_name='강희명')
        start_time = dt.now()
        end_time = dt.now() + timedelta(hours=12)
        booking = self.add_random_booking(
            car=car,user=renter,start_time=start_time,end_time=end_time,
            owner_earning=5000
            )
        booking.status=2
        db.session.commit()
        with freeze_time(dt.now()) as frozen_datetime:
            frozen_datetime.tick(delta=timedelta(hours=14))
            change_past()
        owner_send = OwnerSend.query.first()
        rv = self.client.get("/owner_send/"+owner_send.id)
        self.assertTrue( str(owner_send.tran_amt) in  rv.data.decode())
        self.assertTrue( owner_send.wd_bank_name in rv.data.decode())
        self.assertTrue( owner_send.wd_account_holder_name in rv.data.decode())
        self.assertTrue(owner_send.account_num_masked in rv.data.decode())
        self.assertTrue(str(owner_send.booking.total_distance) in rv.data.decode())

    def test_add_user_liscence(self):
        user = self.register_user_with_phone(email="todhm@nate.com")
        rv = self.client.post('/register_liscence', data=self.return_full_liscence_info(),follow_redirects=True)
        self.assertTrue(user.liscence_1 == user.liscence_1)
        self.assertTrue(user.liscence_1 in rv.data.decode())
        logList = Tracking.objects.filter(
            Q(__raw__ = {'custom_data.action': 'add_user_liscence'})
            ).order_by('-date_created')
        self.assertEqual(len(logList),1)

    def test_add_invalid_user_liscence(self):
        user = self.register_user_with_phone(email="todhm@nate.com")
        original_data = self.return_full_liscence_info()
        for key in original_data:
            new_data = original_data.copy()
            new_data.pop(key)
            rv = self.client.post('/register_liscence', data=new_data,follow_redirects=True)
            logList = Tracking.objects.filter(
                Q(__raw__ = {'custom_data.action': 'add_user_liscence'})
                ).order_by('-date_created')
            self.assertEqual(len(logList),0)
