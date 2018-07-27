import bcrypt
from flask_wtf import FlaskForm,Form
from wtforms import validators, StringField, PasswordField,FloatField,TextAreaField,HiddenField,DateField,BooleanField,DateTimeField
from wtforms.fields import FormField,FieldList,IntegerField,SelectField
from wtforms.validators import ValidationError,Optional
from wtforms.fields.html5 import EmailField,TelField
from datetime import datetime as dt
from carbooking.models import VacationData,CarPriceSchedule
from utilities.timeutil import find_duplicate_time
from utilities.common import BaseForm

BooleanField.false_values = {False, 'false', ''}


class DailyAvailable(FlaskForm):
    class Meta:
        csrf = False
    start = IntegerField('start')
    end = IntegerField('end')
    dailyAlways = IntegerField('dailyAlways')

class AvailableForm(FlaskForm):
    class Meta:
        csrf=False
    rentAlways = BooleanField([validators.DataRequired("상시선택여부를 입력해주세요!")])
    availability = FieldList(FormField(DailyAvailable))





    def validate(self):
        if not super().validate():
            return False
        result=True
        if not self.rentAlways.data:
            length_availability = len(self.availability.data)
            if not length_availability==7:
                self.availability.errors.append("Not enough data")
                result=False
            for availability in self.availability.data:
                if not(int(availability['dailyAlways']) ==2 or int(availability['dailyAlways']) ==1 or int(availability['dailyAlways']) ==0):
                    self.availability.errors.append("Not valid availability")
                    result = False
                if int(availability['dailyAlways'])==1:
                    if int(availability['start'])> int(availability['end']):
                        result = False
                        self.availability.errors.append("Invalid Time")

        return result


class VacationForm(FlaskForm):
    class Meta:
        csrf=False
    start_time = DateTimeField(format="%Y-%m-%d %H:%M")
    end_time = DateTimeField(format="%Y-%m-%d %H:%M")
    user_id = HiddenField()
    def validate(self):
        if not super().validate():
            return False
        result = True
        if self.start_time.data>= self.end_time.data:
            self.start_time.errors.append("시작시간이 종료시간보다 큽니다.")
            result = False
        vacation_list = VacationData\
                            .query\
                            .filter(VacationData.user_id == self.user_id.data)\
                            .filter(VacationData.end_time > dt.now()).all()
        if vacation_list:
            for vacation in vacation_list:
                duplication_check = find_duplicate_time(
                    vacation.start_time,
                    vacation.end_time,
                    self.start_time.data,
                    self.end_time.data
                    )
                if duplication_check:
                    result=False
                    self.start_time.errors.append("중복되는 시간이 존재합니다.")
        return result


class BookCheckingForm(FlaskForm):
    class Meta:
        csrf=False
    start_time = DateTimeField(format="%Y-%m-%d %H:%M")
    end_time = DateTimeField(format="%Y-%m-%d %H:%M")
    car_id = HiddenField()


class CardNumberForm(FlaskForm):

    name = StringField('카드별명',[
        validators.DataRequired("카드등록에러")
        ])

    customer_uid = StringField("",[
        validators.DataRequired("카드등록에러")
        ])


class NiceCardForm(FlaskForm):

    name = StringField('카드명',[
        validators.DataRequired("카드등록애러")
        ])
    birth = TelField('카드주 생년월일(6자리)',[
        validators.DataRequired("카드주의 생년월일을 입력해주세요"),
        validators.Length(min=6, max=6,message="생년월일의 형식이 맞지 않습니다.")
    ])
    card_1 = TelField('카드번호',[
        validators.DataRequired('카드번호에러'),
        validators.Length(min=19, max=19,message='카드번호 형식이 옳지 않습니다.')
    ])
    card_2 = TelField()
    card_3 = TelField()
    card_4 = TelField()
    expire_year =SelectField('만료년도',[
        validators.DataRequired("년도를 입력해주세요")
        ],
        choices=[ ( str(i), str(i)) for i in range(dt.now().year,dt.now().year+50)])

    expire_month = SelectField('만료월',[
        validators.DataRequired("달을 입력해주세요."),
        validators.Length(min=2, max=2)
        ],
        choices=[
            ('01','01'),
            ('02','02'),
            ('03','03'),
            ('04','04'),
            ('05','05'),
            ('06','06'),
            ('07','07'),
            ('08','08'),
            ('09','09'),
            ('10','10'),
            ('11','11'),
            ('12','12')
            ])

    cvc = TelField('CVC',[
        validators.DataRequired("cvc번호를 입력해주세요."),
        validators.Length(min=3, max=3,message="cvc번호는 3자리 숫자를 입력해주세요")
        ])
    password = PasswordField('비밀번호앞 2자리',[
        validators.DataRequired("비밀번호 앞 2자리를 입력해주세요."),
        validators.Length(min=2, max=2,message="비밀번호는 2자리를 입력해주세요.")
      ])

    def validate(self):
        if self.card_2.data and self.card_3.data and self.card_4.data:
            self.card_1.data = self.card_1.data + "-" + self.card_2.data+"-" + self.card_3.data+ "-"+ self.card_4.data
        if not super().validate():
            return False


        return True


class CreditCardForm(FlaskForm):

    name = StringField('카드명',[
        validators.DataRequired("카드등록애러")
        ])
    birth = TelField('카드주 생년월일(6자리)',[
        validators.DataRequired("카드주의 생년월일을 입력해주세요"),
        validators.Length(min=6, max=6,message="생년월일의 형식이 맞지 않습니다.")
    ])
    card_1 = TelField('카드번호',[
        validators.DataRequired('카드번호에러'),
        validators.Length(min=19, max=19,message='카드번호 형식이 옳지 않습니다.')
    ])
    expire_year =SelectField('만료년도',[
        validators.DataRequired("년도를 입력해주세요")
        ],
        choices=[ ( str(i), str(i)) for i in range(dt.now().year,dt.now().year+50)])

    expire_month = SelectField('만료월',[
        validators.DataRequired("달을 입력해주세요."),
        validators.Length(min=2, max=2)
        ],
        choices=[
            ('01','01'),
            ('02','02'),
            ('03','03'),
            ('04','04'),
            ('05','05'),
            ('06','06'),
            ('07','07'),
            ('08','08'),
            ('09','09'),
            ('10','10'),
            ('11','11'),
            ('12','12')
            ])

    cvc = TelField('CVC',[
        validators.DataRequired("cvc번호를 입력해주세요."),
        validators.Length(min=3, max=3,message="cvc번호는 3자리 숫자를 입력해주세요")
        ])
    password = PasswordField('비밀번호앞 2자리',[
        validators.DataRequired("비밀번호 앞 2자리를 입력해주세요."),
        validators.Length(min=2, max=2,message="비밀번호는 2자리를 입력해주세요.")
      ])

    def validate(self):
        if len(self.card_1.data)==16:
            self.card_1.data = self.card_1.data[0:4] + "-" + self.card_1.data[4:8]+"-" + self.card_1.data[8:12]+ "-"+ self.card_1.data[12:]
        if not super().validate():
            return False


        return True
class BookingForm(FlaskForm):
    class Meta:
        csrf=False
    start_time = DateTimeField(format="%Y-%m-%d %H:%M")
    end_time = DateTimeField(format="%Y-%m-%d %H:%M")
    car_id = HiddenField()


class ConfirmForm(FlaskForm):
    confirm = HiddenField('confirm',[validators.DataRequired()],default="confirm")

class OwnerCancelForm(FlaskForm):
    disallow = HiddenField('disallow',[validators.DataRequired()],default="disallow")

class UserCancelForm(FlaskForm):
    cancel = HiddenField('cancel',[validators.DataRequired()],default="cancel")

class MessageForm(FlaskForm):
    message = TextAreaField('message',[validators.DataRequired('메세지를 입력해주세요')])

class ReviewForm(FlaskForm):
    review = TextAreaField('message')
    review_point = SelectField('리뷰점수',[
        validators.DataRequired("리뷰 점수를 입력해주세요.")
        ],
        choices=[
            (5,5),
            (4.5,4.5),
            (4,4),
            (3.5,3.5),
            (3,3),
            (2.5,2.5),
            (2,2),
            (1.5,1.5),
            (1,1),
            (0.5,0.5),
            (0,0)
            ],coerce=float
            )


class VacationScheduleForm(BaseForm):
    class Meta:
        csrf=False
    start_time = DateTimeField(format="%Y-%m-%d")
    end_time = DateTimeField(format="%Y-%m-%d")
    car_id = HiddenField()
    def validate(self,vacation_list):
        if not super().validate():
            return False
        result = True
        if self.start_time.data> self.end_time.data:
            self.start_time.errors.append("시작시간이 종료시간보다 큽니다")
            result = False

        if vacation_list:
            for vacation in vacation_list:
                duplication_check = find_duplicate_time(
                    vacation.start_time,
                    vacation.end_time,
                    self.start_time.data,
                    self.end_time.data
                    )
                if duplication_check:
                    result=False
                    self.start_time.errors.append("중복된 시간입니다")
                    return result
        return result

class CarVacationUpdateForm(VacationScheduleForm):
    id = HiddenField()

class CarPriceScheduleForm(VacationScheduleForm):
    price = IntegerField()

class CarPriceUpdateForm(CarPriceScheduleForm):
    id = HiddenField()
