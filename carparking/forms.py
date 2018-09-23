from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField,IntegerField
from wtforms.validators import DataRequired, Length, Email, EqualTo , ValidationError
from carparking import db
from carparking.models import Car
from datetime import datetime


class AddCar(FlaskForm):

    RegNo = StringField('RegNo',
                           validators=[DataRequired(), Length(min=13, max=13)])
    Color = StringField('Color',
                           validators=[DataRequired(), Length(min=2, max=20)])
    SlotNo = StringField('SlotNo',
                           validators=[DataRequired(), Length(min=1)])
    Status = BooleanField('Status' , default= False)

    Intime = StringField('Intime',validators=[DataRequired(), Length(min=2, max=20)])

    OutTime = StringField('OutTime',validators=[ Length(min=2, max=20)])
    
    RevenueGenerated = IntegerField('RevenueGenerated', default=30)

    submit = SubmitField('Add')
    