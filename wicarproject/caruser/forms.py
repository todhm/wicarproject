import bcrypt
from flask_wtf import FlaskForm
from wtforms import validators, StringField, PasswordField,FloatField,TextAreaField,HiddenField,DateField,BooleanField
from wtforms.fields import SelectField
from wtforms.validators import ValidationError
from wtforms.fields.html5 import EmailField,TelField
from datetime import datetime as dt
from caruser.models import User
from utilities.timeutil import get_time_comb
from utilities.common import get_liscence_region_choices
time_list =  get_time_comb()['timeLabel']
region_choices=get_liscence_region_choices()
class SearchForm(FlaskForm):
    address = HiddenField('address',[validators.DataRequired("주소를 입력해주세요.")])
    pointX = HiddenField('pointX')
    pointY = HiddenField('pointY')
    startDate = DateField("시작일", format='%m/%d/%Y')
    endDate = DateField("시작일", format='%m/%d/%Y')
    startTime = SelectField('시작시간',
        choices=[ (
             str(i),
             dt.strftime(dt.strptime("2018-01-01 "+str(i),'%Y-%m-%d %H:%M'),"%I:%M %p")
             ) for i in time_list
             ],
         default="10:00"
        )
    endTime =SelectField('종료시간',
        choices=[ (
             str(i),
             dt.strftime(dt.strptime("2018-01-01 "+str(i),'%Y-%m-%d %H:%M'),"%I:%M %p")
             ) for i in time_list
             ],
        default="10:00"
        )


    def validate(self):
        if not super().validate():
            return False
        result = True
        start_date_time = dt.strftime(self.startDate.data,'%m/%d/%Y') +" "+self.startTime.data
        end_date_time = dt.strftime(self.endDate.data,"%m/%d/%Y") +" "+self.endTime.data
        start_date_time = dt.strptime(start_date_time,'%m/%d/%Y %H:%M')
        end_date_time = dt.strptime(end_date_time,'%m/%d/%Y %H:%M')
        if start_date_time <= dt.now():
            self.startDate.errors.append("시간오류")
            result = False
        if start_date_time>= end_date_time:
            self.startDate.errors.append("시간오류")
            result = False
        return result


class SignUpForm(FlaskForm):
    email = EmailField('이메일주소', [
        validators.DataRequired(message= '이메일을 입력해주세요.'),
        validators.Email(message= '알맞지 않는 형식입니다.')
        ])

    username = StringField('사용자명', [
            validators.DataRequired(message='이름을 입력해 주세요.'),
            validators.Length(min=2, max=10,message='이름은 2 ~ 10자리의 글자여야합니다.')
        ])

    password = PasswordField('비밀번호', [
            validators.DataRequired('비밀번호를 입력해주세요.'),
            validators.EqualTo('confirm', message='비밀번호가 일치해야합니다.'),
            validators.Length(min=6, max=12,message='비밀번호는 6 ~12자리의 값이여야 합니다.')
        ])

    confirm = PasswordField('비밀번호 확인')

    def validate_email(form,field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError("이미 사용중인 Email입니다.")


class LoginForm(FlaskForm):
    email = EmailField('Email', [
            validators.DataRequired('email을 입력해주세요'),
            validators.Email(message= '알맞지 않는 형식입니다.')
        ])
    password = PasswordField('Password', [
            validators.DataRequired(message='비밀번호를 입력해주세요'),
            validators.Length(min=6, max=12,message='비밀번호는 6에서 12자리의 숫자입니다.')
        ])


    def validate_email(form,field):
        user = User.query.filter_by(email = field.data).first()
        if not user:
            raise ValidationError("존재하지 않는 이메일입니다.")
        if not user.check_password(form.password.data):
            raise ValidationError("비밀번호가 맞지 않습니다.")


class PhoneForm(FlaskForm):
    phonenumber = StringField('전화번호', [
            validators.DataRequired(message="번호를 입력해주세요."),
            validators.Length(min=9, max=16,message="번호의 길이가 맞지 않습니다.")
        ])

    def validate_phone(form, field):
        input_number = field.data
        input_number = input_number\
                        .replace("+","")\
                        .replace("-","")\
                        .replace("(")\
                        .replace(")","")\
                        .replace(" ","")

        if not input_number.isdigit():
            raise ValidationError("알맞지 않는 형식입니다.")

class BankAccountForm(FlaskForm):

        bank_code_std = SelectField('은행명',[
            validators.DataRequired("은행을 선택해주세요."),
            ],
            choices=[
                ('003','기업은행'),
                ('004','국민은행'),
                ('005','외환은행'),
                ('007','수협'),
                ('011','농협'),
                ('020','우리은행'),
                ('023','제일은행'),
                ('027','씨티은행'),
                ('031','대구은행'),
                ('032','부산은행'),
                ('034','광주은행'),
                ('035','제주은행'),
                ('037','전북은행'),
                ('039','경남은행'),
                ('045','새마을금고'),
                ('048','신협'),
                ('071','우체국'),
                ('081','하나은행'),
                ('088','신한은행'),
                ('097','오픈은행'),
                ('001','테스트은행')
                ])

        account_holder_name = StringField('계좌주 성명',[
            validators.DataRequired(message="계좌주의 성명을 입력해주세요")
        ])

        account_num = TelField('계좌번호',[
            validators.DataRequired(message="계좌번호를 입력해주세요.")
        ])
        account_holder_info = TelField('예금주 생년월일(법인일 경우 사업자등록번호)',[
            validators.DataRequired(message="예금주의 생년월일을 입력해주세요."),
            validators.Length(min=7, max=20,message='생년월일 7자리나 사업자등록번호가 필요합니다.')
        ])

class UserLiscenceForm(FlaskForm):

    liscence_1 =   SelectField('운전면허번호',[
        validators.DataRequired("운전면허번호를 입력해주세요"),
        ],
        choices=region_choices)
    liscence_2 = TelField("",[
        validators.DataRequired("운전면허번호를 입력해주세요"),
        ])
    liscence_3 = TelField("",[
        validators.DataRequired("운전면허번호를 입력해주세요"),
        ])
    liscence_4 = TelField("",[
        validators.DataRequired("운전면허번호를 입력해주세요"),
        ])
    serialNumber = StringField('일련번호',[
        validators.DataRequired(message="운전면허오른쪽 사진및 일련번호를 입력해주세요")
    ])
    birth =TelField('생년월일6자리',[
        validators.DataRequired(message="생년월일 6자리를 입력해주세요"),
        validators.Length(min=6, max=6,message='생년월일 6자리를 입력해주세요')
    ])

class UserLiscenceApiForm(UserLiscenceForm):
    class Meta:
        csrf = False

class CodeForm(FlaskForm):
    code = StringField('인증코드입력',[
        validators.DataRequired(message="인증코드를 입력해주세요.")
    ])


class TermForm(FlaskForm):
    privacy = BooleanField()
    term_service = BooleanField()
