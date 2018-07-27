from application import db
from caruser.models import User,UserBank
from flask import session,request
from utilities.imaging import save_user_profile
from utilities.hashutil import encrypt_hash,decrypt_hash
import uuid
from datetime import datetime as dt

class UserDao(object):

    def get_user_phone(self,email):
        user  = User.query.filter(User.email==email).first()
        return user.phone

    @classmethod
    def get_user_phone_byid(self,id):
        user  = User.query.filter(User.id==id).first()
        return user.phone

    @classmethod
    def get_user_name(self,email):
        user  = User.query.filter(User.email==email).first()
        return user.name



    @classmethod
    def add_user(self,name,email,password,admin=False):
        user = User(name=name, email =email,password=password,admin=admin)
        db.session.add(user)
        db.session.commit()
        return user


    @classmethod
    def get_user_id(self,email):
        user  = User.query.filter(User.email==email).first()
        return user.id


    @classmethod
    def get_user_obj(self,email):
        user  = User.query.filter(User.email==email).first()
        return user


    @classmethod
    def login_user(self,email,username,profile,data={}):
        user =  User.query.filter_by(email = email).first()
        if not user:
            session['login_data'] = {}
            session['login_data']['email'] = email
            session['login_data']['username'] = username
            session['login_data']['profile'] = profile
            data['first_time'] = True

        else:
            session['email']  = email
            data['first_time'] = False
            session['user_id'] = user.id

            if "next" in session:
                data['next_url'] = session['next']
                session.pop("next")

            else:
                data['next_url']=False

            if profile and not user.image:
                image_id = save_user_profile(profile,user.id)
                if image_id:
                    user.image = image_id
                    db.session.commit()

        data['message'] = "success"
        return data

    @classmethod
    def add_user_bank_account(self,responseObj):
        try:
            userBank = UserBank.query.filter_by(user_id = session['user_id']).first()
            if userBank:
                userBank.bank_code_std = responseObj.get('bank_code_std')
                userBank.bank_code_sub = responseObj.get('bank_code_sub')
                userBank.bank_name = responseObj.get('bank_name')
                userBank.account_holder_info = responseObj.get('account_holder_info')
                userBank.account_num = responseObj.get('account_num')
                userBank.register_date = dt.now()
                userBank.account_holder_name = responseObj.get('account_holder_name')
                db.session.commit()
                request._tracking_data = {
                    'user_id':session['user_id'],
                     'action':'modify_bank'
                     }
            else:
                userBank = UserBank(
                    user_id = session['user_id'],
                    bank_code_std = responseObj.get('bank_code_std'),
                    bank_code_sub = responseObj.get('bank_code_sub'),
                    bank_name = responseObj.get('bank_name'),
                    account_holder_info = responseObj.get('account_holder_info'),
                    account_num = responseObj.get('account_num'),
                    register_date = dt.now(),
                    account_holder_name = responseObj.get('account_holder_name'),
                )
                db.session.add(userBank)
                db.session.commit()
                request._tracking_data = {
                    'user_id':session['user_id'],
                     'action':'add_bank'
                     }
            return userBank
        except Exception as e:
            return None
    @classmethod
    def add_bank_with_form(self,user_id,form):
        choice_list = form.bank_code_std.choices
        bank_code = form.bank_code_std.data
        bank_name=list(filter(lambda x: x[0]==bank_code ,choice_list))[0][1]
        userBank = UserBank.query.filter_by(user_id = user_id).first()
        if userBank:
            userBank.account_holder_info = form.account_holder_info.data
            userBank.account_holder_name = form.account_holder_name.data,
            userBank.bank_code_std = bank_code
            userBank.bank_name = bank_name
            userBank.account_num = form.account_num.data
            request._tracking_data = {
                'user_id':user_id,
                 'action':'modify_bank'
                 }
            db.session.commit()

        else:
            userBank = UserBank(
                user_id = user_id,
                account_holder_name=form.account_holder_name.data,
                account_holder_info=form.account_holder_info.data,
                bank_code_std = bank_code,
                bank_name = bank_name,
                account_num = form.account_num.data,
                register_date = dt.now(),
            )
            db.session.add(userBank)
            db.session.commit()
            request._tracking_data = {
                'user_id':user_id,
                 'action':'add_bank'
                 }
        return userBank

    @classmethod
    def add_liscence_user(self,user_id,liscence_1,liscence_2,liscence_3,liscence_4,serialNumber,birth):
        user = User.query.filter_by(id = user_id).first()
        if user:
            user.liscence_1 = liscence_1
            user.liscence_2 = encrypt_hash(liscence_2)
            user.liscence_3 = encrypt_hash(liscence_3)
            user.liscence_4 = encrypt_hash(liscence_4)
            user.serial = encrypt_hash(serialNumber)
            user.birth = encrypt_hash(birth)
            db.session.commit()
            request._tracking_data = {
                'user_id':user_id,
                 'action':'add_user_liscence'
                 }
            return user
        else:
            return False

    @classmethod
    def get_user_liscence(self,user_id):
        user = User.query.filter_by(id = user_id).first()
        result={}
        if user and user.liscence_1:
            result['liscence_1'] = user.liscence_1
            result['liscence_2'] = decrypt_hash(user.liscence_2)
            result['liscence_3'] = decrypt_hash(user.liscence_3)
            result['liscence_4'] = decrypt_hash(user.liscence_4)
            result['serialNumber'] = decrypt_hash(user.serial)
            result['birth'] = decrypt_hash(user.birth)
            result['message']="success"
            return result
        else:
            result['message']="fail"
            return result
