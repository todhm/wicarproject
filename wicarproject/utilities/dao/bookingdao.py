from application import db
from carupload.models import CarImage,Car
from carbooking.models import *
from caruser.models import UserBank,User
from datetime import datetime as dt
from datetime import timedelta
from utilities.timeutil import *
from utilities.common import get_price,convert_wtf_error,convert_events_time
from utilities.errorutil import return_booking_error
from utilities.flask_tracking.documents import Tracking
from utilities.smsutil import send_sms, send_lms
from flask import jsonify,request
from sqlalchemy import func
import json


class BookingDao(object):

    @classmethod
    def get_booking_obj_by_user(self,user_id):
        booking  = CarBooking.query.filter(CarBooking.renter_id==user_id).order_by(CarBooking.register_date.desc()).first()
        return booking

    @classmethod
    def get_booking_obj_by_car(self,car_id):
        booking  = CarBooking.query.filter(CarBooking.car_id==car_id).order_by(CarBooking.register_date.desc()).first()
        return booking

    @classmethod
    def add_vacation_time(self,user_id,start_time_str,end_time_str):
        start_time = dt.strptime(start_time_str,VacationData.get_time_format())
        end_time = dt.strptime(end_time_str,VacationData.get_time_format())
        vacation = VacationData(user_id,start_time,end_time)
        db.session.add(vacation)
        db.session.commit()

    @classmethod
    def add_booking(self,car_id,renter_id,total_price,insurance_price,owner_earning,start_time,end_time,status,total_distance,register_date =None):
        booking = CarBooking(
            car_id=car_id,
            renter_id=renter_id,
            total_price=total_price,
            insurance_price=insurance_price,
            owner_earning=owner_earning,
            start_time=start_time,
            end_time=end_time,
            status=status,
            register_date=register_date,
            total_distance=total_distance
            )
        db.session.add(booking)
        db.session.commit()
        return booking

    @classmethod
    def add_availability(self,user_id,availability_list):
        user_time_list = UserTime.query.filter(UserTime.user_id==user_id).order_by(UserTime.dow).all()
        if user_time_list:
            for idx,available in  enumerate(availability_list):
                user_time_list[idx].availability= available['dailyAlways']
                user_time_list[idx].start_time = available['start']
                user_time_list[idx].end_time = available['end']

        else:
            for idx,available in  enumerate(availability_list):
                utt = UserTime(
                    user_id = user_id,
                    dow=idx,
                    availability=available['dailyAlways'],
                    start_time = available['start'],
                    end_time = available['end'],
                )
                db.session.add(utt)
        db.session.commit()

    @classmethod
    def check_booking_availability(self,car,start_time,end_time):
        result={}
        if not car.caroption:
            result['message']="fail"
            result['errorMessage']="옵션이 등록되어있지 않습니다."
            return result
        advance_time = car.caroption.advance_notice
        if not car.active:
            result['message']="fail"
            result['errorMessage']= "등록이 되지않는 자동차입니다."
            return result

        required_time = dt.now() + timedelta(hours=advance_time)
        if required_time > start_time:
            result['message'] = "fail"
            result['errorMessage'] = dt.strftime(required_time,"%Y-%m-%d %H:%M")
            result['errorMessage'] += '이전에는 예약이 불가능합니다.'
            return result

        vacationList = VacationData\
                            .query\
                            .filter(VacationData.user_id==car.user_id)\
                            .filter(VacationData.end_time >= dt.now())\
                            .all()

        if vacationList:
            for vacation in vacationList:
                if find_duplicate_time(vacation.start_time, vacation.end_time, start_time, end_time):
                    vc_start_str = dt.strftime(vacation.start_time,"%Y-%m-%d %H:%M")
                    vc_end_str = dt.strftime(vacation.end_time,"%Y-%m-%d %H:%M")
                    result['message'] = 'fail'
                    result['errorMessage'] = vc_start_str + "~" + vc_end_str
                    result['errorMessage'] += '에는 예약이 불가능합니다.'
                    return result

        carVacationList = CarVacation\
                            .query\
                            .filter(CarVacation.car_id==car.id)\
                            .filter(CarVacation.end_time >= start_time)\
                            .all()
        for car_vacation in carVacationList:
            if find_duplicate_time(car_vacation.start_time, car_vacation.end_time, start_time, end_time):
                vc_start_str = dt.strftime(car_vacation.start_time,"%Y-%m-%d %H:%M")
                vc_end_str = dt.strftime(car_vacation.end_time,"%Y-%m-%d %H:%M")
                result['message'] = 'fail'
                result['errorMessage'] = vc_start_str + "~" + vc_end_str
                result['errorMessage'] += '에는 예약이 불가능합니다.'
                return result



        userTimeList = UserTime.query\
                                .filter(UserTime.user_id==car.user_id)\
                                .order_by(UserTime.dow)\
                                .all()
        if userTimeList:
            start_time_dow = start_time.weekday()
            end_time_dow = end_time.weekday()
            start_time_minute = start_time.hour * 60 + start_time.minute
            end_time_minute = end_time.hour * 60 + end_time.minute
            start_time_availability = userTimeList[start_time_dow].availability
            end_time_availability = userTimeList[end_time_dow].availability

            #요청한 렌트시작일에 차주가 렌트가능 시간을 열어놓았는지 확인.
            if (start_time_availability==0):
                result['message'] = "fail"
                result['errorMessage'] = "매주" + " "+ dow_convert(start_time_dow)
                result['errorMessage'] += "에는 차주를 만날 수 없습니다."
                return result



            if ((start_time_availability==1)
                and ((start_time_minute < userTimeList[start_time_dow].start_time)
                or (start_time_minute > userTimeList[start_time_dow].end_time))):
                result['message'] = "fail"
                result['errorMessage'] = "매주" + " "+ dow_convert(start_time_dow) + "에는"
                start_hour,start_minute = divmod(userTimeList[start_time_dow].start_time,60)
                start_str = "%d:%02d" % (start_hour,start_minute)
                end_hour, end_minute = divmod(userTimeList[start_time_dow].end_time,60)
                end_str = "%d:%02d" % (end_hour,end_minute)
                errorMessage = start_str +"~" + end_str+ "에 차주를 만날 수 있습니다."
                result['errorMessage'] += errorMessage
                return result

            #요청한 렌트종료일에 차주가 렌트가능 시간을 닫아놨는지 확인
            if end_time_availability==0:
                result['message'] = "fail"
                result['errorMessage'] = "매주" + " "+ dow_convert(end_time_dow)
                result['errorMessage'] += "에는 차주를 만날 수 없습니다."
                return result

            if ((end_time_availability==1)
                    and ((end_time_minute < userTimeList[end_time_dow].start_time)\
                    or (end_time_minute > userTimeList[end_time_dow].end_time))):
                result['message'] = "fail"
                result['errorMessage'] = "매주" + " "+ dow_convert(end_time_dow) + "에는"
                start_hour,start_minute = divmod(userTimeList[end_time_dow].start_time,60)
                start_str = "%d:%02d" % (start_hour,start_minute)
                end_hour, end_minute = divmod(userTimeList[end_time_dow].end_time,60)
                end_str = "%d:%02d" % (end_hour,end_minute)
                errorMessage = start_str +"~" + end_str+ "에 차주를 만날 수 있습니다."
                result['errorMessage'] += errorMessage
                return result


        bookingTimeList = CarBooking.query\
                                .filter(CarBooking.car_id==car.id)\
                                .filter(CarBooking.status>=0)\
                                .filter(CarBooking.end_time >= dt.now())\
                                .all()
        if bookingTimeList:
            for booking in bookingTimeList:
                if find_duplicate_time(booking.start_time, booking.end_time, start_time, end_time):
                    booking_startstr = dt.strftime(booking.start_time,"%Y-%m-%d %H:%M")
                    booking_endstr = dt.strftime(booking.end_time,"%Y-%m-%d %H:%M")
                    result['message'] = 'fail'
                    result['errorMessage'] = booking_startstr + "~" + booking_endstr
                    result['errorMessage'] += '에는 예약이 불가능합니다.'
                    return result

        result['message']='success'
        return result

    @classmethod
    def add_car_price_schedule(self,car_id,price,start_time,end_time):
        carPriceSchedule = CarPriceSchedule(
            car_id=car_id,
            price=price,
            start_time=start_time,
            end_time=end_time
        )
        db.session.add(carPriceSchedule)
        db.session.commit()

    @classmethod
    def add_car_vacation(self,car_id,start_time,end_time):
        carVacation = CarVacation(
            car_id=car_id,
            start_time=start_time,
            end_time=end_time
        )
        db.session.add(carVacation)
        db.session.commit()

    @classmethod
    def iterate_notification_info(self,bookingList,is_car_owner):
        for booking in bookingList:
            carimage = booking.car.carimage.order_by(CarImage.image).filter(CarImage.active==True).first()
            booking.imgsrc = carimage.imgsrc if carimage else None
            time_difference = min(booking.register_date + timedelta(hours=12),booking.start_time) - dt.now()
            remaining_hours = (time_difference.days *24) + (time_difference.seconds / 3600)
            booking.remaining_time = round(remaining_hours)
            booking.is_car_owner = is_car_owner
        return bookingList

    @classmethod
    def get_owner_review(self,user_id):
        owner_review_list = OwnerReview.query.filter(OwnerReview.owner_id==user_id).all()
        point = 0
        for owner_review in owner_review_list:
            point += owner_review.review_point
        rate = point / max(len(owner_review_list),1)
        return owner_review_list, rate


    @classmethod
    def get_renter_review(self,user_id):
        renter_review_list = RenterReview.query.filter(RenterReview.renter_id==user_id).all()
        point = 0
        for renter_review in renter_review_list:
            point += renter_review.review_point
        rate = point / max(len(renter_review_list),1)
        return renter_review_list, rate



    @classmethod
    def get_renter_review_json(self,user_id):
        review_json = []
        renter_review_list = RenterReview.query.filter(RenterReview.renter_id==user_id).all()
        point = 0
        for renter_review in renter_review_list:
            review = {}
            review['message'] = renter_review.review
            review['point'] = renter_review.review_point
            review['reviewer_user_id'] = renter_review.booking.car.user.id
            review['register_year'] = renter_review.register_date.year
            review['register_month'] = renter_review.register_date.month
            review['register_day'] = renter_review.register_date.day
            review['reviewer_name'] = renter_review.booking.car.user.name
            review['reviewer_id'] = renter_review.booking.car.user.id

            review['reviewer_img'] = renter_review.booking.car.user.imgsrc
            review_json.append(review)
            point += renter_review.review_point
        rate = point / max(len(renter_review_list),1)
        return review_json, rate

    @classmethod
    def get_owner_review_json(self,user_id):
        review_json = []
        owner_review_list = OwnerReview.query.filter(OwnerReview.owner_id==user_id).all()
        point = 0
        for owner_review in owner_review_list:
            review = {}
            review['message'] = owner_review.review
            review['point'] = owner_review.review_point
            review['reviewer_user_id'] = owner_review.booking.renter.id
            review['register_year'] = owner_review.register_date.year
            review['register_month'] = owner_review.register_date.month
            review['register_day'] = owner_review.register_date.day
            review['reviewer_name'] = owner_review.booking.renter.name
            review['reviewer_id'] = owner_review.booking.renter.id
            review['reviewer_img'] = owner_review.booking.renter.imgsrc
            review_json.append(review)
            point += owner_review.review_point
        rate = point / max(len(owner_review_list),1)
        return review_json, rate

    @classmethod
    def convert_schedule(self,obj,car_id):
        scheduleList = obj\
            .query\
            .filter(obj.end_time>=dt.now())\
            .filter(obj.car_id==car_id).all()
        result = {}
        if scheduleList:
            priceEvents = [ schedule.to_json for schedule in scheduleList]
            result['priceEvents'] = priceEvents
            result['message'] = 'success'
        else:
            result['message'] = "fail"
        return jsonify(result)

    @classmethod
    def update_carprice_schedule(self,car_id,data,form_class,vacation_class):
        data['car_id'] = car_id
        form = form_class(data = data)
        result={}
        vacation_list= vacation_class\
                        .query\
                        .filter(vacation_class.car_id == car_id)\
                        .filter(vacation_class.end_time > dt.now())\
                        .filter(vacation_class.id !=data.get('id'))\
                        .all()
        if form.validate(vacation_list):
            start_time,end_time = convert_events_time(data)
            vacationSchedule = vacation_class.query.filter(vacation_class.id==form.id.data).first()
            if vacationSchedule:
                vacationSchedule.start_time = start_time
                vacationSchedule.end_time = end_time
                if type(vacationSchedule) is CarPriceSchedule:
                    vacationSchedule.price = form.price.data
                db.session.commit()
                result['id'] = vacationSchedule.id
                result['message'] = "success"
            else:
                result['message']="fail"
                result['errorMessage'] = "해당 스케쥴이 존재하지 않습니다"
        else:
            result = convert_wtf_error(result,form)
        return jsonify(result)


    @classmethod
    def get_booking_for_pay(self,start_time,end_time):
        carBookingList = db.session.query(CarBooking,User,UserBank)\
            .outerjoin(Car,CarBooking.car_id==Car.id)\
            .outerjoin(User,Car.user_id==User.id)\
            .outerjoin(UserBank,Car.user_id==UserBank.user_id)\
            .filter(CarBooking.end_time >=start_time)\
            .filter(CarBooking.end_time<=end_time)\
            .filter(CarBooking.status==3)\
            .order_by(Car.user_id)\
            .order_by(CarBooking.end_time)\
            .all()
        result = {}
        for (carBooking,owner,bank) in carBookingList:
            if not result.get(owner.id):
                result[owner.id] = {}
                result[owner.id]['booking_list'] = []
                result[owner.id]['total_earning'] = 0
                result[owner.id]['account_num'] = bank.account_num if bank else ""
                result[owner.id]['account_holder_name'] = bank.account_holder_name if bank else ""
                result[owner.id]['bank_name'] = bank.bank_name if bank else ""
                result[owner.id]['owner_name'] = owner.name
                result[owner.id]['owner_phone'] = owner.phone



            booking_info={}
            booking_info['id'] = carBooking.id
            booking_info['start_time'] = dt.strftime(carBooking.start_time,"%Y-%m-%d %H:%M")
            booking_info['end_time'] = dt.strftime(carBooking.end_time,"%Y-%m-%d %H:%M")
            booking_info['owner_earning'] = carBooking.owner_earning
            booking_info['renter_name'] = carBooking.renter.name
            result[owner.id]['booking_list'].append(booking_info)
            result[owner.id]['total_earning'] += carBooking.owner_earning
        return result


    @classmethod
    def send_owner_list_money(self,checkedList):
        total_true = True
        unsent_booking = []
        bank_tran_date = dt.strftime(dt.now(),"%Y-%m-%d")
        for checkedOwner in checkedList:
            owner_id = checkedOwner['ownerId']
            total_amount = checkedOwner['total_earning']
            account_holder_name =checkedOwner['account_holder_name'] if checkedOwner.get('account_holder_name')  else""
            bank_name=checkedOwner['bank_name'] if checkedOwner.get('bank_name')  else ""
            account_num=checkedOwner['account_num'] if checkedOwner.get('account_num')  else ""
            for booking in checkedOwner['booking_list']:
                try:
                    result = self.send_owner_money(
                        booking_id=booking['id'],
                        account_num = account_num,
                        user_id =owner_id,
                        account_holder_name =account_holder_name,
                        tran_amt = booking['owner_earning'],
                        bank_tran_date = bank_tran_date,
                        bank_name=bank_name
                    )

                except:
                    total_true = False
                    unsent_booking.append(booking['id'])
            _tracking_data = {
                'user_id':owner_id,
                'total_amount':total_amount,
                'account_holder_name':account_holder_name,
                'action':'send_owner_money',
            }
            t = Tracking(date_created=dt.now(),custom_data = _tracking_data)
            t.save()
            send_sms(checkedOwner['owner_phone'],'고객님에게 {}원의 Wi-CAR수익이 전달되었습니다'.format(total_amount))

        return total_true,unsent_booking




    @classmethod
    def send_owner_money(self,booking_id,user_id,account_num,account_holder_name,tran_amt,bank_tran_date,bank_name):
        account_num_masked=  account_num[:3] + "*******"
        ownerSend = OwnerSend(
            booking_id = booking_id,
            user_id=user_id,
            tran_amt = tran_amt,
            rsp_code = "A0000",
            bank_tran_id = "직접송금",
            bank_name = bank_name,
            account_holder_name = account_holder_name,
            account_num = account_num,
            account_num_masked = account_num_masked,
            bank_tran_date =bank_tran_date ,
            print_content = "예약지급완료",
            wd_bank_name ="KB국민은행" ,
            wd_account_holder_name = "주식회사 쉐어몬스터즈",
            bank_rsp_code = "직접송금",
            bank_rsp_message = "직접송금"
        )
        booking = CarBooking.query.filter(CarBooking.id==booking_id).first()
        booking.status = 4
        db.session.add(ownerSend)
        db.session.commit()
        return True

    @classmethod
    def update_bookingimage_filename(self):
        bookingImageList = BookingImage.query.all()
        for bookingImage in bookingImageList:
            bookingImage.filename = bookingImage.originalImgSrc
            db.session.add(bookingImage)
        db.session.commit()
        return True
