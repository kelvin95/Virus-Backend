from app import db
from time import time


infections = db.Table('infections',
			db.Column('infector_id', db.Integer, db.ForeignKey('virus.id')),
			db.Column('infected_id', db.Integer, db.ForeignKey('virus.id')))

class Virusappearance(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	virus = db.relationship('Virus', backref='appearance', uselist=False)

	radius = db.Column(db.Float)
	speed = db.Column(db.Float)
	speed_variance = db.Column(db.Float)
	start_size = db.Column(db.Float)
	start_size_variance = db.Column(db.Float)
	finish_size = db.Column(db.Float)
	finish_size_variance = db.Column(db.Float)
	lifespan = db.Column(db.Float)
	lifespan_variance = db.Column(db.Float)
	start_color = db.Column(db.String())
	start_color_variance = db.Column(db.String())
	end_color = db.Column(db.String())
	end_color_variance = db.Column(db.String())

	def __init__(self, radius, speed, speed_variance, start_size, start_size_variance, 
				finish_size, finish_size_variance, lifespan, lifespan_variance, start_color,
				start_color_variance, end_color, end_color_variance):
		self.radius = radius
		self.speed = speed
		self.speed_variance = speed_variance
		self.start_size = start_size
		self.start_size_variance = start_size_variance
		self.finish_size = finish_size
		self.finish_size_variance = finish_size_variance
		self.lifespan = lifespan
		self.lifespan_variance = lifespan_variance
		self.start_color = start_color
		self.start_color_variance = start_color_variance
		self.end_color = end_color
		self.end_color_variance = end_color_variance

	def generate_json(self):
		return {'id':self.id,
				'virus_id':self.virus.id, 
				'radius':self.radius,
				'speed':self.speed,
				'speed_variance':self.speed_variance,
				'start_size':self.start_size,
				'start_size_variance':self.start_size_variance,
				'finish_size':self.finish_size,
				'finish_size_variance':self.finish_size_variance,
				'lifespan':self.lifespan,
				'lifespan_variance':self.lifespan_variance,
				'start_color':self.start_color,
				'start_color_variance':self.start_color_variance,
				'end_color':self.end_color,
				'end_color_variance':self.end_color_variance
		}

class Infection(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	infected_id = db.Column(db.Integer, db.ForeignKey('virus.id'))
	infector_id = db.Column(db.Integer, db.ForeignKey('virus.id'))
	infected_at = db.Column(db.Integer)

	def __init__(self, infector, infected):
		self.infector = infector
		self.infected = infected
		self.infected_at = time()


class Virus(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	appearance_id = db.Column(db.Integer, db.ForeignKey('virusappearance.id'))
	name = db.Column(db.String())
	max_energy = db.Column(db.Integer)
	longevity = db.Column(db.Integer)
	points = db.Column(db.Integer)
	rank = db.Column(db.Integer)

	infected = db.relationship('Infection', primaryjoin=(id==Infection.infector_id), 
					backref=db.backref('infector'), lazy='dynamic')
	infected_by = db.relationship('Infection', primaryjoin=(id==Infection.infected_id),
					backref=db.backref('infected'), lazy='dynamic')

	def __init__(self, name, max_energy=9, longevity=1, points=0):
		self.name = name
		self.max_energy = max_energy 
		self.longevity = longevity
		self.points = points

	def generate_json(self):
		return {'id':self.id,
				'name':self.name,
				'max_energy':self.max_energy,
				'longevity':self.longevity,
				'points':self.points,
				'rank':self.rank if self.rank else self.id,
				'infected_count':self.infected.count(),
				'infected_by_count':self.infected_by.count(),
				'appearance_id':self.appearance_id
		}





