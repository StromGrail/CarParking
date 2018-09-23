import unittest
from carparking import db,app
from carparking.models import Car
import os

#status code HTTP_200 means OK page is working fine
# status code HTTP_302 means FOUND


#basic test for checking everything running fine
class BasicTestCase(unittest.TestCase):
	# checking app is running fine or not
	def test_index(self):
		tester = app.test_client(self)
		response = tester.get('/',content_type='html/text') 
		self.assertEqual(response.status_code,200)

	# checking database is working fine or not
	def test_database(self):
		car = Car(RegNo='KA-49-MY-0717',Color='Red',Status=True,SlotNo=1)
		db.session.add(car)
		db.session.commit()
		self.assertIn( car, db.session)

# Main Test class
class CarparkingTestCase(unittest.TestCase):

	def setUp(self):
		"""Set up a blank temp database before each test"""
		basedir = os.path.abspath(os.path.dirname(__file__))
		app.config['TESTING'] = True
		app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + \
            os.path.join(basedir, 'test.db')
		self.app = app.test_client()
		db.create_all()		
		self.car = Car(RegNo='KA-49-MY-0803',Color='Red',Status=True,SlotNo=1)
		db.session.add(self.car)
		db.session.commit()
		self.assertIn( self.car, db.session)

	def tearDown(self):
		"""Destroy blank temp database after each test"""
		db.drop_all()


	# testing each routes of the app with their applicable methods
	def test_parking(self):
		self.assertEqual( self.app.get('/parking').status_code, 200)
		self.assertEqual( self.app.post('/parking',
			data=dict(cars=10,randomcars=2)).status_code, 200)

	def test_addparking(self):
		self.assertEqual(self.app.post('/addparking',data=dict(regno='KA-49-MY-0804',color='Red')).status_code, 302)
		# Raising error
		self.assertEqual(self.app.post('/addparking',data=dict(regno='KA-49-MY-0803',color='Violet')).status_code, 302)
		c = Car.query.all()
		print(c)

	def test_colorslot(self):
		self.assertEqual( self.app.post('/colorslot', 
			data=dict(selectVal=list('Default'))).status_code, 200)

	def test_searchcar(self):
		self.assertEqual( self.app.post('/searchcar', 
			data= dict(search='KA-49-MY-0803') ).status_code, 200)

	def test_deleteparking(self):
		self.assertEqual( self.app.post('/deleteparking/%d'%int(self.car.SlotNo)).
			status_code, 302)

	def test_slotnocolor(self):
		self.assertEqual( self.app.post('/slotnocolor', 
			data=dict(color=list('Red'))).status_code, 200)