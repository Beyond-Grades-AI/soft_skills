from apscheduler.schedulers.background import BackgroundScheduler

from .LM import check_and_evaluate_answers


def start():
    scheduler = BackgroundScheduler()
    scheduler.add_job(check_and_evaluate_answers, 'interval', minutes=5, max_instances=2)
    scheduler.start()
