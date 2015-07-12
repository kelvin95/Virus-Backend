from apscheduler.scheduler import Scheduler
from rq import Queue
from worker import conn
from app import db
from models import Virus
from sqlalchemy import func

q = Queue(connection=conn)
sched = Scheduler()

def update_rank(db):
	db.session.query(Virus).update({"rank":Virus.query.count()})
	viruses = db.session.query(Virus, func.count(Infection.id)).outerjoin(Infection.infector).\
				order_by(func.count(Infection.id)).all()
	rank = 1
	for virus in viruses:
		virus[0].rank = rank
		rank += 1
	db.session.commit()


@sched.interval_schedule(hours=24)
def timed_job():
	q.enqueue(update_rank, db)

sched.start()

while True:
    pass