import os
import unittest
import sqlalchemy
from flask import Flask,session,url_for,redirect,current_app as app
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime as dt
from datetime import timedelta
from application import create_app ,db,mdb
import unittest
import json
from carbooking.models import *
from caruser.models import *
from carupload.models import *
from flask_testing import TestCase
from utilities.dao.userdao import UserDao
from utilities.dao.cardao import CarDao
from utilities.dao.bookingdao import BookingDao
from utilities.timeutil import get_current_day,get_end_day
from utilities.hashutil import encrypt_hash,decrypt_hash
from utilities.imaging import save_image
from settings import TEST_DB_URI,TEST_MONGO_URI
import urllib
from mongoengine.connection import _get_db
import os
from freezegun import freeze_time

TEST_UPLOADED_FOLDER='/static/images/test_images'

class TestUtil(unittest.TestCase):


    def create_app(self):
        app = create_app(
            SQLALCHEMY_DATABASE_URI = TEST_DB_URI,
            TESTING= True,
            testing=True,
            WTF_CSRF_ENABLED=False,
            UPLOADED_FOLDER = TEST_UPLOADED_FOLDER,
            MONGODB_SETTINGS={'host': TEST_MONGO_URI},
            SQLALCHEMY_MAX_OVERFLOW	=200,
            UPLOADED_IMAGES_URL='/static/images/test_images',
            BOOKING_IMAGE_FOLDER='/static/images/test_images'
            )
        return app


    def setUp(self):
        self.app = self.create_app()
        self.app_context = self.app.app_context()
        self.app_context.push()
        self.userdao = UserDao()
        self.cardao = CarDao()
        self.client = self.app.test_client()
        TEST_UPLOADED_FOLDER='/static/images/test_images'
        self.test_image="."+TEST_UPLOADED_FOLDER + "/background.jpg"
        db.create_all()



    def search_address(self,address):
        apiUrl = '/api/get_address_info'
        data ={}
        data['address'] = address
        rv = self.client.post(apiUrl,
                            data = json.dumps(data),
                            content_type='application/json',
                            follow_redirects=True)
        return json.loads(rv.get_data().decode('utf-8'))


    def verify_data(self,orm,data_dict):
        for key in data_dict:
            self.assertEqual(getattr(orm,key),data_dict[key])

    def verify_address(self,address):
        rv = self.search_address(address)
        self.assertTrue(len(rv) >=1)
        for data in rv:
            self.assertTrue(isinstance(data['address'],str))
            self.assertTrue(isinstance(data['pointX'],float))
            self.assertTrue(isinstance(data['pointY'],float))

    def verify_region(self,region):
        rv = self.search_address(region)
        for data in rv:
            self.assertTrue(isinstance(data['address'],str))
        self.assertTrue(len(rv) >=1)

    def verify_car_basic(self,car,car_data):

        self.assertEqual(car.brand, car_data['brandName'])
        self.assertEqual(car.class_name,car_data['className'])
        self.assertEqual(car.model, car_data['model'])
        self.assertEqual(car.year, car_data['year'])
        self.assertEqual(car.cartype, car_data['cartype'])
        self.assertEqual(car.detail_address,car_data['detail_address'])
        self.assertEqual(car.address,car_data['address']['address'])
        self.assertEqual(car.address,car_data['address']['address'])
        self.assertEqual(car.transmission,car_data['transmission'])

    def register_user(self, username='김희동', email='todhm@nate.com', password='test1234', confirm='test1234'):
        return self.client.post('/signup', data=dict(
            username=username,
            email=email,
            password=password,
            confirm=confirm
            ),
        follow_redirects=True)

    def register_user_with_phone(self,email='todhm@nate.com',name='김희동',phone="01071675299"):
        rv = self.register_user(email=email,username=name)
        userList=User.query.all()
        user  = User.query.filter(User.email==email).first()
        user.phone=phone
        db.session.commit()
        return user

    def login_user(self,email='todhm@nate.com',password='test1234'):
        return self.client.post('/login', data=dict(
            email=email,
            password=password
            ),
        follow_redirects=True)

    def send_code(self,phonenumber='01071675299'):
        return self.client.post('/sendcode', data=dict(
            phonenumber=phonenumber
            ),
        follow_redirects=True)

    def verify_code(self,code="",submit="notresend"):
        return self.client.post('/verifycode', data=dict(
            code=code,
            submit=submit
            ),
        follow_redirects=True)

    def check_mongoData(self,queryName,query_url,codeName):
        query_data = {}
        query_data[queryName] = codeName
        rv2= self.client.get(
        query_url,
        query_string = query_data
        )
        data = json.loads(rv2.get_data().decode('utf-8'))
        self.assertTrue(len(data)>0)
        self.assertTrue(isinstance(data[0]['codeName'],str))

    def return_car_with_coord(self,email="todhm@nate.com",address={'address':'경기도 안양시 동안구 평촌대로40번길 100',
                                                                   'pointX':123.1223321,
                                                                   'pointY':47.1231231}):
        data=dict(
            email=email,
            brandName="현대자동차",
            model="소나타 2017년형",
            year=2010,
            className="소나타",
            cartype="sedan",
            address=address,
            detail_address='샘마을 임광아파트 308동 2402호',
            transmission="auto",
            distance=10000
        )
        return data
    def return_car_without_coord(self):
        data=dict(
            email="todhm@nate.com",
            brandName="현대자동차",
            model="소나타 2017형",
            className="소나타",
            cartype="sedan",
            year=2016,
            address={'address':'경기도 안양시 동안구 평촌대로40번길 100 샘마을 아파트' },
            detail_address='샘마을 임광아파트 308동 2402호',
            transmission="auto",
            distance=10000
        )
        return data

    def return_full_liscence_info(self):
        data = dict(
        liscence_1 = '13',
        liscence_2 = '391933',
        liscence_3 = '33',
        liscence_4 = '31',
        birth='920127',
        serialNumber="U123DF"
        )
        return data

    def return_car_obj(self,email='todhm@naver.com',name="강희명",address={'address':'경기도 안양시 동안구 평촌대로40번길 100',
                                                                   'pointX':123.1223321,
                                                                   'pointY':47.1231231},remainUser=True):

        if not remainUser:
            with self.client.session_transaction() as session:
                if session.get('email'):
                    rv = self.client.get('/logout')
        user = self.register_user_with_phone(email = email,name=name)
        with self.client.session_transaction() as session:
            car_with_coord = self.return_car_with_coord(email=email,address=address)
            user_id = self.userdao.get_user_id(email)
            rv = self.client.post(
            '/api/add_basic_info' ,
                data=json.dumps(car_with_coord),
                content_type='application/json',
                follow_redirects=True
                )
            car = self.cardao.get_car_obj(user_id)
            return car

    def get_caroption_data(self,advance_notice=1,price=40000):
        data = {}
        data['advance_notice'] =advance_notice
        data['price'] = price
        data['plate_num'] = '15 가 2039'
        data['description'] = '이차는 정말 좋습니다. 한마디로 개쩌는 자동차라고 볼 수 있죠. ,ㅇasdfasdfadsi22'
        data['roof_box']=False
        data['hid']=False
        data['led']=True
        data['auto_trunk']=True
        data['leather_seater']=False
        data['room_mirror']=False
        data['seat_6_4']=False
        data['seat_heater_1st']=False
        data['seat_heater_2nd']=False
        data['seat_cooler']=False
        data['high_pass']=False
        data['button_starter']=False
        data['handle_heater']=True
        data['premium_audio']=False
        data['hud']=True
        data['smart_cruz_control']=False
        data['tpms']= False
        data['curtton_airbag']=False
        data['esp']=False
        data['isofix']=False
        data['slope_sleepery']=False
        data['front_collusion']=False
        data['lane_alarm']=True
        data['high_bim']=True
        data['aux_bluetooth']=False
        data['usb']=False
        data['auto_head_light']=False
        data['android_conn']=True
        data['apple_conn']=True
        data['electric_brake']=False
        data['navigation']=False
        data['backword_cam']=False
        data['surround_view_cam']=False
        data['bolt_220']=False
        data['smartphone_charge']=False
        return data

    def get_search_obj(self, address='평촌대로40번길 100',startDate='06/29/2018',
        endDate='07/31/2018',startTime='10:00',endTime='10:00'):
        address_list = self.search_address(address)
        addressObj = address_list[0]
        search_obj = dict(
            address = addressObj['address']
            )
        if 'pointX' in addressObj :
            search_obj['pointX'] = addressObj['pointX']
            search_obj['pointY'] = addressObj['pointY']
        search_obj['startDate'] = startDate
        search_obj['endDate'] = endDate
        search_obj['startTime'] = startTime
        search_obj['endTime'] = endTime
        return search_obj

    def activate_car_without_img(self,address="평촌대로40번길 100",advance_notice=0,email="todhm@naver.com",remainUser=True):
        address_list = self.search_address(address)
        car = self.return_car_obj(address = address_list[0],email=email,remainUser=remainUser)
        data = self.get_caroption_data(advance_notice)
        url = '/api/add_car_option'+ "/" + str(car.id)
        rv2=self.client.post(
                        url,
                        data=json.dumps(data),
                        content_type='application/json',
                        follow_redirects=True
                        )
        car_id = str(car.id)
        rv = self.client.post('/api/activate_car/'+car_id)
        return car
    def activate_car_with_address(self,address="평촌대로40번길 100",advance_notice=1):
        address_list = self.search_address(address)
        car = self.return_car_obj(address = address_list[0])
        data = self.get_caroption_data(advance_notice)
        url = '/api/add_car_option'+ "/" + str(car.id)
        rv2=self.client.post(
                        url,
                        data=json.dumps(data),
                        content_type='application/json',
                        follow_redirects=True
                        )
        car_id = str(car.id)
        test_image_url = "."+TEST_UPLOADED_FOLDER + "/background.jpg"
        with open(test_image_url, 'r+b') as f:
            rv= self.client.post('/api/upload_image/' + car_id, buffered=True,
                               content_type='multipart/form-data',
                               data={'image':f})
        rv = self.client.post('/api/activate_car/'+car_id)
        return car

    def search_car(self,address,startDate='06/29/2018',
        endDate='07/31/2018',startTime='10:00',endTime='10:00'):
        search_obj = self.get_search_obj(
            address,startDate=startDate,endDate=endDate,startTime=startTime,
            endTime=endTime
            )
        rv = self.client.post('/',data=search_obj)


    def get_random_valid_availability(self):
        availability=[ {"dailyAlways":"0"} for i in range(7)]
        availability[1] = {'dailyAlways':"1","start":"0","end":"30"}
        availability[5] = {'dailyAlways':"1","start":"30","end":"120"}

        return availability
    def get_all_day_custom_availability(self):
        availability=[ {"dailyAlways":"0","start":"90","end":"300"} for i in range(7)]
        availability[1] = {'dailyAlways':"1","start":"0","end":"30"}
        availability[5] = {'dailyAlways':"1","start":"30","end":"120"}

        return availability


    def check_random_valid_availability(self,rv,user):
        self.assertTrue(rv.status_code==200)
        user_time_table = UserTime.query.filter(UserTime.user_id==user.id).order_by(UserTime.dow).all()
        self.assertTrue(len(user_time_table)==7)
        self.assertTrue(user_time_table[1].start_time==0)
        self.assertTrue(user_time_table[1].end_time==30)
        self.assertTrue(user_time_table[5].start_time==30)
        self.assertTrue(user_time_table[5].end_time==120)

    def get_card_info(self,user_id,name="내카드",customer_uid='adfasdfadsfsk'):
        card_info= dict(
            name="내카드",
            customer_uid = customer_uid,
            auth_token=encrypt_hash(str(user_id))
        )
        return card_info

    def get_nice_card_info(self,user_id,name="내카드"):
        card_info= dict(
            name="내카드",
            card_1='4364-2007-1641-3305',
            expire_year='2022',
            expire_month='04',
            password='59',
            cvc='457',
            birth='920127',
            auth_token=encrypt_hash(str(user_id))
        )
        return card_info
    def get_nice_seperate_info(self,user_id,name="내카드"):
        card_info= dict(
            name="내카드",
            card_1='4364200716413305',
            expire_year='2022',
            expire_month='04',
            password='59',
            cvc='457',
            birth='920127',
            auth_token=encrypt_hash(str(user_id))
        )
        return card_info


    def get_bank_info(self, bank_code_std='001', bank_name='테스트은행',
        account_num='111222333',account_holder_info='9201011', account_holder_name='테스트'):
        return dict(
            bank_code_std=bank_code_std,
            bank_name=bank_name,
            account_num =account_num,
            account_holder_info=account_holder_info,
            account_holder_name=account_holder_name,
        )

    def add_bank(self,user_id,bank_code_std='001', bank_name='테스트은행',
            account_num='111222333',account_holder_info='9201011',
            account_holder_name='테스트'):
        bank_info = self.get_bank_info(
            bank_code_std=bank_code_std,
            bank_name=bank_name,
            account_num=account_num,
            account_holder_info=account_holder_info,
            account_holder_name=account_holder_name
            )
        bank = UserBank(
            user_id=user_id,
            bank_code_std=bank_info['bank_code_std'],
            bank_name=bank_info['bank_name'],
            account_num = bank_info['account_num'],
            account_holder_info=bank_info['account_holder_info'],
            account_holder_name=bank_info['account_holder_name'],

        )
        db.session.add(bank)
        db.session.commit()
        return bank


    def add_card_info(self,user_id,name="내카드",customer_uid='adfasdfadsfsk'):
        card_data = self.get_card_info(user_id,name=name,customer_uid=customer_uid)
        userCard = UserCard(
            user_id = user_id,
            name=card_data.get('name'),
            customer_uid= card_data.get('customer_uid')
        )
        db.session.add(userCard)
        db.session.commit()
        return userCard


    def add_random_booking(self,car,user,total_price=10000,insurance_price=1000,
        owner_earning=5000,start_time = None,end_time=None,status=0,total_distance=1000):
        start_time = start_time if start_time is not None else dt.now()
        end_time = end_time if end_time is not None else dt.now() + timedelta(hours=3)
        booking = BookingDao.add_booking(
           car_id=car.id,
           renter_id=user.id,
           total_price=total_price,
           insurance_price=insurance_price,
           owner_earning=owner_earning,
           start_time=start_time,
           end_time=end_time,
           status=status,
           total_distance=total_distance
       )
        return booking

    def confirm_booking(self,booking):
        booking.status = 2
        db.session.commit()
        return booking

    def get_booked_car(self,owneremail='todhm@naver.com',renteremail='gmlaud14@nate.com',start_time=None,end_time=None):
        car,user = self.return_user_and_car(owneremail=owneremail, renteremail = renteremail)
        user_id = user.id
        self.add_card_info(user_id)
        booking = self.add_random_booking(car,user,start_time=start_time,end_time=end_time)
        return booking,user,car

    def get_booked_ownercar(self,owneremail='todhm@naver.com',renteremail='gmlaud14@nate.com',start_time=None,end_time=None,total_price=10000,insurance_price=1000,
            owner_earning=5000,status=0,total_distance=1000
            ):
        car,user = self.return_user_and_car(owneremail=owneremail, renteremail = renteremail)
        user_id = user.id
        self.add_card_info(user_id)
        booking = self.add_random_booking(
            car,user,start_time=start_time,end_time=end_time,total_price=total_price,
            insurance_price=insurance_price,owner_earning=owner_earning,status=status,total_distance=total_distance
            )
        self.client.get('/logout')
        self.login_user(email=owneremail)
        owner = UserDao.get_user_obj(owneremail)
        return booking,owner,car

    def add_owner_review(self,booking,owner,review_point=3,review_message='안녕하떼염'):
        booking.status = 3
        db.session.commit()
        ownerReview = OwnerReview(
            booking_id=booking.id,
            owner_id=owner.id,
            review_point=review_point,
            review=review_message
        )
        db.session.add(ownerReview)
        db.session.commit()
        return ownerReview

    def add_renter_review(self,booking,user,review_point=3,review_message='안녕하떼염'):
        booking.status = 3
        db.session.commit()
        review = RenterReview(
            booking_id=booking.id,
            renter_id=user.id,
            review_point=review_point,
            review=review_message
        )
        db.session.add(review)
        db.session.commit()
        return review

    def return_user_and_car(self,owneremail='todhm@naver.com', renteremail='gmlaud14@nate.com',remainUser=True):
        car = self.activate_car_without_img(email=owneremail,remainUser=remainUser)
        rv = self.client.get('/logout')
        user = self.register_user_with_phone(email=renteremail)
        return car,user

    def add_car_with_img(
        self,user_id,file,price=40000,
        address='서울시 중구 명동',detail_address="우리집",lat=123.22020,
        lng=123.292999,distance=100,brand="현대",cartype="sedan",
        class_name="소나타",model="2018년식",year=2018,register_date=None,
        transmission="auto",active=1
        ):
        car = self.add_car_without_img(user_id=user_id,price=price,
        address=address,detail_address=detail_address,lat=lat,
        lng=lng,distance=distance, brand=brand,cartype=cartype,
        class_name=class_name,model=model,year=year,register_date=register_date,
        transmission=transmission, active=active)
        with open(file, 'r+b') as f:
            image_id = save_image(f,car.id)
        self.cardao.add_car_image(car_id=car.id,image_id=image_id,image_index=0)
        return car, image_id
    def add_car_without_img(
        self,user_id,price=40000,
        address='서울시 중구 명동',detail_address="우리집",lat=123.22020,
        lng=123.292999,distance=100,brand="현대",cartype="sedan",
        class_name="소나타",model="2018년식",year=2018,register_date=None,
        transmission="auto",active=1
        ):
        car = self.cardao.add_car(user_id,address,detail_address,lat,lng,distance,brand,
        cartype,class_name,model,year,register_date,transmission,active)
        carData = self.get_caroption_data(price= price)
        self.cardao.add_car_option(car.id,carData)
        return car


    def remove_image(self,image_id,car_id,image_loc='UPLOADED_FOLDER'):
        if not  app.config['AWS_BUCKET']:
            filename_template =  '{}.{}.jpg'.format(car_id,image_id)
            upload_folder=app.config[image_loc]
            file_path = "."+os.path.join(upload_folder,filename_template)
            os.remove(file_path)

    def remove_image_with_path(self,source):
        os.remove(file_path)

    def remove_added_img(self,image_list, added_car_list):
        if not app.config['AWS_BUCKET']:
            for idx,image_id in enumerate(image_list):
                self.remove_image(image_id,added_car_list[idx])

    def add_carprice_schedule(self,car_id,start_time=None,end_time=None,price=10000):
        start_time = start_time if start_time else dt.now()
        end_time = end_time if end_time else dt.now() + timedelta(days=3)
        carPriceSchedule = CarPriceSchedule(
            start_time = start_time,
            end_time= end_time,
            car_id =car_id,
            price = price,
        )
        db.session.add(carPriceSchedule)
        db.session.commit()
        return carPriceSchedule

    def add_car_vacation(self,car_id,start_time=None,end_time=None):
        start_time = start_time if start_time else dt.now()
        end_time = end_time if end_time else dt.now() + timedelta(days=3)
        carVacation = CarVacation(
            start_time = start_time,
            end_time= end_time,
            car_id =car_id,
        )
        db.session.add(carVacation)
        db.session.commit()
        return carVacation


    def create_admin_user(self,name="강희명",email="todhm@naver.com",password='todhmtest1234',phonenumber='01071675299'):
        user = User(
            name=name,
            email=email,
            password=password,
            admin=True,
            phonenumber=phonenumber
            )
        db.session.add(user)
        db.session.commit()
        return user


    def api_post(self,url,data,token=""):

        if token:
            headers={'Authorization': 'Bearer {}'.format(token)}
        else:
            headers={}
        rv = self.client.post(url,
            data=json.dumps(data),
            content_type='application/json',
            headers=headers
            )
        try:
            response = json.loads(rv.data.decode())
            return response
        except:
            return False


    def add_confirmed_booking(self,start_time=None,end_time=None,
            owneremail="todhm@naver.com",renteremail="gmlaud14@nate.com",
            bank_code_std='001', bank_name='테스트은행',account_num='111222333',
            account_holder_info='9201011',account_holder_name='테스트'):
        booking, owner, renter = self.get_booked_owner(
            owneremail=owneremail,
            renteremail=renteremail,
            start_time=start_time,
            end_time=end_time
            )
        rv = self.client.post(
            '/reservation/'+booking.id,
            data = dict(
                confirm='confirm'
                )
            )
        bank = self.add_bank(
            user_id=owner.id,
            bank_code_std=bank_code_std,
            bank_name=bank_name,
            account_num=account_num,
            account_holder_info=account_holder_info,
            account_holder_name=account_holder_name
            )
        return owner,renter,bank
    def add_finished_booking_and_bank(self,start_time=None,end_time=None,
            owneremail="todhm@naver.com",renteremail="gmlaud14@nate.com",
            bank_code_std='001', bank_name='테스트은행',account_num='111222333',
            account_holder_info='9201011',account_holder_name='테스트',total_price=10000,insurance_price=1000,
                    owner_earning=5000,status=0,total_distance=1000):
        booking, owner, renter = self.get_booked_owner(
            owneremail=owneremail,
            renteremail=renteremail,
            start_time=start_time,
            end_time=end_time,
            total_price=10000,
            insurance_price=1000,
            owner_earning=5000,
            status=3,
            total_distance=1000
            )
        bank = self.add_bank(
            user_id=owner.id,
            bank_code_std=bank_code_std,
            bank_name=bank_name,
            account_num=account_num,
            account_holder_info=account_holder_info,
            account_holder_name=account_holder_name
            )
        return owner,bank,booking

    def add_car(self,user_id,address="경기도안양시동안구 평촌대로40번길 100",
        detail_address="지하주차장",lat=123.10202,lng=39.29292,distance=150,brand="현대",cartype="rv",
        class_name="산타페",model="소나타",year=2016,transmission="auto",register_date=None,active=0):

        car = self.cardao.add_car(
        user_id=user_id,address=address,detail_address=detail_address,lat=lat,
        lng=lng,distance=distance,brand=brand,cartype=cartype,
        class_name=class_name,model=model,year=year,register_date=register_date,transmission=transmission,
        active=active
        )
        return car

    def add_car_image(self,car_id,test_image_url):
        with freeze_time(dt.now()) as frozen_datetime:
            with open(test_image_url, 'r+b') as f:
                image_id = save_image(f,car_id)
                #이미지가 성공적으로 저장되었으면 DB에 url저장.
                carImages =CarImage.query.filter(CarImage.car_id ==car_id).filter(CarImage.active==True).order_by(CarImage.image_index).all()
                if image_id:
                    if carImages:
                        last_index = carImages[-1].image_index
                        new_image_index = last_index + 1
                    else:
                        new_image_index = 0
                    carImage = CarImage(
                        car_id = car_id,
                        image = image_id,
                        image_index = new_image_index,
                        active = 1
                    )
                    db.session.add(carImage)
                    db.session.commit()
            frozen_datetime.tick(delta=timedelta(seconds=1))
            return image_id

    def add_booking_img(self,booking,image_url,description="",user_id=None):
        with freeze_time(dt.now()) as frozen_datetime:
            with open(image_url, 'r+b') as f:
                car_id = booking.car_id
                user_id= booking.renter_id if user_id is None else user_id
                user = User.query.filter(User.id==user_id).first()
                user_name= user.name
                image_loc = app.config['BOOKING_IMAGE_FOLDER']
                image_id = save_image(f,booking.id,'BOOKING_IMAGE_FOLDER',image_width=400,image_height=400)
                bookingImage=BookingImage\
                    .query\
                    .filter(BookingImage.booking_id ==booking.id)\
                    .filter(BookingImage.active==True).order_by(BookingImage.image_index.desc()).first()
                if image_id:
                    if bookingImage:
                        last_index = bookingImage.image_index
                        new_image_index = last_index + 1
                    else:
                        new_image_index = 0
                    bookingImage = BookingImage(
                        booking_id = booking.id,
                        sender_id = user_id,
                        image = image_id,
                        description=description,
                        image_index = new_image_index,
                        active = 1
                    )
                    db.session.add(bookingImage)
                    db.session.commit()


    def tearDown(self):
        db.session.remove()
        db.drop_all()
        mdb = _get_db()
        mdb.client.drop_database(mdb)
        self.app_context.pop()
