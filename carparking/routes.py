from flask import render_template, url_for, flash, redirect,request, flash, session
from carparking import app, db
from carparking.forms import AddCar
from carparking.models import Car
import string, random
from sqlalchemy import exc,asc,desc
from functools import wraps
import re
from datetime import datetime,timedelta
import json


# declared global variable to keep record of the cars in total and present in the parking
maxVal=totalCar=0

# decorator will check the format of the registration number, color and slot availability
def check(f):
	# passing all the args and kwargs received from the addparking route
	@wraps(f)
	def wrap(*args, **kwargs):
		global maxVal,totalCar
		try:
			regexRegNo = re.compile(r'^KA-\d\d-[A-Z][A-Z]-\d\d\d\d')
			regexCarColor = re.compile(r'Blue|Black|White|Red')
			carRegNo = request.form['regno']
			carColor = request.form['color']
			c=Car.query.filter_by(RegNo=request.form['regno']).first()
			if c is None:
				status=False
			else:
				status =c.SlotNo
			totalCarInParking = Car.query.all()
			flag =  all([False if c.RegNo==carRegNo and not status else True for c in totalCarInParking ])
			print(maxVal,totalCar)
			if regexRegNo.match(carRegNo)!= None and regexCarColor.match(carColor)!= None and flag and maxVal >= totalCar+1:
				print('here')
				#return f(*args,**kwargs)
			else:
				# flash use to show the warning messages
				flash('Check Car Details or the parking limit')
				return redirect(url_for('parking'))
		except Exception:
			flash('Error in adding car in parking')
			return redirect(url_for('parking'))
		return f(*args, **kwargs)
	return wrap



@app.route('/totalrevenue',methods=['POST'])
def totalrevenue():
	start = datetime.strptime(request.form['StartDate']+' 00:00:00',"%Y-%m-%d %H:%M:%S")
	end = datetime.strptime(request.form['EndDate']+' 00:00:00',"%Y-%m-%d %H:%M:%S")
	car = Car.query.filter(Car.Intime>= start).filter(Car.OutTime<= end).all()
	revenue = sum([c.RevenueGenerated for c in car])
	dataset = {}
	month = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']
	dates = [31,28,31,30,31,30,31,31,30,31,30,31]
	for s in range(int(start.strftime("%Y%m")), int(end.strftime("%Y%m"))):
		s=str(s)
		m=int(s[4:])
		if m>0 and m<13:
			tempstart = datetime(year=int(s[0:4]), month=m,day= 1,hour=0,minute=0,second=0,microsecond=000000)
			tempend = datetime(year=int(s[0:4]), month=m,day= dates[m-1],hour=0,minute=0,second=0,microsecond=000000)
			tempcar = Car.query.filter(Car.Intime>= tempstart).all()
			#print('____',tempstart,"\n\n",tempcar,"\n\n")
			temprevenue = sum([c.RevenueGenerated for c in tempcar])
			dataset[month[int(s[5:])-1]+' '+s[0:4]]= temprevenue
			#print(dataset)
	return render_template('totalrevenue.html',Revenue=revenue,StartDate= start, EndDate= end,dataset= dataset)


@app.route('/',methods=['GET','POST'])
def index():
	# always starting page with empty database 
	try:
		deleteAll= Car.query.all()
		Car.query.delete()
		db.session.commit()
	except exc.IntegrityError as e:
		db.session.rollback()
	return render_template('index.html')

@app.route('/deleteparking/<int:slot>',methods=['POST'])
def deleteparking(slot):
	try:
		global totalCar
		car = Car.query.filter_by(SlotNo=slot).first()
		car.SlotNo=-1*slot
		car.OutTime = datetime.now()
		delta = (car.OutTime-car.Intime).total_seconds()//3600
		if delta <= 1:
			car.RevenueGenerated=30
		elif delta>1 and delta<=3:
			car.RevenueGenerated=80
		else:
			car.RevenueGenerated=100*(delta//24)
		flash("Price to be paid = {} for car {} ".format(car.RevenueGenerated,car.RegNo))
		db.session.commit()
		totalCar-=1
	except Exception:
		flash('Failed to delete')
	return redirect(url_for('parking'))

#decorator to check all details are in correct form or not
@app.route('/addparking', methods=['POST'])
@check
def addparking():

	try:
		global maxVal,totalCar
		# finding nearest slot for the car
		carInParking = Car.query.order_by(asc(Car.SlotNo)).all()
		prev=value=0
		for c in carInParking:
			if c.SlotNo>0:
				if c.SlotNo-prev!=1:
					value=prev
					break
				prev=c.SlotNo

		if carInParking!= None:
			if prev==0:
				carSlotNo=1
			else:
				carSlotNo=prev+1
			print(Car.query.filter_by(RegNo=request.form['regno']).first())
			d= datetime.strptime(request.form['InTimeDate']+' '+request.form['InTimeTime']+':00',"%Y-%m-%d %H:%M:%S")
			print(d)
			if Car.query.filter_by(RegNo=request.form['regno']).first() is None:
				newCar = Car(RegNo=request.form['regno'], Color=request.form['color'],  Status=True, SlotNo=int(carSlotNo),
					Intime=d,OutTime=datetime.now(),RevenueGenerated=30)
			else:
				newCar = Car.query.filter_by(RegNo=request.form['regno']).first()
				newCar.SlotNo,newCar.Status,newCar.Intime= int(carSlotNo), True, d
			try:
				db.session.add(newCar)
				db.session.commit()
				totalCar+=1
			except ValueError:
				db.session.rollback()
				flash('Database Error')
	except ValueError:
		flash('Some Error Occurred')
	return redirect(url_for('parking'))

# page to show the detail info about the cars in the parking
@app.route('/parking',methods=['GET','POST'])
def parking():
    if request.method =='POST':
        details=request.form
        try:
        	global maxVal,totalCar
	        if int(details['cars']) >= int(details['randomcars']):
	        	maxVal = int(details['cars'])
				#generating random cars registration number and slot number
		        colorString=['Black','White', 'Blue', 'Red']
		        for j in range(int(details['randomcars'])):
		        	regNo = 'KA-'+"".join([random.choice(string.digits) for i in range(2)])+'-'+"".join([random.choice(string.ascii_uppercase) for i in range(2)])+"-"+"".join([random.choice(string.digits) for i in range(4)])
		        	carColor= colorString[random.randint(0,3)]
		        	# inserting pre-car data into the database
		        	preCar = Car(RegNo=regNo, Color=carColor, SlotNo=j+1, Status=True,Intime=datetime.now()-timedelta(days=random.randint(0,100), hours= random.randint(0,24), minutes= random.randint(0,60)),
		        		OutTime=datetime.now(),RevenueGenerated=30)
		        	try:
		        		db.session.add(preCar)
		        		db.session.commit()
	        			totalCar = int(details['randomcars'])
		        	except exc.IntegrityError as e:
		        		#print("IntegrityError")
		        		db.session.rollback()
		        	carDetails = Car.query.order_by(asc(Car.SlotNo)).all()
		        return render_template('parking.html' ,details=carDetails)
        	else:
        		flash('Total cars should be greater than random cars')
        		return redirect(url_for('index'))	
        except ValueError:
        	flash('Please Enter integer value in the fields')
	        return redirect(url_for('index'))
        except  Exception:
        	print(request.method)
        	return redirect(url_for('index'))
    
    carDetails = Car.query.order_by(asc(Car.SlotNo)).all()
    return render_template('parking.html' ,details=carDetails)
    

# Registration numbers of all cars of a particular colour.
@app.route('/colorslot', methods=['POST'])
def colorslot():
	try:
		color = request.form.getlist('selectVal')[0]
		if color=='Default':
			return redirect(url_for('parking'))
		car = Car.query.filter_by(Color=color).all()
		return render_template('colorslot.html' ,details=car)
	except Exception:
		flash('Error in finding car of that color')
	return redirect(url_for('parking'))

# Slot number in which a car with a given registration number is parked.
@app.route('/searchcar', methods=['POST'])
def searchcar():
	try:
		regNo = request.form.getlist('search')[0].strip()
		regcar = Car.query.filter_by(RegNo=regNo).first()
		return render_template('regslot.html', car=regcar)
	except Exception:
		flash('Error Occurred while searching for car')
	return redirect(url_for('parking'))

# Slot numbers of all slots where a car of a particular colour is parked.
@app.route('/slotnocolor', methods=['POST'])
def slotnocolor():
	try:
		color = request.form.getlist('color')[0]
		car = Car.query.filter_by(Color=color).all()
		print(car,' ',color)
		return render_template('slotnocolor.html',details=car)
	except Exception:
		flash('Error in finding slot for that color')
	return redirect(url_for('parking'))