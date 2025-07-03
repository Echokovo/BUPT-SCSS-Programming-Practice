from datetime import datetime, timedelta

from apscheduler.schedulers.background import BackgroundScheduler
from flask import Flask
from models.online import Online

class CheckUser:
    def check_inactive_user(self):
        with self.app.app_context():
            time_to_live = datetime.now() - timedelta(seconds=30)
            users = Online.delete_inactive_user(time_to_live)
        if len(users) > 0:
            self.app.logger.warning(f"{len(users)} inactive users deleted:{[user.user_id for user in users]}")

    def __init__(self, app: Flask):
        self.app = app
        self.scheduler = BackgroundScheduler()
        self.scheduler.add_job(self.check_inactive_user, 'interval', seconds=10)
        self.scheduler.start()