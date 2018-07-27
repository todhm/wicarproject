from flask import Blueprint, render_template, session, make_response, request, flash, jsonify, redirect, url_for, send_from_directory, abort,current_app
from wicaradmin.forms import *
from caruser.models import User
from carbooking.models import CarBooking
from utilities.dao.bookingdao import BookingDao
from utilities.decorators import admin_login_required
from utilities.errorutil import convert_error_by_field
from datetime import datetime as dt
from datetime import timedelta
import json
import uuid

wicar_admin_app = Blueprint('wicar_admin_app',__name__)

@wicar_admin_app.route('/auth_login',methods=["POST"])
def login_page():
    data = request.get_json()
    form = AdminLoginForm(data=data,csrf_enabled=False)
    error = None
    result={}
    if form.validate():
        user = User.query.filter_by(email = form.email.data).first()
        auth_token = user.encode_auth_token(user.id)
        if auth_token:
            result['message']="success"
            result['auth_token'] = auth_token.decode()
        else:
            result['message'] = "fail"
            result['errorMessage'] = {}
            result['errorMessage']['emailError'] ="인증에 실패하였습니다. 잠시후 다시시도해주세요"

    else:
        result = convert_error_by_field(result,form)
    return jsonify(result)


@wicar_admin_app.route('/get_unpaid_data',methods=["POST"])
@admin_login_required
def account_page():
    data = request.get_json()
    form = BaseDateForm(data=data)
    result={}
    if form.validate():
        start_time =form.startDate.data
        end_time = form.endDate.data
        payment_result = BookingDao.get_booking_for_pay(start_time,end_time)
        result['message']="success"
        result['data'] =payment_result
    else:
        result = convert_error_by_field(result,form)
    return jsonify(result)

@wicar_admin_app.route('/pay_complete',methods=["POST"])
@admin_login_required
def pay_complete(booking_id=""):
    data = request.get_json()
    result={}
    success,unsent_list = BookingDao.send_owner_list_money(data['checkedList'])
    if success:
        result['message']="success"
    else:
        result['message']="fail"
        result['errorMessage']="송금에 실패하였습니다"
        result['unsentList'] = unsent_list

    return jsonify(result)
