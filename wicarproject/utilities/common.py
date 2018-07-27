from flask import current_app,request,session
from application import db
from datetime import datetime as dt
from sqlalchemy import func, distinct
from sqlalchemy.orm import lazyload
import requests
import json
from datetime import timedelta,date
from carbooking.models import UserCard, CarBooking, Payment, Message
from utilities.smsutil import send_sms,send_payment_error,send_lms
from utilities.hashutil import decrypt_hash, return_card_number
from itertools import product
import time
from iamport import Iamport
import uuid
from flask_wtf import FlaskForm,Form

class BaseForm(Form):
    def __iter__(self):
        token = self.csrf_token
        yield token

        field_names = {token.name}
        for cls in self.__class__.__bases__:
            for field in cls():
                field_name = field.name
                if field_name not in field_names:
                    field_names.add(field_name)
                    yield self[field_name]

        for field_name in self._fields:
            if field_name not in field_names:
                yield self[field_name]

def get_bank_token():
    ENDPOINT = 'https://testapi.open-platform.or.kr/oauth/2.0/token'
    data = dict(
        scope='oob',
        client_id = current_app.config.get('BANK_API_KEY'),
        client_secret = current_app.config.get("BANK_API_SECRET"),
        grant_type='client_credentials'
    )
    r = requests.post(ENDPOINT,data = data)
    return r

def verify_bank_data(bankForm, auth_code):
    time_format =  dt.strftime(dt.now(),'%Y%m%d%H%M%S')
    headers = {
        'Content-Type':"application/json",
        'Accept': 'application/json'
    }
    headers.update({"Authorization":"Bearer " + auth_code})
    url = ' https://testapi.open-platform.or.kr/v1.0/inquiry/real_name'
    data = dict(
        bank_code_std=bankForm.bank_code_std.data,
        account_num=bankForm.account_num.data,
        account_holder_info=bankForm.account_holder_info.data,
        tran_dtime=time_format
    )
    response = requests.post(url, data=json.dumps(data), headers=headers)
    return response

def add_reivew_process(reviewForm,RenterReview,booking_id):
    review_validate =  reviewForm.validate()
    if review_validate and not renter_review:
        renter_review = RenterReview(
            booking_id=booking_id,
            renter_id=renter_id,
            review_point=reviewForm.review_point.data,
            review=reviewForm.review.data
            )
        db.session.add(renter_review)
        db.session.commit()
        return redirect(url_for('carbooking_app.reservation_page',booking_id=booking_id))
    elif not review_validate:
        review_error = list(reviewForm.errors.items())[0][1][0]
        return redirect(url_for('carbooking_app.reservation_page',booking_id=booking_id,review_error=review_error))


def get_count(table,filter_query):
    main_query = db.session\
        .query(table)\
        .options(lazyload('*'))\
        .filter(filter_query)\
        .statement.with_only_columns([func.count()])\
        .order_by(None)
    count = db.session.execute(main_query).scalar()
    return count


def handle_message(messageForm,booking,sender_id,receiver_id,
    receiver_phone,sender_name,sender_img, receiver_name,now_time):
    message_error=""
    if messageForm.validate_on_submit():
        message = Message(
            sender_id = sender_id,
            receiver_id = receiver_id,
            booking_id = booking.id,
            message = messageForm.message.data,
            register_date = now_time
        )
        db.session.add(message)
        db.session.commit()

        if session.get(receiver_phone):
            last_time_str = session[receiver_phone]
            last_time_message = dt.strptime(last_time_str,'%Y-%m-%d %H:%M')
            # 저번 메세지 전송 후  3시간이상 알림을 보내지 않았을 경우.
        if ((session.get(receiver_phone)) and \
                ((now_time -last_time_message).total_seconds()/3600 >= 3)) or \
           (not session.get(receiver_phone)):
            request._tracking_data = {
                'user_id':sender_id,
                'booking_id':booking.id,
                'sender_id': sender_id,
                'sender_name': sender_name,
                'sender_img': sender_img,
                'receiver_id':receiver_id,
                'receiver_name':receiver_name,
                'action':'message'
            }
            if not current_app.config['TESTING']:
                body = '새로운 Wi-CAR 메세지가 도착하였습니다.'
                send_sms(receiver_phone, body)

        session[receiver_phone] = dt.strftime(now_time,'%Y-%m-%d %H:%M')
    else:
        message_error = list(messageForm.errors.items())[0][1][0]
    return message_error



def get_price(price,start_time,end_time):
    td = end_time -start_time
    days,hours = td.days, td.seconds//3600
    days = 1 if days==0 else days
    total_price = days * price
    if hours >=12:
        total_price += price
    return total_price

def get_cancellation_level(booking_time,start_time):
    now_time = dt.now()
    time_from_booking = now_time - booking_time
    time_from_start = start_time - now_time
    hours_pass = round(time_from_booking.total_seconds() / 3600)

    if hours_pass <= 1:
        return -3
    if time_from_start.days < 1:
        return -6
    if time_from_start.days >=1 and time_from_start.days < 7 :
        return -5
    elif time_from_start.days >=7:
        return -4


def handle_confirm_booking(booking,userCard,owner,renter_name=None, error=None,
    renter_img=None, owner_name=None,owner_img=None,renter_phone=None,
    owner_phone=None):

    start_time_fmt = dt.strftime(booking.start_time,'%Y-%m-%d')
    if not current_app.config['TESTING'] :
        iamport = Iamport(
            imp_key='{}'.format(current_app.config['IAMPORT_API_KEY']),
            imp_secret='{}'.format(current_app.config['IAMPORT_SECRET_KEY'])
            )

        payload = {
                'merchant_uid': booking.id ,
                'customer_uid':userCard.customer_uid,
                'amount': booking.total_price
            }

        #결제성공시 카드저장/ 결제테이블에 데이터 삽입.
        try:
            response = iamport.pay_again(**payload)
            if not response.get('fail_reason'):
                booking.status = 2
                payment = Payment(
                    booking_id=booking.id,
                    mid=response['merchant_uid'],
                    tid=response.get('pg_tid'),
                    price=response.get('amount'),
                    register_date=dt.fromtimestamp(response.get('paid_at'))
                )
                db.session.add(payment)
                db.session.commit()
                request._tracking_data = {
                    'user_id':owner.id,
                    'booking_id': booking.id,
                    'renter_name': renter_name,
                    'renter_img': renter_img,
                    'owner_name': owner_name,
                    'owner_img':owner_img,
                    'owner_id': owner.id,
                    'renter_id': booking.renter_id,
                    'total_price': response['amount'],
                    'owner_earning': booking.owner_earning,
                     'action':'booking_confirm'
                     }
                send_sms(owner_phone,'{} Wi-CAR예약이 완료되었습니다.'.format(start_time_fmt))
                send_sms(renter_phone,'Wi-CAR: {}님이 예약을 수락하여 {} 예약이 완료되었습니다.'.format(owner_name, start_time_fmt))
            else:
                error = "{}고객님측 사정으로 인해 예약을 진행할 수 없습니다.".format(renter_name)
                message = response.get('fail_reason')
                send_payment_error(renter_phone,message)

        except KeyError:
            error = KeyError.message

        except Iamport.ResponseError as e:
            message = e.message
            if "F112" in message or "F113" in message or "한도" in message:
                error = "{}고객님측 사정으로 인해 예약을 진행할 수 없습니다.".format(renter_name)
                send_payment_error(renter_phone,message)

            else:
                error = e.message

            # 응답 에러 처리
        except Iamport.HttpError as http_error:
            error = http_error.reason
            # HTTP not 200 응답 에러 처리
        except Exception as e:
            error = e

    else:
        booking.status = 2
        request._tracking_data = {
            'user_id':owner.id,
            'booking_id': booking.id,
            'renter_name': renter_name,
            'renter_img': renter_img,
            'owner_name': owner_name,
            'owner_img':owner_img,
            'owner_id': owner.id,
            'renter_id': booking.renter_id,
            'total_price': booking.total_price,
            'owner_earning': booking.owner_earning,
             'action':'booking_confirm'
             }
        payment = Payment(
            booking_id=booking.id,
            mid='asdfasfasd',
            tid='adfasfasd',
            price=booking.total_price,
            register_date=dt.now()
        )
        db.session.add(payment)
        db.session.commit()
    return error

def convert_wtf_error(result,form):
    result['message']="fail"
    error_list = []
    for field, errors in form.errors.items():
        for error in errors:
            error_list.append(error)
    result['errorMessage'] = error_list[0]
    return result

def convert_events_time(data):
    start_time = dt.strptime(data['start_time'],'%Y-%m-%d')
    start_time = start_time.replace(hour=0,minute=0,second=0)
    end_time = dt.strptime(data['end_time'],'%Y-%m-%d')
    end_time = end_time.replace(hour=23,minute=59,second=59)
    return start_time,end_time


def handle_cancel_request(price, booking, error, owner, owner_name=None,
    owner_phone=None,renter_phone=None ,owner_img=None, renter_name=None,
     renter_img=None, now_time=dt.now()):

    start_time_fmt = dt.strftime(booking.start_time,'%Y-%m-%d')
    if current_app.config['TESTING']:
        request._tracking_data = {
            'user_id':booking.renter_id,
            'booking_id':booking.id,
            'owner_id':owner.id,
            'owner_name':owner_name,
            'owner_img':owner_img,
            'renter_id':booking.renter_id,
            'renter_img':renter_img,
            'renter_name':renter_name,
            'cancel_price':price*(-1),
            'status':booking.status,
             'action':'cancel_booking'
         }
        if price > 0:
            payment = Payment(
                booking_id=booking.id,
                mid='asdfasdfasdfd',
                tid='adfsadfsadfd',
                price=price * (-1),
                register_date=now_time,
                is_cancel=True
            )
            db.session.add(payment)
            db.session.commit()

    else:
        iamport = Iamport(
            imp_key='{}'.format(current_app.config['IAMPORT_API_KEY']),
            imp_secret='{}'.format(current_app.config['IAMPORT_SECRET_KEY'])
            )
        try:
            if price >0:
                response = iamport.cancel(u'취소하는 이유', merchant_uid=booking.id,amount=price)
                if not response.get('fail_reason'):
                    body = 'Wi-CAR: {}고객님의 요청으로 인해 {} 예약이 취소되었습니다.'.format(renter_name,start_time_fmt)
                    send_sms(owner_phone,body)
                    body = 'Wi-CAR예약이 취소되었습니다.{}원의 환불금액이 발생하였습니다.'.format(response['amount'])
                    send_sms(renter_phone,body)
                    payment = Payment(
                        booking_id=booking.id,
                        mid=response['merchant_uid'],
                        tid=response.get('pg_tid'),
                        price=response['amount'] * (-1),
                        register_date=dt.fromtimestamp(response.get('cancelled_at')),
                        is_cancel=True
                    )
                    db.session.add(payment)
                    request._tracking_data = {
                        'user_id':booking.renter_id,
                        'booking_id':booking.id,
                        'owner_id':owner.id,
                        'owner_name':owner_name,
                        'owner_img':owner_img,
                        'renter_id':booking.renter_id,
                        'renter_img':renter_img,
                        'renter_name':renter_name,
                        'cancel_price':response['amount'] * (-1),
                        'status':booking.status,
                         'action':'cancel_booking'
                         }
                    db.session.commit()
                else:
                    error = response.get('fail_reason')
            else:
                db.session.commit()
                body = 'Wi-CAR: {}고객님의 요청으로 인해 예약이 취소되었습니다.'.format(renter_name)
                send_sms(owner_phone,body)

        except Iamport.ResponseError as e:
            error= e.message  # 에러난 이유를 알 수 있음
        except Iamport.HttpError as http_error:
            error =  http_error.reason # HTTP not 200 에러난 이유를 알 수 있음
    return error

def handle_owner_cancel(price, booking, error, owner, owner_name=None,
    owner_phone=None,renter_phone=None ,owner_img=None, renter_name=None,
     renter_img=None, now_time=dt.now(),status = -7):
    start_time_fmt = dt.strftime(booking.start_time,'%Y-%m-%d')
    if current_app.config['TESTING']:
        payment = Payment(
            booking_id=booking.id,
            mid='asdfasdfasdfd',
            tid='adfsadfsadfd',
            price=price * (-1),
            register_date=now_time,
            is_cancel=True
        )
        db.session.add(payment)
        db.session.commit()
        request._tracking_data = {
            'user_id':owner.id,
            'booking_id':booking.id,
            'owner_id':owner.id,
            'owner_name':owner_name,
            'owner_img':owner_img,
            'renter_id':booking.renter_id,
            'renter_img':renter_img,
            'renter_name':renter_name,
            'cancel_price':price*(-1),
            'status':booking.status,
             'action':'cancel_booking'
             }
    else:
        iamport = Iamport(
            imp_key='{}'.format(current_app.config['IAMPORT_API_KEY']),
            imp_secret='{}'.format(current_app.config['IAMPORT_SECRET_KEY'])
            )
        try:
            response = iamport.cancel(u'취소하는 이유', merchant_uid=booking.id,amount=price)
            if not response.get('fail_reason'):
                body = 'wicar 예약 취소. {}님이 예약을 취소하여 {}예약이 취소되었습니다. \n'.format(owner_name,start_time_fmt)
                body += '{}원의 환불금액이 발생하였습니다.'.format(response['amount'])
                send_lms(renter_phone,'Wi-CAR예약 취소',body)
                body = 'Wi-CAR예약이 취소되었습니다'
                send_sms(owner_phone,body)
                payment = Payment(
                    booking_id=booking.id,
                    mid=response['merchant_uid'],
                    tid=response.get('pg_tid'),
                    price=response['amount'] * (-1),
                    register_date=dt.fromtimestamp(response.get('cancelled_at')),
                    is_cancel=True
                )
                booking.status = status
                db.session.add(payment)
                request._tracking_data = {
                    'user_id':owner.id,
                    'booking_id':booking.id,
                    'owner_id':owner.id,
                    'owner_name':owner_name,
                    'owner_img':owner_img,
                    'renter_id':booking.renter_id,
                    'renter_img':renter_img,
                    'renter_name':renter_name,
                    'cancel_price':response['amount'] * (-1),
                    'status':booking.status,
                     'action':'cancel_booking'
                     }
                db.session.commit()
            else:
                error = response.get('fail_reason')
        except Iamport.ResponseError as e:
            error= e.message  # 에러난 이유를 알 수 있음
        except Iamport.HttpError as http_error:
            error =  http_error.reason # HTTP not 200 에러난 이유를 알 수 있음
        return error


def register_user(self,**kwargs):
    url = '{}subscribe/customers/{}'.format(self.imp_url,kwargs.get('customer_uid'))
    for key in ['amount', 'card_number', 'expiry', 'birth', 'pwd_2digit']:
        if key not in kwargs:
            raise KeyError('Essential parameter is missing!: %s' % key)
    return self._post(url, kwargs)

def delete_user(self,**kwargs):
    url = '{}subscribe/customers/{}'.format(self.imp_url,kwargs.get('customer_uid'))
    for key in ['customer_uid']:
        if key not in kwargs:
            raise KeyError('Essential parameter is missing!: %s' % key)
    headers = self.get_headers()
    response = self.requests_session.delete(url, headers=headers)
    return response


def register_card(birth,password,expire_month,expire_year,card_number,customer_uid,user_id,action="add_card"):
    expiry = expire_year + '-' + expire_month
        # 테스트용 값
    payload = {
        'customer_uid':customer_uid ,
        'amount': 0,
        'card_number': card_number,
        'expiry': expiry,
        'birth': birth,
        'pwd_2digit': password,
        'customer_uid':customer_uid
    }
    Iamport.register_card = register_user
    iamport = Iamport(
        imp_key='{}'.format(current_app.config['IAMPORT_API_KEY']),
        imp_secret='{}'.format(current_app.config['IAMPORT_SECRET_KEY'])
        )
    #결제성공시 카드저장/ 결제테이블에 데이터 삽입.
    try:
        response = iamport.register_card(**payload)
        if not response.get('fail_reason'):
            return True,"success"
        else:
            return False,"카드등록실패"
    except KeyError:
        error = KeyError.message
        return False,error

    except Iamport.ResponseError as e:
        message = e.message
        return False,message
        # 응답 에러 처리
    except Iamport.HttpError as http_error:
        print(http_error,http_error.reason)
        error = http_error.reason
        return False,error
        # HTTP not 200 응답 에러 처리
    except Exception as e:
        error = e
        return False,e



def delete_card(customer_uid):
    Iamport.delete_card = delete_user
    iamport = Iamport(
        imp_key='{}'.format(current_app.config['IAMPORT_API_KEY']),
        imp_secret='{}'.format(current_app.config['IAMPORT_SECRET_KEY'])
        )
    #결제성공시 카드저장/ 결제테이블에 데이터 삽입.
    try:
        response = iamport.delete_card(customer_uid=customer_uid)
        return response,True
    except KeyError:
        error = KeyError.message
        return False,error

    except Iamport.ResponseError as e:
        message = e.message
        return False,message
        # 응답 에러 처리
    except Iamport.HttpError as http_error:
        error = http_error.reason
        return False,error
        # HTTP not 200 응답 에러 처리
    except Exception as e:
        error = e
        return False,e



def get_liscence_region_choices():
    regionStr = '''
                경기
                서울
                경기북부
                강원
                충북
                충남
                전북
                경북
                경남
                제주
                대구
                인천
                광주
                대전
                울산
                부산
                11
                28
                13
                14
                15
                16
                17
                18
                19
                20
                21
                22
                23
                24
                25
                26
                12
                '''
    regionList = list(filter(lambda x: len(x) != 0,map(lambda x: x.strip(),regionStr.split('\n'))))
    region_choices = list(map(lambda x:(x,x),regionList))
    return region_choices
