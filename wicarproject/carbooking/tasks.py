from datetime import datetime as dt
from datetime import timedelta
from application import celery,db
from carbooking.models import CarBooking, OwnerSend
from caruser.models import UserBank
from utilities.smsutil import send_sms, send_lms
from utilities.dao.userdao import UserDao
from utilities.flask_tracking.documents import Tracking
from utilities.common import get_bank_token
from flask import request, current_app
import json
import requests


def cancel_overtime():
    bookingList = CarBooking.query.filter(CarBooking.status==0).all()
    renter_phone_lst = []
    owner_phone_lst = []
    for booking in bookingList:
        time_difference = min(booking.register_date + timedelta(hours=12),booking.start_time) - dt.now()
        if time_difference <= timedelta(hours=0):
            booking.status = -2
            renter_phone = UserDao.get_user_phone_byid(booking.renter_id)
            owner_phone = UserDao.get_user_phone_byid(booking.car.user.id)
            renter_phone_lst.append(renter_phone)
            owner_phone_lst.append(owner_phone)
            _tracking_data = {
                'user_id':'wicar',
                'booking_id':booking.id,
                'owner_id':booking.car.user.id,
                'owner_name':booking.car.user.name,
                'renter_id':booking.renter_id,
                'renter_name':booking.renter.name,
                'cancel_price':booking.total_price,
                 'action':'auto_cancel_booking'
                 }
            t = Tracking(date_created=dt.now(),custom_data = _tracking_data)
            try:
                t.save(cascade=False, write_concern={'w': -1, 'fsync': False})
            except Exception as e:  # InvalidStringData is raised when a BSON object can't be encoded
                pass
    db.session.commit()
    if not current_app.config['TESTING']:
        for owner_phone in owner_phone_lst:
            send_sms(
                owner_phone,
                '고객님께서 예약을 수락하지 않아 예약이 취소되었습니다.'
                )
        for renter_phone in renter_phone_lst:
            send_sms(
                renter_phone,
                '차주께서 예약을 수락하지 않아 예약이 취소되었습니다.'
                )

@celery.task(bind=True)
def cancel_overtime_booking(self):
    cancel_overtime()

def change_past():
    bookingList = CarBooking.query.filter(CarBooking.status==2).all()
    phone_lst = []
    response = get_bank_token()
    now_time = dt.now()
    if response.status_code == 200:
        responseObj = response.json()
        auth_token = responseObj['access_token']
        time_format =  dt.strftime(now_time,'%Y%m%d%H%M%S')
        headers = {
            'Content-Type':"application/json",
            'Accept': 'application/json'
        }
        headers.update({"Authorization":"Bearer " + auth_token})
        for booking in bookingList:
            is_finished_rent = now_time >=  booking.end_time
            if is_finished_rent:
                owner_id = booking.car.user.id
                owner_bank = UserBank.query.filter(UserBank.user_id == owner_id).first()
                renter_phone = UserDao.get_user_phone_byid(booking.renter_id)
                owner_phone = UserDao.get_user_phone_byid(owner_id)
                if not owner_bank:
                    send_lms(
                        owner_phone,
                        'Wi-CAR 계좌요청',
                        '고객님의 wicar계좌가 등록되어있지 않아서 예약금액을 지급할 수 없습니다. www.wicar.co.kr/account_info 에서 계좌를 등록해주세요.',
                        )

                else:
                    request_body = {}
                    request_body['wd_pass_phrase'] = "NONE"
                    request_body['wd_print_content'] = "와이카차주금액지급"
                    request_body['req_cnt'] = "1"
                    request_body['req_list'] = []
                    request_body['req_list'].append({})
                    request_body['req_list'][0]['tran_no'] = "1"
                    request_body['req_list'][0]['bank_code_std'] = owner_bank.bank_code_std
                    request_body['req_list'][0]['account_num'] = owner_bank.account_num
                    request_body['req_list'][0]['account_holder_name'] = owner_bank.account_holder_name
                    request_body['req_list'][0]['print_content'] = "와이카차주금액지급"
                    request_body['req_list'][0]['tran_amt'] = booking.owner_earning
                    request_body['tran_dtime'] = time_format
                    url = ' https://testapi.open-platform.or.kr/v1.0/transfer/deposit2'
                    response = requests.post(url,data=json.dumps(request_body) ,headers=headers)
                    if response.status_code == 200:
                        responseObj = response.json()
                        ownerSend = OwnerSend(
                            booking_id = booking.id,
                            user_id=owner_id,
                            tran_amt = responseObj['res_list'][0]['tran_amt'],
                            rsp_code = responseObj['rsp_code'],
                            bank_tran_id = responseObj['res_list'][0]['bank_tran_id'],
                            bank_name = responseObj['res_list'][0].get('bank_name'),
                            account_holder_name = responseObj['res_list'][0].get('account_holder_name'),
                            account_num = responseObj['res_list'][0].get('account_num'),
                            account_num_masked = responseObj['res_list'][0].get('account_num_masked'),
                            bank_tran_date = responseObj['res_list'][0].get('bank_tran_date'),
                            print_content = responseObj['res_list'][0].get('print_content'),
                            wd_bank_name = responseObj.get('wd_bank_name'),
                            wd_account_holder_name = responseObj.get('wd_account_holder_name'),
                            bank_rsp_code = responseObj['res_list'][0]['bank_rsp_code'],
                            bank_rsp_message = responseObj['res_list'][0]['bank_rsp_message']
                        )
                        db.session.add(ownerSend)
                        db.session.commit()
                        if responseObj['rsp_code'] == "A0000":
                            booking.status = 3
                            phone_obj = {}
                            phone_obj['renter_phone'] = renter_phone
                            phone_obj['owner_phone'] = owner_phone
                            phone_obj['booking_id'] = booking.id
                            phone_lst.append(phone_obj)
                            _tracking_data = {
                                'user_id':'wicar',
                                'booking_id':booking.id,
                                'owner_id': owner_id,
                                'owner_name':booking.car.user.name,
                                'renter_id':booking.renter_id,
                                'renter_name':booking.renter.name,
                                'total_price':booking.total_price,
                                'owner_earning':booking.owner_earning,
                                 'action':'finish_booking'
                                 }
                            t = Tracking(date_created=dt.now(),custom_data = _tracking_data)
                            try:
                                t.save(cascade=False, write_concern={'w': -1, 'fsync': False})
                            except Exception as e:  # InvalidStringData is raised when a BSON object can't be encoded
                                pass
                    db.session.commit()
        if not current_app.config['TESTING']:
            for phone_obj in phone_lst:
                send_lms(
                    phone_obj['owner_phone'],
                    'Wi-CAR 예약 완료',
                    '고객님의예약이 완료되었고 예약 금액을 지급하였습니다. www.wicar.co.kr/reservation/{}에서 사용자에 대한 평가를 남겨주세요.'.format(booking.id)
                    )
                send_lms(
                    phone_obj['renter_phone'],
                    'Wi-CAR 예약 완료',
                    '고객님의예약이 완료되었습니다. www.wicar.co.kr/reservation/{}에서 차주에 대한 평가를 남겨주세요.'.format(booking.id)
                    )

def finish_past_booking():
    bookingList = CarBooking.query.filter(CarBooking.status==2).all()
    phone_lst = []
    now_time = dt.now()
    for booking in bookingList:
        is_finished_rent = now_time >=  booking.end_time
        if is_finished_rent:
            phone_obj={}
            owner_id = booking.car.user.id
            owner_bank = UserBank.query.filter(UserBank.user_id == owner_id).first()
            renter_phone = UserDao.get_user_phone_byid(booking.renter_id)
            owner_phone = UserDao.get_user_phone_byid(owner_id)
            booking.status = 3
            db.session.commit()
            phone_obj['renter_phone'] = renter_phone
            phone_obj['owner_phone'] = owner_phone
            phone_obj['booking_id'] = booking.id
            phone_lst.append(phone_obj)
            _tracking_data = {
                'user_id':'wicar',
                'booking_id':booking.id,
                'owner_id': owner_id,
                'owner_name':booking.car.user.name,
                'renter_id':booking.renter_id,
                'renter_name':booking.renter.name,
                'total_price':booking.total_price,
                'owner_earning':booking.owner_earning,
                 'action':'finish_booking'
                 }
            t = Tracking(date_created=dt.now(),custom_data = _tracking_data)
            try:
                t.save(cascade=False, write_concern={'w': -1, 'fsync': False})
            except Exception as e:  # InvalidStringData is raised when a BSON object can't be encoded
                pass
    if not current_app.config['TESTING']:
        for phone_obj in phone_lst:
            send_lms(
                phone_obj['owner_phone'],
                'Wi-CAR 예약 완료',
                '서비스 시간이 지나 고객님의 서비스가 자동 완료되었습니다. www.wicar.co.kr/reservation/{}에서 사용자에 대한 평가를 남겨주세요.'.format(booking.id)
                )
            send_lms(
                phone_obj['renter_phone'],
                'Wi-CAR 예약 완료',
                '서비스 시간이 지나 고객님의예약이 자동 완료되었습니다. www.wicar.co.kr/reservation/{}에서 차주에 대한 평가를 남겨주세요.'.format(booking.id)
                )

#Modify: CarBooking .
#Effect: Change all booking status to 3 and send message to Customers.send Money to Car Owner.
@celery.task(bind=True)
def change_past_booking(self):
    change_past()



#Modify: CarBooking .
#Effect: Change all booking status to 3 and send message to Customers.
@celery.task(bind=True)
def finish_past_booking_celery(self):
    finish_past_booking()
