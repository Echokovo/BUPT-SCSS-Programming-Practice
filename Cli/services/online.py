from services.serverAPI import serverAPI
from apscheduler.schedulers.background import BackgroundScheduler

class Heartbeat:
    def __init__(self):
        self.scheduler = BackgroundScheduler()
        self.scheduler.add_job(serverAPI.heartbeat(), 'interval', seconds=5)
        self.scheduler.start()