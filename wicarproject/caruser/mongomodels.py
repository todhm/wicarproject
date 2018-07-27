from mongoengine import CASCADE,DynamicField
from application import mdb as db
from datetime import datetime as dt
class BestCar(db.DynamicDocument):
    meta = {
        'collection': 'bestcars',
        'indexes':['-register_date']
    }
    car_list= db.DynamicField(db_field="cl",required=True)
    register_date = db.DateTimeField(db_field="rd",default=dt.now())
