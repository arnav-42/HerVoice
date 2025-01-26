from apscheduler.schedulers.background import BackgroundScheduler
from services import fetch_and_store_bills

def start_scheduler():
    scheduler = BackgroundScheduler()
    scheduler.add_job(fetch_and_store_bills, 'interval', minutes=1)
    scheduler.start()
