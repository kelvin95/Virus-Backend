from sqlalchemy import desc
from flask import Flask, request
from flask.ext.restful import Resource, reqparse
from time import time
from sqlalchemy import func

from app import app, api
from models import *

class VirusProfileAPI(Resource):
	def __init__(self):
		self.parser = reqparse.RequestParser()
		self.parser.add_argument('points_required', type=int)
		self.parser.add_argument('max_energy', type=int)
		self.parser.add_argument('longevity', type=int)

	def get(self, id):
		virus = Virus.query.filter_by(id=id).first()
		if not virus:
			return {'error':'virus not found!'}
		now = time()
		for infection in db.session.query(Infection).filter_by(infected_id=virus.id)\
						.order_by(Infection.infected_at).all():
			if (now - infection.infected_at) >= (infection.infector.longevity*3600):
				db.session.delete(infection)
			else:
				break
		for infection in db.session.query(Infection).filter_by(infector_id=virus.id)\
						.order_by(Infection.infected_at).all():
			if (now - infection.infected_at) >= (infection.infector.longevity*3600):
				db.session.delete(infection)
			else:
				break
		json = virus.generate_json()
		json['appearance'] = virus.appearance.generate_json() if virus.appearance else None
		return {'success':'virus retrieved', 'virus':json}

	def put(self, id):
		virus = Virus.query.filter_by(id=id).first()
		if not virus:
			return {'error':'virus not found!'}
		args = self.parser.parse_args()
		if not args['points_required'] or not args['max_energy'] or not args['longevity']:
			return {'error':'information is not complete!'}
		virus.points -= args['points_required'] 
		virus.max_energy = args['max_energy']
		virus.longevity = args['longevity']
		db.session.commit()
		return {'success':'virus successfully updated', 'virus':virus.generate_json()}


class NewVirusAPI(Resource):
	def post(self):
		json = request.get_json()
		try:
			name = json['name']
			del json['name']

			new_virus = Virus(name)
			virus_appearance = Virusappearance(**json)
			new_virus.appearance = virus_appearance
			db.session.add(new_virus)
			db.session.add(virus_appearance)
			db.session.commit()
			json = new_virus.generate_json()
			json['appearance'] = virus_appearance.generate_json()
			return {'success':'virus was successfully added', 'virus':json}

		except (ValueError, KeyError, TypeError), e:
			return {'error':'data supplied is not correct'}, 400

class VirusAppearanceAPI(Resource):
	def get(self, id):
		virus_appearance = Virusappearance.query.filter_by(id=id).first()
		if not virus_appearance:
			return {'error':'appearance not found!'}, 400
		return {'success':'virus appearance was successfully retrieved', 
				'virus_appearance':virus_appearance.generate_json()}

class InfectionAPI(Resource):
	def __init__(self):
		self.parser = reqparse.RequestParser()
		self.parser.add_argument('infector_id', type=int, required=True)
		self.parser.add_argument('infected_id', type=int, required=True)

	def post(self):
		args = self.parser.parse_args()
		infector = Virus.query.filter_by(id=args['infector_id']).first() 
		infected = Virus.query.filter_by(id=args['infected_id']).first()
		if not infector or not infected:
			return {'error':'virus not found'}, 400
		infection = Infection(infector, infected)
		db.session.add(infection)
		infector.points += 15

		for infects in infector.infected_by.all():
			i = Infection(infects, infected)
			infects.points += 5
			db.session.add(i)
		db.session.commit()
		return {'success':'virus has been successfully infected', 'virus':infector.generate_json()}

class HealAPI(Resource):
	def __init__(self):
		self.parser = reqparse.RequestParser()
		self.parser.add_argument('healer_id', type=int, required=True)
		self.parser.add_argument('healed_id', type=int, required=True)

	def post(self):
		args = self.parser.parse_args()
		healer = Virus.query.filter_by(id=args['healer_id']).first()
		healed = Virus.query.filter_by(id=args['healed_id']).first()
		healer.points += 15
		now = time()
		if not healer or not healed:
			return {'error':'virus not found'}, 400
		infections = db.session.query(Infection).filter_by(infected_id=healed.id)\
					.order_by(Infection.infected_at).all()
		for infection in infections:
			db.session.delete(infection)
			if not (now - infection.infected_at) >= (infection.infector.longevity*36000):
				break
		db.session.commit()
		return {'success':'virus successfully healed another', 'virus':healer.generate_json()}

class RankUpdateAPI(Resource):
	def get(self):
		count = Virus.query.count()
		db.session.query(Virus).update({"rank":count})
		db.session.commit()
		viruses = db.session.query(Virus, func.count(Infection.id)).outerjoin(Infection.infector).group_by(Virus).order_by(func.count(Infection.id)).all()
		rank = 1
		for virus in viruses:
			if virus[0] is None:
				break
			virus[0].rank = rank
			rank += 1
		db.session.commit()
		return {'success':'rank updated'}

api.add_resource(VirusProfileAPI, '/virus/<int:id>')
api.add_resource(NewVirusAPI, '/virus')
api.add_resource(InfectionAPI, '/infection')
api.add_resource(HealAPI, '/heal')
api.add_resource(VirusAppearanceAPI, '/virus/appearance/<int:id>')
api.add_resource(RankUpdateAPI, '/rank/update')




