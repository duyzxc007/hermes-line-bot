from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from datetime import datetime
import pytz

import os

# We use SQLAlchemyJobStore with SQLite to persist jobs even if the server restarts!
DATA_DIR = os.environ.get("DATA_DIR", ".")
jobstores = {
    'default': SQLAlchemyJobStore(url=f'sqlite:///{os.path.join(DATA_DIR, "jobs.db")}')
}

bkk_tz = pytz.timezone('Asia/Bangkok')

scheduler = BackgroundScheduler(jobstores=jobstores, timezone=bkk_tz)

def add_reminder(time_str: str, message: str, user_id: str):
    """
    Schedules a message to be pushed to the user at a specific time.
    time_str: ISO format string 'YYYY-MM-DD HH:MM:SS'
    """
    from line_client import push_message_to_user
    
    # Parse the time string to a datetime object in Bangkok timezone
    run_date = datetime.strptime(time_str, '%Y-%m-%d %H:%M:%S')
    run_date = bkk_tz.localize(run_date)
    
    # Schedule the job
    job = scheduler.add_job(
        push_message_to_user,
        'date',
        run_date=run_date,
        args=[user_id, f"⏰ แจ้งเตือน: {message}"]
    )
    return job.id
