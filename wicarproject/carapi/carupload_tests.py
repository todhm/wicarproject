import os
import unittest
import sqlalchemy
from flask import Flask,session,url_for,redirect
from flask_sqlalchemy import SQLAlchemy
from application import create_app ,db
import unittest
import json
from caruser.models import User, UserBank
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
from utilities.flask_tracking.documents import Tracking
from mongoengine.queryset.visitor import Q
import os


TEST_UPLOADED_FOLDER='/static/images/test_images'

class CaruploadTest(TestUtil):



    def validate_caroption(self,data,carOption):
        for key in data:
            option_data = getattr(carOption,key) if getattr(carOption,key) is not  None else ""
            self.assertEqual(data[key],option_data)

    # def test_mongoDB_api(self):
    #     rv = self.client.get(
    #     '/api/getCarBrand',
    #         content_type='application/json',
    #         follow_redirects=True
    #         )
    #     data = json.loads(rv.get_data().decode('utf-8'))
    #     self.assertTrue(len(data) >50)
    #     self.check_mongoData('brandName','api/getCarClass','기아')
    #     self.check_mongoData('brandName','api/getCarClass','현대')
    #
    #     self.check_mongoData('className','api/getCarModel','K9')
    #     self.check_mongoData('className','api/getCarModel','쏘울')



    def test_carWith_coordinate(self):
        with self.client.session_transaction() as session:
            rv1= self.register_user()
            session['email'] = 'todhm@nate.com'
            session['verification_code'] = '12345'
            rv2 = self.verify_code(code = '123445')
            carWithCoord = self.return_car_with_coord()
            rv = self.client.post(
            '/api/add_basic_info',
                data=json.dumps(carWithCoord),
                content_type='application/json',
                follow_redirects=True
                )
            data = json.loads(rv.get_data().decode('utf-8'))
            user_id = self.userdao.get_user_id(session['email'])
            car = self.cardao.get_car_obj(user_id)
            self.verify_car_basic(car,carWithCoord)

            self.assertAlmostEqual(float(car.lng),carWithCoord['address']['pointX'])
            self.assertAlmostEqual(float(car.lat),carWithCoord['address']['pointY'])


    def test_update_car(self):

        with self.client.session_transaction() as session:
            rv1= self.register_user()
            session['email'] = 'todhm@nate.com'
            session['verification_code'] = '12345'
            rv2 = self.verify_code(code = '123445')
            car_without_coord = self.return_car_without_coord()
            rv = self.client.post(
            '/api/add_basic_info',
                data=json.dumps(car_without_coord),
                content_type='application/json',
                follow_redirects=True
                )
            data = json.loads(rv.get_data().decode('utf-8'))
            user_id = self.userdao.get_user_id(session['email'])
            car = self.cardao.get_car_obj(user_id)
            car_id = car.id
            car_without_coord['brandName'] = "르노삼성"
            car_without_coord['model']="sm5"
            car_without_coord['transmission'] = "manual"
            rv = self.client.post(
            '/api/add_basic_info' + '/'+str(car_id),
                data=json.dumps(car_without_coord),
                content_type='application/json',
                follow_redirects= True
                )
            user_id = self.userdao.get_user_id(session['email'])
            car = self.cardao.get_car_obj(user_id)
            self.verify_car_basic(car,car_without_coord)








    def test_car_without_coordinate(self):
        with self.client.session_transaction() as session:
            self.register_user_with_phone()
            car_without_coord = self.return_car_without_coord()
            session['email'] = 'todhm@nate.com'
            rv = self.client.post(
            '/api/add_basic_info',
                data=json.dumps(car_without_coord),
                content_type='application/json',
                follow_redirects=True
                )
            user_id = self.userdao.get_user_id(session['email'])
            car = self.cardao.get_car_obj(user_id)
            self.verify_car_basic(car,car_without_coord)

            self.assertTrue(isinstance(float(car.lng), float))
            self.assertTrue(isinstance(float(car.lat),float))

    def test_proper_address(self):
        self.verify_address('평촌대로40번길 100')
        self.verify_address('신사동 502')
        self.verify_address('제주시 도령로 129')



    def test_proper_region(self):
        self.verify_region('과천도서관')
        self.verify_region('연세대학교')
        self.verify_region('고려대학교')
        self.verify_region('패스트캠퍼스')


    def test_liscence_addwith_correctemail(self):
        with self.client.session_transaction() as session:
            self.register_user_with_phone('todhm@naver.com')
            session['email'] = 'todhm@naver.com'
            liscence_data = self.return_full_liscence_info()
            rv = self.client.post(
                '/api/add_liscence_info',
                data=json.dumps(liscence_data),
                content_type='application/json',
                follow_redirects=True
            )
            user = self.userdao.get_user_obj(session['email'])
            self.assertEqual(user.liscence_1 , liscence_data['liscence_1'])

    def test_liscence_with_uncomplete(self):
        with self.client.session_transaction() as session:
            self.register_user_with_phone('todhm@naver.com')
            session['email'] = 'todhm@naver.com'
            liscence_data = self.return_full_liscence_info()
            liscence_data.pop('liscence_1')
            rv = self.client.post(
                '/api/add_liscence_info',
                data=json.dumps(liscence_data),
                content_type='application/json',
                follow_redirects=True
            )
            self.assertTrue(json.loads(rv.data.decode())['message'] !="success")

    def test_liscence_addwith_withoutsession(self):
        self.register_user_with_phone(email = 'todhm@naver.com')
        self.client.get('/logout')
        self.register_user_with_phone(email = 'gmlaud14@nate.com')
        liscence_data = self.return_full_liscence_info()
        rv = self.client.post(
            '/api/add_liscence_info',
            data=json.dumps(liscence_data),
            content_type='application/json',
            follow_redirects=True
        )
        with self.client.session_transaction() as session:
            user = self.userdao.get_user_obj('todhm@naver.com')
            self.assertTrue(user.liscence_1 != liscence_data['liscence_1'])


    def test_get_liscence(self):
        self.register_user_with_phone(email = 'todhm@naver.com')
        liscence_data = self.return_full_liscence_info()
        rv = self.client.post(
            '/api/add_liscence_info',
            data=json.dumps(liscence_data),
            content_type='application/json',
            follow_redirects=True
        )
        with self.client.session_transaction() as session:
            rv = self.client.get('/api/get_liscence')
            liscence_json = json.loads(rv.get_data().decode('utf-8'))
            self.assertTrue(liscence_json['liscence_1'] == liscence_data['liscence_1'])
            self.assertTrue(liscence_json['liscence_2'] == liscence_data['liscence_2'])
            self.assertTrue(liscence_json['liscence_3'] == liscence_data['liscence_3'])
            self.assertTrue(liscence_json['liscence_4'] == liscence_data['liscence_4'])
            self.assertTrue(liscence_json['birth'] == liscence_data['birth'])
            self.assertTrue(liscence_json['serialNumber'] == liscence_data['serialNumber'])


    def test_empty_liscence(self):
        self.register_user_with_phone(email = 'todhm@naver.com',name='강희명')
        with self.client.session_transaction() as session:
            rv = self.client.get('/api/get_liscence')
            liscence_json = json.loads(rv.get_data().decode('utf-8'))
            self.assertTrue(liscence_json.get('liscecne_1')is None)






    def test_caroption_add(self):
        car = self.return_car_obj()
        data = self.get_caroption_data()

        url = '/api/add_car_option'+ "/" + str(car.id)
        rv2=self.client.post(
                        url,
                        data=json.dumps(data),
                        content_type='application/json',
                        follow_redirects=True
                        )

        carOption = CarOption.query.filter(CarOption.id==car.id).first()
        self.validate_caroption(data,carOption)



    def test_add_caroption_without_carData(self):
        self.register_user_with_phone(email = 'todhm@naver.com',name='강희명')
        data = self.get_caroption_data()

        rv2=self.client.post('/api/add_car_option/1',
                            data=json.dumps(data),
                            content_type='application/json',
                            follow_redirects=True)
        self.assertTrue(rv2.status_code==403)



    def test_add_caroption_with_unvalid_carData(self):
        car = self.return_car_obj()
        data = self.get_caroption_data()
        data.pop('price')
        url = '/api/add_car_option'+ "/" + str(car.id)
        rv2=self.client.post(
                        url,
                        data=json.dumps(data),
                        content_type='application/json',
                        follow_redirects=True
                        )
        self.assertEqual(rv2.status_code,403)


    def test_update_caroption(self):
        car = self.return_car_obj()
        data = self.get_caroption_data()
        url = '/api/add_car_option'+ "/" + str(car.id)
        rv2=self.client.post(
                        url,
                        data=json.dumps(data),
                        content_type='application/json',
                        follow_redirects=True
                        )
        data['price'] = 400000
        data['description']='자동차가 업드레이드되서 돈을 조금 더 받아야할것 같습니다. '
        rv3 = self.client.post(
                        url,
                        data=json.dumps(data),
                        content_type='application/json',
                        follow_redirects=True
                        )
        carOption = CarOption.query.filter(CarOption.id==car.id).first()
        self.validate_caroption(data,carOption)

    def test_get_caroption(self):
        car = self.return_car_obj()
        data = self.get_caroption_data()
        url = '/api/add_car_option'+ "/" + str(car.id)
        rv2=self.client.post(
                        url,
                        data=json.dumps(data),
                        content_type='application/json',
                        follow_redirects=True
                        )
        url = '/api/get_car_option'+ "/" + str(car.id)
        carOption = CarOption.query.filter(CarOption.id==car.id).first()
        rv3 = self.client.get(
                        url,
                        content_type='application/json',
                        follow_redirects=True
                        )
        json_data = json.loads(rv3.get_data().decode('utf-8'))
        self.validate_caroption(json_data,carOption)


    def test_empty_caroption(self):
        car = self.return_car_obj()
        data = self.get_caroption_data()
        url = '/api/get_car_option'+ "/" + str(car.id)
        carOption = CarOption.query.filter(CarOption.id==car.id).first()
        rv3 = self.client.get(
                        url,
                        content_type='application/json',
                        follow_redirects=True
                        )
        json_data = json.loads(rv3.get_data().decode('utf-8'))
        self.assertTrue(isinstance(json_data,dict))

    def test_add_proper_image(self):
        car = self.return_car_obj()
        car_id = str(car.id)
        test_image_url = "."+TEST_UPLOADED_FOLDER + "/background.jpg"
        with open(test_image_url, 'r+b') as f:
            rv= self.client.post('/api/upload_image/' + car_id, buffered=True,
                               content_type='multipart/form-data',
                               data={'image':f})
            carImage = CarImage.query.filter(CarImage.car_id==car_id).first()
            imgUrl =json.loads(rv.get_data().decode('utf-8'))['imgList']
            self.assertTrue(len(imgUrl)==1)
            self.assertTrue(carImage.active ==1)
            self.assertTrue(carImage.image_index == 0)
            with open("."+carImage.imgsrc,"r+b") as f2:
                self.assertTrue(f2 is not None )
        self.remove_image(carImage.image,car.id)

    def test_update_image(self):
        car = self.return_car_obj()
        car_id = str(car.id)
        test_image_url = "."+TEST_UPLOADED_FOLDER + "/background.jpg"
        with freeze_time(dt.now()) as frozen_datetime:
            with open(test_image_url, 'r+b') as f:
                rv1= self.client.post('/api/upload_image/' + car_id, buffered=True,
                                   content_type='multipart/form-data',
                                   data={'image':f})
                imgUrl =json.loads(rv1.get_data().decode('utf-8'))['imgList']
                carImage = CarImage.query.filter(CarImage.car_id==car_id).first()
                with open("."+carImage.imgsrc,"r+b") as f:
                    self.assertTrue(f is not None )
                self.remove_image(carImage.image,car.id)


            frozen_datetime.tick(delta=timedelta(hours=1))
            with open(test_image_url, 'r+b') as f2:
                rv2 = self.client.post('/api/update_image/' + car_id, buffered=True,
                                   content_type='multipart/form-data',
                                   data={'image':f2,'image_index':0})
                imgUrl2 =json.loads(rv2.get_data().decode('utf-8'))['imgList']

        carImage = CarImage.query.filter(CarImage.car_id==car_id).first()
        self.assertTrue(len(imgUrl)==1)
        self.assertTrue(carImage.active ==1)
        self.assertTrue(carImage.image_index == 0)
        print(imgUrl,imgUrl2)
        self.assertTrue(imgUrl[0]['url'] != imgUrl2[0]['url'])
        with open("."+carImage.imgsrc,"r+b") as f:
            self.assertTrue(f is not None )
        self.remove_image(carImage.image,car.id)

    def test_update_image_multiple_times(self):
        car = self.return_car_obj()
        car_id = str(car.id)
        test_image_url = "."+TEST_UPLOADED_FOLDER + "/background.jpg"
        with freeze_time(dt.now()) as frozen_datetime:
            with open(test_image_url, 'r+b') as f:
                rv1= self.client.post('/api/upload_image/' + car_id, buffered=True,
                                   content_type='multipart/form-data',
                                   data={'image':f})
                imgUrl =json.loads(rv1.get_data().decode('utf-8'))['imgList']
                carImage = CarImage.query.filter(CarImage.car_id==car_id).first()
                self.remove_image(carImage.image,car.id)

            frozen_datetime.tick(delta=timedelta(hours=1))
            with open(test_image_url, 'r+b') as f2:
                rv2 = self.client.post('/api/update_image/' + car_id, buffered=True,
                                   content_type='multipart/form-data',
                                   data={'image':f2,'image_index':0})
                imgUrl2 =json.loads(rv2.get_data().decode('utf-8'))['imgList']
                carImage = CarImage.query.filter(CarImage.car_id==car_id).first()
                self.remove_image(carImage.image,car.id)

            frozen_datetime.tick(delta=timedelta(hours=1))
            with open(test_image_url, 'r+b') as f2:
                rv3 = self.client.post('/api/update_image/' + car_id, buffered=True,
                                   content_type='multipart/form-data',
                                   data={'image':f2,'image_index':'0'})
                imgUrl3 =json.loads(rv3.get_data().decode('utf-8'))['imgList']
                carImage = CarImage.query.filter(CarImage.car_id==car_id).first()
                self.remove_image(carImage.image,car.id)

        carImage = CarImage.query.filter(CarImage.car_id==car_id).first()
        self.assertTrue(len(imgUrl)==1)
        self.assertTrue(carImage.active ==1)
        self.assertTrue(carImage.image_index == 0)
        self.assertTrue(imgUrl[0]['url'] != imgUrl2[0]['url'])
        self.assertTrue(imgUrl[0]['url'] != imgUrl3[0]['url'])
        self.assertTrue(imgUrl2[0]['url'] != imgUrl3[0]['url'])


    def test_add_multiple_valid_image(self):
        car = self.return_car_obj()
        car_id = str(car.id)
        test_image_url = "."+TEST_UPLOADED_FOLDER + "/background.jpg"
        test_image_url2 = "."+TEST_UPLOADED_FOLDER + "/background4.jpg"
        with freeze_time(dt.now()) as frozen_datetime:
            with open(test_image_url, 'r+b') as f:
                rv1 =self.client.post('/api/upload_image/' + car_id, buffered=True,
                                   content_type='multipart/form-data',
                                   data={'image':f})

            frozen_datetime.tick(delta=timedelta(seconds=1))


            with open(test_image_url2, 'r+b') as f2:
                rv2 = self.client.post('/api/upload_image/' + car_id, buffered=True,
                                   content_type='multipart/form-data',
                                   data={'image':f2,'image_index':1})


        imgUrl1 =json.loads(rv1.get_data().decode('utf-8'))['imgList']
        imgUrl2 =json.loads(rv2.get_data().decode('utf-8'))['imgList']
        self.assertTrue(len(imgUrl1)==1)
        self.assertTrue(len(imgUrl2)==2)

        for idx,img in enumerate(imgUrl2):
            with open( "."+img['url'], 'r+b') as f3:
                self.assertTrue(f3 is not None)
                self.assertTrue(img['image_index'] ==idx)
            os.remove("."+img['url'])


    @freeze_time("Jan 14th, 2020", tick=True)
    def test_get_car_img(self):
        car = self.return_car_obj()
        car_id = str(car.id)
        test_image_url =  "."+TEST_UPLOADED_FOLDER + "/background.jpg"
        with freeze_time(dt.now()) as frozen_datetime:
            with open(test_image_url, 'r+b') as f:
                rv1= self.client.post('/api/upload_image/' + car_id, buffered=True,
                                   content_type='multipart/form-data',
                                   data={'image':f})
            frozen_datetime.tick(delta=timedelta(seconds=1))
            with open(test_image_url, 'r+b') as f2:
                rv2 = self.client.post('/api/upload_image/' + car_id, buffered=True,
                                   content_type='multipart/form-data',
                                   data={'image':f2,'car_index':1})
        img_response = json.loads(self.client.get('/api/get_images/'+car_id).get_data().decode('utf-8'))
        self.assertTrue(img_response['message']=="success")
        self.assertTrue(len(img_response['imgList'])==2)

        for idx,img in enumerate(img_response['imgList']):
            with open("."+img['url'],"r+b") as f3:
                self.assertTrue(img['image_index']==idx)
                self.assertTrue(f3 is not None )
            os.remove("."+img['url'])





    def test_remove_img(self):
        car = self.return_car_obj()
        car_id = str(car.id)
        test_image_url = "."+TEST_UPLOADED_FOLDER + "/background.jpg"
        with open(test_image_url, 'r+b') as f:
            rv= self.client.post('/api/upload_image/' + car_id, buffered=True,
                               content_type='multipart/form-data',
                               data={'image':f})
        removeUrl={}
        removeUrl['image_index'] = 0

        rv = self.client.post('/api/remove_image/' + car_id,
                                data=json.dumps(removeUrl),
                                content_type='application/json',
                                follow_redirects= True
                                )
        carImage = CarImage.query.filter(CarImage.car_id==car_id).filter(CarImage.active==False).all()
        self.assertTrue(len(carImage)==1)
        self.assertTrue(rv.status_code==200)
        for carimg in carImage:
            self.remove_image(carimg.image,car_id)


    @freeze_time("Jan 14th, 2020", tick=True)
    def test_remove_multiple_img(self):
        car = self.return_car_obj()
        car_id = str(car.id)
        test_image_url = "."+TEST_UPLOADED_FOLDER + "/background.jpg"
        test_image_url2 = "."+TEST_UPLOADED_FOLDER + "/background4.jpg"
        with freeze_time(dt.now()) as frozen_datetime:
            with open(test_image_url, 'r+b') as f:
                rv1= self.client.post('/api/upload_image/' + car_id, buffered=True,
                                   content_type='multipart/form-data',
                                   data={'image':f})
            frozen_datetime.tick(delta=timedelta(hours=1))
            with open(test_image_url2, 'r+b') as f2:
                rv2 = self.client.post('/api/upload_image/' + car_id, buffered=True,
                                   content_type='multipart/form-data',
                                   data={'image':f2})
                imgUrl =json.loads(rv2.get_data().decode('utf-8'))['imgList']

        removeUrl={}
        removeUrl['image_index'] = 0
        for img in imgUrl:
            os.remove("."+img['url'])

        with freeze_time(dt.now()) as frozen_datetime:
            rv = self.client.post('/api/remove_image/' + car_id,
                                    data=json.dumps(removeUrl),
                                    content_type='application/json',
                                    follow_redirects= True
                                    )
            removeUrl['image_index'] = 1
            frozen_datetime.tick(delta=timedelta(hours=1))
            rv2 = self.client.post('/api/remove_image/' + car_id,
                                    data=json.dumps(removeUrl),
                                    content_type='application/json',
                                    follow_redirects= True
                                    )
        carImage = CarImage.query.filter(CarImage.car_id==car_id).filter(CarImage.active==False).all()
        self.assertTrue(len(carImage)==2)
        self.assertTrue(rv.status_code==200)
        self.assertTrue(rv2.status_code==200)

    @freeze_time("Jan 14th, 2020", tick=True)
    def test_add_invalid_img(self):
        car = self.return_car_obj()
        car_id = str(car.id)
        test_image_url = "."+TEST_UPLOADED_FOLDER + "/hm.jpg"
        with open(test_image_url, 'r+b') as f:
            rv1= self.client.post('/api/upload_image/' + car_id, buffered=True,
                               content_type='multipart/form-data',
                               data={'image':f})
        data = json.loads(rv1.data.decode())
        self.assertTrue(data['message']=="fail")
        carImage = CarImage.query.filter(CarImage.car_id==car_id).all()
        self.assertTrue(len(carImage)==0)


    def test_get_inactive_car(self):
        car = self.return_car_obj()
        car_id = str(car.id)
        rv = self.client.get('/api/get_images/'+car_id)
        data = json.loads(rv.data.decode())
        self.assertTrue(data['active']==False)

    def test_get_active_car(self):
        car = self.return_car_obj()
        car_id = str(car.id)
        self.assertTrue(car.active ==0)
        rv = self.client.post('/api/activate_car/'+car_id)
        rv = self.client.get('/api/get_images/'+car_id)
        data = json.loads(rv.data.decode())
        self.assertTrue(data['active']==True)

    def test_car_activate(self):
        car = self.return_car_obj()
        car_id = str(car.id)
        self.assertTrue(car.active ==0)
        rv = self.client.post('/api/activate_car/'+car_id)
        self.assertTrue("success" in rv.get_data().decode('utf-8'))
        car = Car.query.filter(Car.id==car_id).first()
        self.assertTrue(rv.status_code ==200)
        self.assertTrue(car.active ==1)

    #한사용자가 여러대의 차량을 등록해놓고 사진을 업데이트 시키면 다른자동차의 사진이 없어지는 문제를 확인하기 위한 테스트.
    def test_update_multiple_images(self):
        car = self.return_car_obj()
        car_id = str(car.id)
        test_image_url = "."+TEST_UPLOADED_FOLDER + "/background.jpg"
        test_image_url2 = "."+TEST_UPLOADED_FOLDER + "/background4.jpg"
        with freeze_time(dt.now()) as frozen_datetime:
            with open(test_image_url, 'r+b') as f:
                rv1 =self.client.post('/api/upload_image/' + car_id, buffered=True,
                                   content_type='multipart/form-data',
                                   data={'image':f})
            frozen_datetime.tick(delta=timedelta(hours=1))
            with open(test_image_url2, 'r+b') as f2:
                rv2 = self.client.post('/api/upload_image/' + car_id, buffered=True,
                                   content_type='multipart/form-data',
                                   data={'image':f2,'image_index':1})

        car2 = self.return_car_obj(remainUser= True)
        car_2id = str(car2.id)
        with freeze_time(dt.now()) as frozen_datetime:
            with open(test_image_url, 'r+b') as f:
                rv1 =self.client.post('/api/upload_image/' + car_2id, buffered=True,
                                   content_type='multipart/form-data',
                                   data={'image':f})
            frozen_datetime.tick(delta=timedelta(hours=1))
            with open(test_image_url2, 'r+b') as f2:
                rv2 = self.client.post('/api/upload_image/' + car_2id, buffered=True,
                                   content_type='multipart/form-data',
                                   data={'image':f2})

            frozen_datetime.tick(delta=timedelta(hours=1))
            with open(test_image_url2, 'r+b') as f:
                rv2 = self.client.post('/api/update_image/' + car_2id, buffered=True,
                                   content_type='multipart/form-data',
                                   data={'image':f,'image_index':0})
        carImage = CarImage.query.filter(CarImage.car_id==car_id).filter(CarImage.active==True).filter(CarImage.image_index==0).first()
        car2Image = CarImage.query.filter(CarImage.car_id==car_2id).filter(CarImage.active==True).filter(CarImage.image_index==0).first()

        with open("."+carImage.imgsrc,"r+b") as f:
            self.assertTrue(f is not None )
        with open("."+car2Image.imgsrc,"r+b") as f:
            self.assertTrue(f is not None )


    #차량등록시 사용자들이 알맞은 위치에 존재하고 있는지 확인
    def test_get_last_status(self):
        #차량 처음등록일경우.
        self.register_user_with_phone(email = 'todhm@naver.com')
        rv = self.client.get('/api/getLastStatus')
        data = json.loads(rv.data.decode())
        self.assertEqual(data['stage_name'], ["자동차 등록","면허*계좌등록","세부사항조정","사진 등록","최종확인"])


    #은행계좌등록.
    def test_bank_account(self):
        # 제대로된 계좌가 아닌경우.
        user = self.register_user_with_phone(email='todhm@naver.com')
        bank_info = self.get_bank_info()
        origin_birth = bank_info['account_holder_info']
        original_account = bank_info['account_num']
        bank_info['account_holder_info'] = origin_birth[1:]
        rv = self.client.post(
            '/api/add_bank_account',
            data=json.dumps(bank_info),
            content_type='application/json'
            )
        result = json.loads(rv.data.decode())
        self.assertTrue(result['message']!="success")
        self.assertEqual(rv.status_code,400)


    #은행계좌등록.
    def test_get_bank_account(self):
        user = self.register_user_with_phone(email='todhm@naver.com')
        bank = self.add_bank(user.id)
        rv = self.client.get('/api/get_bank_account')
        bank_info = json.loads(rv.data.decode())
        bank_info.pop('message')
        self.verify_data(bank,bank_info)
        # 제대로된 계좌가 아닌경우.



    #가격불러오기.
    def test_get_car_price(self):
        car  = self.activate_car_without_img()
        rv = self.client.get("/api/get_car_price/"+car.id)
        response = json.loads(rv.data.decode())
        self.assertTrue(car.caroption.price==response['ordinaryPrice'])
        self.assertTrue(0==response['weeklyDiscount'])
        self.assertTrue(0==response['monthlyDiscount'])

    #가격 및 주별 월별 할인율 추가
    def test_add_car_ordinary_price(self):
        car  = self.activate_car_without_img()
        price_info = dict(
            ordinaryPrice=5000,
            weeklyDiscount=10,
            monthlyDiscount=30
        )
        rv = self.client.post(
            '/api/add_car_ordinary_price/'+car.id,
            data=json.dumps(price_info),
            content_type='application/json'
            )
        response = json.loads(rv.data.decode())
        self.assertTrue(response['message']=="success")
        self.assertTrue(price_info['ordinaryPrice']==car.caroption.price)
        self.assertTrue(price_info['weeklyDiscount']==car.caroption.weekly_discount)
        self.assertTrue(price_info['monthlyDiscount']==car.caroption.monthly_discount)
