from mongoengine import CASCADE
from application import mdb as db

class CarBrand(db.DynamicDocument):
    meta = {
        'collection': 'carBrand',
        'indexes':['codeName']
    }
    codeName= db.StringField(db_field="codeName",required=True)
    code= db.StringField(db_field="code",required=True)

class CarClass(db.DynamicDocument):
    meta = {
        'collection': 'carClass',
        'indexes':['makerName','makerCode']
    }
    makerName = db.StringField(db_field="makerName",required=True)
    makerCode = db.StringField(db_field="makerCode",required=True)
    codeName= db.StringField(db_field="codeName",required=True)
    code= db.StringField(db_field="code",required=True)

class CarModel(db.DynamicDocument):
    meta = {
        'collection': 'carModel',
        'indexes':['className']
    }
    makerName = db.StringField(db_field="makerName",required=True)
    makerCode = db.StringField(db_field="makerCode",required=True)
    className= db.StringField(db_field="className",required=True)
    classCode= db.StringField(db_field="classCode",required=True)
    codeName= db.StringField(db_field="codeName",required=True)
    code= db.StringField(db_field="code",required=True)
