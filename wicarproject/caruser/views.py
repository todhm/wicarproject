import random
import bcrypt
import string
import json
import requests
from flask import Blueprint, render_template,session,make_response,request,flash,jsonify,redirect,url_for,current_app,abort
import httplib2
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
from caruser.forms import *
from caruser.models import User, UserBank
from caruser.mongomodels import BestCar
from carupload.models import Car,CarImage
from carbooking.models import UserCard,CarBooking,OwnerReview, RenterReview,CarBooking, OwnerSend
from carbooking.forms import  NiceCardForm,CreditCardForm
from application import db
from utilities.decorators import logout_required,login_required, nophone_required,phonenumber_required, owner_send_matched
from utilities.smsutil import send_sms, send_confirmation_code
from utilities.timeutil import get_current_day, get_time_comb,get_end_day
from utilities.dao.userdao import UserDao
from utilities.dao.bookingdao import BookingDao
from utilities.hashutil import encrypt_hash
from utilities.imaging import save_user_profile
from utilities.common import verify_bank_data, get_bank_token, get_count,register_card,delete_card
from sqlalchemy import and_
from datetime import datetime as dt
import requests
import uuid
from facebook import get_user_from_cookie,GraphAPI
from sqlalchemy import or_

carshare_app = Blueprint('carshare_app',__name__,template_folder='templates')
carshare_app.config = {}

@carshare_app.record
def record_params(setup_state):
    app = setup_state.app
    carshare_app.config = dict([(key,value) for (key,value) in app.config.items()])
    # carshare_app.config['CLIENT_FB_JSON'] = json.loads(
    #      open(carshare_app.config['CLIENT_FB_SECRET_FILE'], 'r').read())

@carshare_app.route('/gconnect',methods=['POST'])
@logout_required
def gconnect():
    #Obtain auth code.
    code = request.data

    try:
        #Upgrade the authorization code into a credential object
        oauth_flow = flow_from_clientsecrets("client_secret.json",scope="")
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)

    except FlowExchangeError:
        response = make_response(
            json.dumps('Failed to upgrade the authorization code.',401))
        response.headers['Content-Type'] = 'application/json'
        return response

    #Check that the access token is valid
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v2/tokeninfo?access_token=%s'
           % access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url,'GET')[1])
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')),500)
        response.headers['Content-Type'] = 'application/json'
        return response

    #Verify that the access token is valid for this app.
    CLIENT_ID = carshare_app.config['CLIENT_JSON']['web']['client_id']
    if result['issued_to'] != CLIENT_ID:
        response = make_response(json.dumps("Token's cleint id does not match apps"),400)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is used for the intended user.
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(
            json.dumps("Token's user ID doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()
    email = data.get('email')
    username = data.get('name')
    profile = data.get('picture')

    #Case where user does not exists
    data = UserDao.login_user(email=email,username=username,profile=profile, data=data)
    return jsonify(data)



@carshare_app.route('/gdisconnect')
@login_required
def gdisconnect():
    access_token = session.get('access_token')
    if access_token is None:
        response = make_response(json.dumps('Current user not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    del session['access_token']
    del session['gplus_id']
    del session['email']
    del session['picture']
    return redirect(url_for('carshare_app.login_page'))


@carshare_app.route('/fbconnect', methods=['POST'])
def fbconnect():
    access_token = request.data
    data = {}
    app_id = carshare_app.config['CLIENT_FB_JSON']['web']['app_id']
    app_secret = carshare_app.config['CLIENT_FB_JSON']['web']['app_secret']
    result = get_user_from_cookie(
        cookies = request.cookies,
        app_id = app_id,
        app_secret = app_secret
        )

    if result:
        graph = GraphAPI(result['access_token'])
        args = {'fields' : 'id,name,email', }
        profile = graph.get_object('me',**args)
        email = profile.get('email')
        username = profile.get('name')
        data = UserDao.login_user(email=email,username=username,profile=None, data=data)
    return jsonify(data)

@carshare_app.route('/kakao_oauth',methods=["POST"])
def kakao_oauth():
    request_obj = json.loads(request.data.decode('utf-8'))
    headers = {
        'Content-Type':"application/x-www-form-urlencoded",
        'Cache-Control' : "no-cache"
    }
    headers.update({"Authorization":"Bearer " + request_obj.get("access_token")})
    request_obj.pop("refresh_token_expires_in")
    request_obj.pop("expires_in")
    url = 'https://kapi.kakao.com/v1/user/me'
    response = requests.request("POST",url,headers=headers)
    result = {}
    if response.status_code == 200:
        kdata = response.json()
        email = kdata.get('kaccount_email')
        if kdata.get('properties'):
            username = kdata['properties'].get('nickname')
            profile = kdata['properties'].get('profile_image')
        else:
            result['message'] = "fail"
            return jsonify(result)
        profile = profile if profile and profile !='null' else None
        result = UserDao.login_user(email=email,username=username,profile=profile, data=result)
        session['ktoken'] = request_obj['access_token']
        return jsonify(result)

    else:
        result['message'] = "fail"
        return jsonify(result)

@carshare_app.route('/login',methods=['GET','POST'])
@logout_required
def login_page():
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in range(32))
    session['state'] = state
    form = LoginForm()
    error = None
    if request.method == 'GET' and request.args.get('next'):
        session['next'] = request.args.get('next', None)

    if form.validate_on_submit():
        session['email'] = form.email.data
        user = User.query.filter_by(email = form.email.data).first()
        session['user_id'] = user.id
        if 'next' in session:
            next = session.get('next')
            session.pop('next')
            return redirect(next)
        else:
            return redirect(url_for('carshare_app.homepage'))
    return render_template('carshare/login.html', form=form, error=error,STATE=state)


@carshare_app.route('/logout')
@login_required
def logout():
    session.pop('email')
    if session.get('user_id'):
        session.pop('user_id')
    if session.get('ktoken'):
        headers = {
            'Content-Type':"application/x-www-form-urlencoded",
            'Cache-Control' : "no-cache"
        }
        headers.update({"Authorization":"Bearer " + session.get("ktoken")})
        url = 'https://kapi.kakao.com/v1/user/logout'
        response = requests.request("POST",url,headers=headers)

    return redirect(url_for('carshare_app.homepage'))

@carshare_app.record
def record_params(setup_state):
  app = setup_state.app
  carshare_app.config = dict([(key,value) for (key,value) in app.config.items()])

@carshare_app.route('/',methods=["GET","POST"])
def homepage():
    form = SearchForm()
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in range(32))
    session['state'] = state
    start_date = ""
    end_date=""
    today = get_current_day()
    current_hour = str(today.hour)
    is_car = BestCar.objects.order_by('-register_date')
    temp_car = [{'id':False,"brand":'소나타', 'class_name':"하이브리드",'is_sale':True,'save_percent':40,'reviewCount':100,'review_point':5,'price':100000,'img':'/static/images/img1.jpg','year':2017},
          {'id':False,"brand":'소나타', 'class_name':"하이브리드",'is_sale':True,'save_percent':40,'reviewCount':100,'review_point':5,'price':100000,'img':'/static/images/img1.jpg','year':2017},
          {'id':False,"brand":'에쿠스', 'class_name':'VS 380','reviewCount':50,'review_point':5,'price':130000,'img':'/static/images/img2.jpg','year':2016},
          {'id':False,"brand":'싼타페', 'class_name':'2016년형','is_sale':True,'save_percent':70,'reviewCount':70,'review_point':5,'price':100000,'img':'/static/images/img4.jpg','year':2016},
          {'id':False,"brand":'싼타페', 'class_name':'2016년형','is_sale':True,'save_percent':70,'reviewCount':70,'review_point':5,'price':100000,'img':'/static/images/img4.jpg','year':2016}]
    if is_car:
        cars = is_car[0]['car_list']
        if len(cars) < 3:
            cars = temp_car
    else:
        cars= temp_car

    if form.validate_on_submit():
        session['search_data'] = request.form
        return redirect(url_for('carbooking_app.car_search'))
    else:
        if session.get('search_data'):
            session.pop('search_data')


    return render_template("/carshare/index_temp.html",
            recommend_cars=cars,
            STATE=state,
            current_hour=current_hour,
            form=form,
            start_date=start_date,
            end_date=end_date
            )


@carshare_app.route('/explain_wicar')
def explanation_page():
    return render_template("/carshare/wicar_explain.html")


@carshare_app.route('/car_share')
def sharing_page():
    return render_template("/carshare/car_share.html")


@carshare_app.route('/car_rent')
def renting_page():
    return render_template("/carshare/car_rent.html")


@carshare_app.route('/insurance')
def insurance_page():
    return render_template("/carshare/insurance.html")


@carshare_app.route('/signup',methods=['GET','POST'])
@logout_required
def signup_page():
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in range(32))
    session['state'] = state
    form = SignUpForm()
    if form.validate_on_submit():
        user = User(
            form.username.data,
            form.email.data,
            form.password.data
        )
        db.session.add(user)
        db.session.commit()
        session['email'] = form.email.data
        session['user_id']  = user.id
        return redirect(url_for('carshare_app.send_code_page'))

    return render_template("/carshare/signup.html",form=form,STATE=state)


@carshare_app.route('/sendcode',methods=['GET','POST'])
@login_required
@nophone_required
def send_code_page():
    form = PhoneForm()
    error = None
    if request.method == 'GET' and request.args.get('next'):
        session['next'] = request.args.get('next', None)
    if form.validate_on_submit():
        code = send_confirmation_code(form.phonenumber.data)
        if not code:
            error = "현재 인증서비스의 에러가 발생했습니다. 잠시 후 다시 이용해 주세요."
            flash(error)
            return render_template('/carshare/sendcode.html',form=form,error=error)

        return redirect(url_for('carshare_app.verify_code_page'))

    return render_template('/carshare/sendcode.html',form=form,error=error)

@carshare_app.route('/verifycode',methods=['GET','POST'])
@login_required
@phonenumber_required
def verify_code_page():
    codeForm = CodeForm()
    error = None
    if request.method =="POST":
        #재전송 버튼을 눌렀을때
        if request.form.get('submit') == "resend":
            phonenumber = session.get('phonenumber')
            code = send_confirmation_code(phonenumber)
            if not code:
                error = "현재 인증서비스의 에러가 발생했습니다. 잠시 후 다시 이용해 주세요."
                flash(error)
            return render_template('/carshare/verifycode.html',form=codeForm,error=error)


        #인증번호를 입력하였을 때
        elif codeForm.validate_on_submit():
            if session.get('verification_code') == codeForm.code.data:
                user = User\
                    .query\
                    .filter_by(email=session.get("email"))\
                    .update(dict(phone= session.get("phonenumber")))
                session.pop("phonenumber")
                session.pop("verification_code")
                db.session.commit()
                if 'next' in session:
                    next = session.get('next')
                    session.pop('next')
                    return redirect(next)
                return redirect(url_for('carshare_app.homepage',next=request.url))
            else:
                error ="인증번호가 일치하지 않습니다!"
                flash(error)

        return render_template('/carshare/verifycode.html',form=codeForm,error=error)

    return render_template('/carshare/verifycode.html',form=codeForm,error=error)


@carshare_app.route('/account_info',methods=['GET','POST'])
@login_required
def account_info():
    user_id = session['user_id']
    customer_uid = encrypt_hash(str(session['user_id']))
    user = User.query.filter(User.id==user_id).first()
    user = user if user.liscence_1 else None
    card = UserCard.query.filter_by(user_id = session['user_id']).first()
    userBank = UserBank.query.filter_by(user_id = session['user_id']).first()
    cardForm = CreditCardForm()
    cardError = None
    bankAccount = None
    accountError = None
    bankForm= BankAccountForm()
    userLiscenceForm=UserLiscenceForm()
    if cardForm.validate_on_submit():
        if not card:
            customer_uid = str(uuid.uuid4())
            card_registered,message = register_card(
                birth=cardForm.birth.data,
                password=cardForm.password.data,
                expire_month=cardForm.expire_month.data,
                expire_year=cardForm.expire_year.data,
                card_number=cardForm.card_1.data,
                customer_uid = customer_uid,
                user_id=user_id
            )
            if card_registered:
                card = UserCard(
                    name=cardForm.name.data,
                    user_id = user_id,
                    customer_uid =customer_uid,
                    )
                db.session.add(card)
                db.session.commit()
                request._tracking_data = {
                    'user_id':user_id,
                     'action':"add_card"
                     }
            else:
                cardError=message
        else:
            old_customer_uid = card.customer_uid
            customer_uid = str(uuid.uuid4())
            card_registered,message = register_card(
                birth=cardForm.birth.data,
                password=cardForm.password.data,
                expire_month=cardForm.expire_month.data,
                expire_year=cardForm.expire_year.data,
                card_number=cardForm.card_1.data,
                customer_uid = customer_uid,
                user_id=user_id,
                )

            if card_registered:
                response,message = delete_card(old_customer_uid)
                if response :
                    if response.status_code==200 and response.json().get('code')==0:
                        card.name = cardForm.name.data
                        card.customer_uid = customer_uid
                        db.session.commit()
                        request._tracking_data = {
                            'user_id':user_id,
                             'action':"modify_card"
                             }
                    else:
                        cardError="기존카드 삭제 실패"
                else:
                    cardError = "기존카드 삭제 실패"
            else:
                cardError=message
    else:
        if cardForm.errors.items():
            cardError = list(cardForm.errors.items())[0][1][0]

    return render_template('/carshare/account.html',
        user=user,
        userLiscenceForm=userLiscenceForm,
        userCard=card,
        userBank=userBank,
        cardForm =cardForm,
        cardError=cardError,
        accountError=accountError,
        bankAccount=bankAccount,
        bankForm = bankForm,
        customer_uid=customer_uid
        )



@carshare_app.route('/register_bank',methods=['POST'])
@login_required
def add_bank():
    bankForm = BankAccountForm()
    before_url = request.referrer if request.referrer else url_for('carshare_app.account_info')
    if bankForm.validate_on_submit():
        userBank =UserDao.add_bank_with_form(user_id=session['user_id'],form=bankForm)
        if userBank:
            return redirect(before_url)
        else:
            flash("통신오류가 발생했습니다. 잠시 후 다시 시도해주세요.",'bank_form')
            return redirect(before_url)

    else:
        bankError = list(bankForm.errors.items())[0][1][0]
        flash(bankError,'bank_form')
        return redirect(before_url)

@carshare_app.route('/register_liscence',methods=['POST'])
@login_required
def add_user_liscence():
    userLiscenceForm = UserLiscenceForm()
    before_url = request.referrer if request.referrer else url_for('carshare_app.account_info')
    if userLiscenceForm.validate_on_submit():
        userLiscence =UserDao.add_liscence_user(
            user_id=session['user_id'],
            liscence_1 = userLiscenceForm.liscence_1.data,
            liscence_2 = userLiscenceForm.liscence_2.data,
            liscence_3 = userLiscenceForm.liscence_3.data,
            liscence_4 = userLiscenceForm.liscence_4.data,
            serialNumber= userLiscenceForm.serialNumber.data,
            birth = userLiscenceForm.birth.data,
        )
        if userLiscence:
            return redirect(before_url)
        else:
            flash("통신오류가 발생했습니다. 잠시 후 다시 시도해주세요.",'liscence_form')
            return redirect(before_url)

    else:
        liscence_error = list(userLiscenceForm.errors.items())[0][1][0]
        flash(liscence_error,'liscence_form')
        return redirect(before_url)


@carshare_app.route('/agree_term',methods=["POST"])
def agree_term():
    request_data = request.get_json()
    termForm = TermForm(data=request_data)
    result = {}
    if termForm.validate() and session.get('login_data'):
        email = session['login_data'].get('email')
        username = session['login_data'].get('username')
        profile = session['login_data'].get('profile')
        if not email or not username:
            result['message'] = "fail"
            return jsonify(result)

        user = User(
            name = username,
            email = email,
            password =  uuid.uuid4().hex[:6].upper()
            )

        if profile and not user.image:
            image_id = save_user_profile(profile,user.id)
            if image_id:
                user.image = image_id
        db.session.add(user)
        db.session.commit()
        session['user_id'] = user.id
        session['email'] = email
        session.pop("login_data")
        result['message'] = "success"
    else:
        result['message'] = "fail"
    return jsonify(result)

@carshare_app.route('/user_info/<string:user_id>')
def user_info(user_id=""):
    return render_template('carshare/userinfo.html')


@carshare_app.route('/login_userinfo')
@login_required
def loginuser_info(user_id=""):
    return redirect(url_for('carshare_app.user_info',user_id=session['user_id']))


@carshare_app.route('/earning')
@login_required
def earning_history():
    bankForm=BankAccountForm()
    bank = UserBank.query.filter(UserBank.user_id==session['user_id']).first()
    carList = Car.query\
        .filter(Car.user_id==session['user_id'] )\
        .all()
    owner_send_list = OwnerSend.query\
        .filter(OwnerSend.user_id==session['user_id'])\
        .filter(OwnerSend.rsp_code=="A0000").all()
    return render_template('carshare/earning.html',
        bankForm=bankForm,bank=bank,owner_send_list=owner_send_list,carList=carList,
        car_id=""
        )

@carshare_app.route('/earning/<string:car_id>')
@login_required
def earning_history_bycar(car_id=""):
    bankForm=BankAccountForm()
    bank = UserBank.query.filter(UserBank.user_id==session['user_id']).first()
    owner_send_list = OwnerSend.query\
        .filter(OwnerSend.user_id==session['user_id'])\
        .filter(CarBooking.car_id==car_id)\
        .filter(OwnerSend.rsp_code=="A0000").all()
    carList = Car.query\
        .filter(Car.user_id==session['user_id'] )\
        .all()
    return render_template(
    'carshare/earning.html',
        bankForm=bankForm,bank=bank,owner_send_list=owner_send_list,carList=carList,
        car_id=car_id
        )


@carshare_app.route('/owner_send/<string:owner_send_id>')
@login_required
@owner_send_matched
def owner_recipt(owner_send_id="",**kwargs):
    owner_send = kwargs['owner_send']
    return render_template('carshare/owner_recipt.html',owner_send=owner_send)
