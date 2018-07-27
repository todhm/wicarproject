from caruser.models import User
from caruser.forms import LoginForm
from flask_wtf import Form
from wtforms import validators, StringField, PasswordField,FloatField,TextAreaField,HiddenField,DateField,BooleanField,DateTimeField
from wtforms.fields import FormField,FieldList,IntegerField,SelectField
from wtforms.validators import ValidationError,Optional
from wtforms.fields.html5 import EmailField,TelField
from utilities.common import BaseForm


class AdminLoginForm(LoginForm):



    def validate(self):
        if not super().validate():
            return False
        result = True
        user = User.query.filter_by(email = self.email.data).first()
        if not user.admin:
            self.email.errors.append("관리자가아닙니다")
            result=False

        return result



class BaseDateForm(BaseForm):
    class Meta:
        csrf = False

    startDate = DateTimeField(format="%Y-%m-%d")
    endDate = DateTimeField(format="%Y-%m-%d")

    def validate(self):

        if not super().validate():
            return False
        self.startDate.data = self.startDate.data.replace(hour=0,minute=0,second=0)
        self.endDate.data = self.endDate.data.replace(hour=23,minute=59,second=59)
        if self.startDate.data >= self.endDate.data:
            self.start_time.errors.append("시작시간이 종료시간보다 큽니다")
            return False
        return True

class BookingListForm(Form):
    class Meta:
        csrf = False
    id = StringField()
    owner_earning = IntegerField()


class OwnerSendForm(BaseForm):
    class Meta:
        csrf = False

    owner_phone = TelField()
    ownerId = StringField()
    total_earning = IntegerField()
    booking_list = FieldList(BookingListForm)


class OwnerSendListForm(BaseForm):
    class Meta:
        csrf = False
    checkedList = FieldList(OwnerSendForm)
