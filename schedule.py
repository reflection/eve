import logging
from datetime import datetime

from apscheduler.triggers.cron import CronTrigger
from slack_sdk.errors import SlackApiError

from auth import get_slack_client, get_sqlite3_cursor
from feedback import setup_feedback
from personality import eveify


def sync_schedules(scheduler):
    cur = get_sqlite3_cursor()
    res = cur.execute("SELECT id, channel_id, message, schedule, tool FROM schedule")
    schedule_ids = [s.id for s in scheduler.get_schedules()]
    for schedule_id, channel_id, message, schedule, tool in res.fetchall():
        schedule_id = str(schedule_id)
        try:
            if schedule_id not in schedule_ids:
                scheduler.add_schedule(
                    post,
                    CronTrigger.from_crontab(schedule),
                    args=[channel_id, message, tool],
                    id=schedule_id,
                )
        except Exception as e:
            logging.error(f"Error scheduling id ({schedule_id}): {e}")


def post(channel_id, message, tool):
    try:
        if tool == "feedback":
            day = datetime.now().strftime("%Y-%m-%d")
            prompt = f"This is the first Slack message from Eve to ask users to reply in the thread to provide feedback. Feedback task: {message}"
            text = eveify(prompt)
        else:
            text = message

        client = get_slack_client()
        result = client.chat_postMessage(
            channel=channel_id,
            text=text,
        )
        logging.info(f"Message posted: {result}")
        if tool == "feedback":
            setup_feedback(result["ts"], day)
    except SlackApiError as e:
        logging.error(
            f"Error posting channel id ({channel_id}) message ({message}): {e}"
        )
