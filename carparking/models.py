from carparking import db
from datetime import datetime

# creating database for the Cars
class Car(db.Model):
    RegNo = db.Column(db.String(20), unique=True, nullable=False,primary_key=True)
    Color = db.Column(db.String(20),  nullable=False)
    Status = db.Column(db.Boolean,default=False)
    SlotNo = db.Column(db.Integer,nullable=True, unique= True)
    Intime = db.Column(db.DateTime,nullable=False ,default=datetime.now)
    OutTime = db.Column(db.DateTime,default='')
    RevenueGenerated = db.Column(db.Integer, default=30)

    def __repr__(self):
        # how the data represent from the database
        return "car('{}', '{}','{}','{}','{}','{}','{}')".format(
                self.RegNo,self.Color,self.Status,self.SlotNo,self.RevenueGenerated,
                self.Intime,self.OutTime 
            )

