from functools import wraps
from flask import session,request,redirect,url_for, abort
from caruser.models import User
from carupload.models import Car
from carbooking.models import UserCard,CarBooking, OwnerSend
from application import db
from utilities.dao.userdao import UserDao
from utilities.hashutil import encrypt_hash,decrypt_hash
from flask import jsonify

def login_required(f):
    @wraps(f)
    def decorated_function(*args,**kwargs):
        if session.get('email') is None or session.get('user_id') is None:
            return redirect(url_for('carshare_app.login_page',next=request.url))
        return f(*args,**kwargs)
    return decorated_function

def logout_required(f):
    @wraps(f)
    def decorated_function(*args,**kwargs):
        if session.get('email') or session.get('user_id') :
            return redirect(url_for('carshare_app.homepage',next=request.url))
        return f(*args,**kwargs)
    return decorated_function

def phonenumber_required(f):
    @wraps(f)
    def decorated_function(*args,**kwargs):
        if not session.get('phonenumber') :
            return redirect(url_for('carshare_app.homepage',next=request.url))
        return f(*args,**kwargs)
    return decorated_function



def registered_phone_required(f):
    @wraps(f)
    def decorated_function(*args,**kwargs):
        email = session.get('email')
        if not email :
            return redirect(url_for('carshare_app.login_page',next=request.url))
        user =  User.query.filter_by(email=email).one()
        if not user.phone:
            return redirect(url_for('carshare_app.send_code_page',next=request.url))
        return f(*args,**kwargs)
    return decorated_function

def nophone_required(f):
    @wraps(f)
    def decorated_function(*args,**kwargs):
        email = session.get('email')
        if not email :
            return redirect(url_for('carshare_app.homepage',next=request.url))
        user =  User.query.filter_by(email=email).one()
        if user.phone:
            return redirect(url_for('carshare_app.homepage',next=request.url))

        return f(*args,**kwargs)
    return decorated_function

def car_owner_match(f):
    @wraps(f)
    def decorated_function(*args,**kwargs):
        car_id = kwargs['car_id']
        email = session['email'] if session.get("email") else 'hmmon@sharemonsters.net'
        user_id = UserDao.get_user_id(email)
        car  = Car.query.filter(Car.id==car_id).first()
        if not car:
            abort(403,"No car exists")
        elif car.user_id != user_id:
            abort(403,"This car is not yours")
        return f(*args,**kwargs)
    return decorated_function

def api_login_match(f):
    @wraps(f)
    def decorated_function(*args,**kwargs):
        email = session['email'] if session.get("email") else 'hmmon@sharemonsters.net'
        user = UserDao.get_user_obj(email)
        if not user:
            abort(403,"user not login")
        session['email'] = email
        session['user_id'] = user.id
        return f(*args, **kwargs)
    return decorated_function

def auth_required(f):
    @wraps(f)
    def decorated_function(*args,**kwargs):
        user_id = session.get('user_id')
        data = request.get_json()
        token = data.get('auth_token')
        decrypt_user_id = decrypt_hash(token)
        if str(user_id) !=decrypt_user_id :
            print(decrypt_user_id)
            abort(403,"autorization failed")
        return f(*args, **kwargs)
    return decorated_function

def cannot_confirm_own_car(f):
    @wraps(f)
    def decorated_function(*args,**kwargs):
        request_data = request.get_json()
        car_id = request_data['car_id']
        email = session.get('email')
        if not email:
            return f(*args, **kwargs)
        user_id = UserDao.get_user_id(email)
        car  = Car.query.filter(Car.id==car_id).first()
        if car.user_id == user_id:
            result = {}
            result['message']='fail'
            result['errorMessage']='본인의 차는 예약할 수 없습니다.'
            return jsonify(result)
        return f(*args, **kwargs)
    return decorated_function

def user_card_registered(f):
    @wraps(f)
    def decorated_function(*args,**kwargs):
        user_id = session.get('user_id')
        user_card = UserCard.query.filter(UserCard.user_id==user_id).filter(UserCard.active==True).first()
        if not user_card:
            result = {}
            result['message'] = 'fail'
            return jsonify(result)
        return f(*args, **kwargs)
    return decorated_function


def verify_booking_matched(f):
    @wraps(f)
    def decorated_function(*args,**kwargs):
        booking_id = kwargs.get('booking_id')
        user_id = session['user_id']
        booking = CarBooking.query.filter(CarBooking.id == booking_id).first()
        if not booking:
            abort(404,"Not valid url ")
        if not user_id==booking.renter_id and not booking.car.user_id==user_id:
            return abort(403,"owner not matched")
        kwargs['booking'] = booking
        kwargs['is_car_owner'] = user_id == booking.car.user_id
        return f(*args,**kwargs)
    return decorated_function


def owner_send_matched(f):
    @wraps(f)
    def decorated_function(*args,**kwargs):
        os_id = kwargs.get('owner_send_id')
        owner_send = OwnerSend.query.filter(OwnerSend.id==os_id).first()
        if not owner_send:
            abort(404,"Not valid url")
        if owner_send.id != os_id:
            return abort(403,"owner not matched")
        kwargs['owner_send'] = owner_send
        return f(*args,**kwargs)
    return decorated_function


def admin_login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        response_object = {
            'status': 'fail',
            'message': 'fail'
        }
        auth_header = request.headers.get('Authorization')
        if not auth_header:
            return jsonify(response_object), 403
        auth_token = auth_header.split(" ")[1]
        resp = User.decode_auth_token(auth_token)
        user = User.query.filter_by(id=resp).first()
        if not user :
            return jsonify(response_object), 401
        if not user.admin:
            return jsonify(response_object), 401
        return f( *args, **kwargs)
    return decorated_function
