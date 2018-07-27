import bcrypt
from application import db
from wtforms import validators, StringField, PasswordField,FloatField,TextAreaField,HiddenField,IntegerField,BooleanField
from wtforms.validators import ValidationError
from wtforms.fields.html5 import EmailField
from carupload.models import Car,CarImage,CarOption
from wtforms_alchemy import model_form_factory
from flask_wtf import FlaskForm


BaseModelForm = model_form_factory(FlaskForm)
BooleanField.false_values = {False, 'false', ''}

#Model과 Form을 연결시킬때 Integer Filed의 경우 0을 인식하지 못함 default 를 0으로 설정해야함.
class ModelForm(BaseModelForm):
    @classmethod
    def get_session(self):
        return db.session


class CarOptionForm(ModelForm):
    class Meta:
        model = CarOption
        exclude = ['register_date','weekly_discount','monthly_discount']
        include = ['id']
    sun_roof= BooleanField()
    smart_key=  BooleanField()
    hid_led=  BooleanField()
    seat_heater=  BooleanField()
    seat_cooler=  BooleanField()
    backword_sensor =  BooleanField()
    backword_cam =  BooleanField()
    side_airbag =  BooleanField()
    navigation =  BooleanField()

class CarOptionEditForm(CarOptionForm):
    class Meta:
        model = CarOption
        exclude = ['register_date','price','weekly_discount','monthly_discount']
        include = ['id']

class OrdinaryPriceForm(FlaskForm):
    class Meta:
        locales = ['kr']
        csrf = False

    ordinaryPrice = IntegerField('ordinaryPrice',[
        validators.NumberRange(
            min=5000,
            message='최소 5000원이상의 가격을 설정해주세요'
        )
    ])

    weeklyDiscount = IntegerField('weeklyDiscount',[
        validators.NumberRange(
            min=0,
            max=100,
            message='0 ~ 100사이의 정수를 입력해주세요'
        )
    ])
    monthlyDiscount = IntegerField('monthlyDiscount',[
        validators.NumberRange(
            min=0,
            max=100,
            message='0 ~ 100사이의 정수를 입력해주세요'
            )
    ])
